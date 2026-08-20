from datetime import date

from django.db import transaction
from django.db.models import Q

from ..models import (  # adapte l'import selon ton app
    TLigneVente,
    TLot,
    TMvtStock,
    TStock,
    TVente,
)

JOURS_MINIMUM_PEREMPTION = 7


class StockInsuffisantError(Exception):
    def __init__(self, art_code, disponible, demande):
        self.art_code = art_code
        self.disponible = disponible
        self.demande = demande
        super().__init__(
            f"Stock sortable insuffisant pour {art_code} : "
            f"disponible {disponible}, demandé {demande}"
        )


def est_sortable(
    date_peremption, jours_minimum: int = JOURS_MINIMUM_PEREMPTION
) -> bool:
    if not date_peremption:
        return False
    return (date_peremption - date.today()).days >= jours_minimum


def allouer_lots_fefo(art_code: str, quantite_demandee: int):
    """
    Verrouille les lignes t_stock de cet article (SELECT ... FOR UPDATE),
    récupère les dates de péremption via t_lot (jointure manuelle sur
    lot_code + art_code, car t_stock n'a pas de FK Django vers t_lot),
    puis alloue en FEFO en excluant les lots à moins de 7 jours de péremption.

    DOIT être appelé à l'intérieur d'un bloc transaction.atomic().
    Retourne une liste de dicts : [{stock_row, lot, quantite_prise}, ...]
    """
    # Verrouille toutes les lignes de stock de cet article ayant du stock.
    # Tant que la transaction n'est pas terminée, aucune autre vente
    # concurrente sur cet article ne peut lire/modifier ces lignes.
    stock_rows = list(
        TStock.objects.select_for_update()
        .filter(stk_art_code=art_code, stk_quantite__gt=0)
        .order_by("stk_id")
    )

    if not stock_rows:
        raise StockInsuffisantError(art_code, 0, quantite_demandee)

    lot_codes = {s.stk_lot_code for s in stock_rows if s.stk_lot_code}

    # On verrouille aussi les lots correspondants pour éviter qu'une
    # modification concurrente de la date de péremption (rare mais possible)
    # ne fausse le calcul pendant la transaction.
    lots = TLot.objects.select_for_update().filter(
        lot_art_code=art_code, lot_code__in=lot_codes
    )
    lot_par_code = {lot.lot_code: lot for lot in lots}

    # Associe chaque ligne de stock à son lot, ne garde que les sortables
    paires = []
    for stock_row in stock_rows:
        lot = lot_par_code.get(stock_row.stk_lot_code)
        if lot is None:
            continue  # ligne de stock orpheline sans lot correspondant, on ignore
        if est_sortable(lot.lot_dateper):
            paires.append((stock_row, lot))

    # FEFO : lot qui expire le plus tôt en premier
    paires.sort(key=lambda p: p[1].lot_dateper)

    stock_total = sum(s.stk_quantite for s, _ in paires)

    if quantite_demandee > stock_total:
        raise StockInsuffisantError(art_code, stock_total, quantite_demandee)

    allocations = []
    reste = quantite_demandee

    for stock_row, lot in paires:
        if reste <= 0:
            break
        qte_du_lot = min(stock_row.stk_quantite, reste)
        if qte_du_lot > 0:
            allocations.append(
                {"stock_row": stock_row, "lot": lot, "quantite_prise": qte_du_lot}
            )
            reste -= qte_du_lot

    return allocations


def generer_code_vente_atomique(prefixe: str = "FA") -> str:
    """
    Génère le prochain code de vente en verrouillant la dernière ligne
    correspondant au préfixe du jour, pour éviter les collisions entre
    deux ventes validées au même moment.
    Format observé : FA + YYMMDD + 4 chiffres (ex: FA26021087)
    """
    aujourdhui = date.today()
    prefixe_jour = f"{prefixe}{aujourdhui.strftime('%y%m%d')}"

    dernier = (
        TVente.objects.select_for_update()
        .filter(vte_code__startswith=prefixe_jour)
        .order_by("-vte_code")
        .first()
    )

    if dernier and dernier.vte_code:
        try:
            dernier_num = int(dernier.vte_code[len(prefixe_jour) :])
        except (ValueError, IndexError):
            dernier_num = 0
        nouveau_num = dernier_num + 1
    else:
        nouveau_num = 1

    return f"{prefixe_jour}{nouveau_num:04d}"


@transaction.atomic
def valider_vente(payload: dict) -> TVente:
    """
    Point d'entrée unique et atomique pour valider une commande client.
    Si une seule ligne échoue (stock insuffisant), tout est annulé
    automatiquement par transaction.atomic via l'exception levée.
    """
    lignes = payload.pop("lignes")

    code_vente = generer_code_vente_atomique("FA")
    today = date.today()

    vente = TVente.objects.create(
        vte_code=code_vente,
        vte_date=payload["date"],
        vte_modepaye=payload["mode_paye"],
        vte_cli_code=payload["code_cli"],
        vte_cli_nom=payload["client_nom"],
        vte_cli_contact=payload.get("contact1", ""),
        vte_payeclient=payload["paye_client"],
        vte_datepay=today,
        vte_telmoney=payload.get("tel_money", ""),
        vte_valide=0,
        vte_datevalide=today,
        vte_paye=0,
        vte_livreur=payload.get("livreur", ""),
        vet_operateur=payload.get("operateur", ""),
        vte_lettremontant=payload.get("lettre_montant", ""),
        ve_dateecheance=payload.get("date_echeance") or payload["date"],
        ve_code_bl=payload.get("bl", ""),
        ve_adresse_liv=payload.get("adresse", ""),
        ve_remise=payload.get("remise", 0),
        vte_montant_ht=payload["montant_ht"],
        vte_montant_ttc=payload["montant_ttc"],
        vte_tva=payload["tva"],
    )

    for ligne in lignes:
        art_code = ligne["art_code"]
        quantite_demandee = int(ligne["quantite"])

        allocations = allouer_lots_fefo(art_code, quantite_demandee)

        for alloc in allocations:
            stock_row = alloc["stock_row"]
            lot = alloc["lot"]
            qte_prise = alloc["quantite_prise"]

            proportion_ht = (qte_prise / quantite_demandee) * float(ligne["total_ht"])
            ttc_ligne = proportion_ht + (proportion_ht * float(ligne["tva"]) / 100)

            TLigneVente.objects.create(
                vtel_quantite=qte_prise,
                vtel_pri_id=ligne["pri_id"],
                vtel_vte_code=code_vente,
                vtel_prixunit=ligne["pua"],
                vtel_tva=ligne["tva"],
                vtel_ht=round(proportion_ht, 2),
                vtel_ttc=round(ttc_ligne, 2),
                vtel_art_code=art_code,
                vtel_cli_code=payload["code_cli"],
                vtel_lot_id=lot.lot_id,
                vtel_lot_code=lot.lot_code,
                vtel_lot_dateper=lot.lot_dateper,
                vtel_remise=ligne.get("remise", 0),
                vtel_valide=0,
            )

            TMvtStock.objects.create(
                mvt_action="delete",
                mvt_code_org=code_vente,
                mvt_date=today,
                mvt_lot_code=lot.lot_code,
                mvt_origine="t_vente",
                mvt_pri_id=ligne["pri_id"],
                mvt_qte=qte_prise,
                mvt_art_code=art_code,
            )

            # Décrémente directement la ligne verrouillée -> pas de race condition
            stock_row.stk_quantite -= qte_prise
            stock_row.save(update_fields=["stk_quantite"])

    return vente
