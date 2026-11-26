# inventaire_views.py
# Backend DRF pour la page d'inventaire physique (TLot / TArticle), avec pagination.
#
# URLs à ajouter dans urls.py :
#   path("inventaire/lots/", InventaireLotsView.as_view(), name="inventaire-lots"),
#   path("inventaire/lots/export/", InventaireLotsExportView.as_view(), name="inventaire-lots-export"),
#   path("inventaire/enregistrer/", InventaireEnregistrerView.as_view(), name="inventaire-enregistrer"),
#
# GET /inventaire/lots/?limit=20&offset=0&search=...&exclude_ids=1,2,3
#   -> {"count": <lots correspondant à la recherche>, "total": <tous les lots>, "results": [...]}

from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import F, OuterRef, Q, Subquery
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from polls.models import (  # adapter l'import si besoin
    TArticle,
    TInventaire,
    TLigneInventaire,
    TLot,
    TPrix,
)
from polls.utils import (
    generate_code_date,  # adapter : module où se trouve generate_code_date
)

INV_ETAT_TERMINE = "Terminé"  # valeur de inv_etat pour tout inventaire enregistré
INV_TABLE_NAME = "t_inventaire"  # nom de table attendu par generate_code_date / get_table_prefix (à adapter)
INVL_ETAT = 1  # valeur de invl_etat pour chaque ligne enregistrée (à adapter selon ta convention)
MAX_INT = 2_147_483_647  # lot_art_quantite est un IntegerField
DEFAULT_LIMIT = 20
MAX_LIMIT = 200
MAX_EXCLUDE_IDS = 5000

FIELDS = ("lotId", "lotCode", "lotArtCode", "lotArtQuantite", "nomArticle", "prixAchat")


def _lots_valides():
    """Seuls les lots actifs (lot_enabled=1) ayant une date de péremption (lot_dateper) sont concernés par l'inventaire."""
    return TLot.objects.filter(lot_enabled=1, lot_dateper__isnull=False)


def _base_queryset():
    """Lots + nom de l'article.

    TLot n'a pas de ForeignKey vers TArticle : le lien se fait par
    lot_art_code == art_code, via une sous-requête.
    """
    nom_article = Subquery(
        TArticle.objects.filter(art_code=OuterRef("lot_art_code")).values("art_nom")[:1]
    )
    # Prix d'achat courant de l'article : lien par pri_art_code == lot_art_code.
    # Si plusieurs lignes de prix existent, on prend la ligne active (pri_enabled=1)
    # la plus récente (pri_datedeb puis pri_id).
    prix_achat = Subquery(
        TPrix.objects.filter(pri_art_code=OuterRef("lot_art_code"), pri_enabled=1)
        .order_by(F("pri_datedeb").desc(nulls_last=True), "-pri_id")
        .values("pri_achat")[:1]
    )
    return _lots_valides().annotate(
        lotId=F("lot_id"),
        lotCode=F("lot_dateper"),
        lotArtCode=F("lot_art_code"),
        lotArtQuantite=F("lot_art_quantite"),
        nomArticle=nom_article,
        prixAchat=prix_achat,
    )


def _ordered(qs):
    # lot_id en dernier critère : garantit un ordre stable, indispensable à la pagination
    return qs.order_by("nomArticle", "lot_code", "lot_id")


def _serialize(qs):
    return [
        {
            "lotId": r["lotId"],
            "lotCode": r["lotCode"] or "",
            "lotArtCode": r["lotArtCode"] or "",
            "lotArtQuantite": r["lotArtQuantite"],
            "nomArticle": r["nomArticle"] or "(article inconnu)",
            # None si aucun prix d'achat actif : le lot n'est alors pas valorisé dans les totaux
            "prixAchat": float(r["prixAchat"]) if r["prixAchat"] is not None else None,
        }
        for r in qs.values(*FIELDS)
    ]


def _int_param(params, name, default, minimum, maximum=None):
    try:
        value = int(params.get(name, default))
    except (TypeError, ValueError):
        return default
    value = max(value, minimum)
    return min(value, maximum) if maximum is not None else value


def _parse_ids(raw):
    ids = []
    for part in (raw or "").split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
        if len(ids) >= MAX_EXCLUDE_IDS:
            break
    return ids


def _creer_inventaire(user, lignes):
    """Crée l'inventaire (t_inventaire) et ses lignes (t_ligne_inventaire).

    lignes : liste de {"lot": TLot, "qte_theo": int, "qte_phys": int}.
    À appeler dans la transaction qui met à jour les lots : si l'une des étapes échoue
    (code, inventaire ou lignes), tout est annulé, lots compris.
    """
    now = timezone.now()
    today = timezone.localdate()
    username = (user.get_username() or "")[
        :25
    ]  # colonnes *_usercre / *_usermdf : max 25 caractères

    # Code d'inventaire généré par la fonction du projet (isInsert=True : réserve le numéro suivant)
    code = generate_code_date(INV_TABLE_NAME, True)

    inventaire = TInventaire.objects.create(
        inv_code=code,
        inv_datecre=now,
        inv_datemdf=now,
        inv_usercre=username,
        inv_usermdf=username,
        inv_nbligne=len(lignes),
        inv_date=today,
        inv_etat=INV_ETAT_TERMINE,
        inv_nbecart=sum(1 for l in lignes if l["qte_phys"] != l["qte_theo"]),
        inv_nbverifie=len(lignes),
        inv_nbart=len({l["lot"].lot_art_code for l in lignes}),
    )

    TLigneInventaire.objects.bulk_create(
        [
            TLigneInventaire(
                invl_datecre=now,
                invl_usercre=username,
                invl_datemdf=now,
                invl_usermdf=username,
                invl_qtetheo=l["qte_theo"],
                invl_art_code=l["lot"].lot_art_code,
                invl_lot_code=(l["lot"].lot_code or "")[
                    :25
                ],  # invl_lot_Code : max 25 caractères
                invl_lot_id=l["lot"].lot_id,
                invl_qtephys=l["qte_phys"],
                invl_ecart=l["qte_phys"] - l["qte_theo"],
                invl_inv_code=code,
                invl_etat=INVL_ETAT,
            )
            for l in lignes
        ]
    )
    return inventaire


class InventaireLotsView(APIView):
    """GET paginé : lots avec nom d'article, recherche et exclusion côté serveur (lecture seule)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        params = request.query_params
        limit = _int_param(params, "limit", DEFAULT_LIMIT, 1, MAX_LIMIT)
        offset = _int_param(params, "offset", 0, 0)

        qs = _base_queryset()
        total = (
            _lots_valides().count()
        )  # même périmètre que la liste, pour des statistiques cohérentes

        search = (params.get("search") or "").strip()
        if search:
            qs = qs.filter(
                Q(nomArticle__icontains=search)
                | Q(lot_art_code__icontains=search)
                | Q(lot_code__icontains=search)
            )

        # Filtre « non modifiés » : le front envoie les lots déjà présents dans sa liste
        exclude_ids = _parse_ids(params.get("exclude_ids"))
        if exclude_ids:
            qs = qs.exclude(lot_id__in=exclude_ids)

        count = qs.count()
        page = _ordered(qs)[offset : offset + limit]

        return Response({"count": count, "total": total, "results": _serialize(page)})


class InventaireLotsExportView(APIView):
    """GET non paginé : tous les lots, utilisé uniquement pour la fiche de comptage."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_serialize(_ordered(_base_queryset())))


class InventaireEnregistrerView(APIView):
    """POST {"modifications": [{"lotId": 1, "nouvelleQuantite": 95}, ...]}

    Met à jour uniquement lot_art_quantite, en transaction atomique :
    si une ligne est invalide ou introuvable, rien n'est enregistré.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        items = request.data.get("modifications")
        if not isinstance(items, list) or not items:
            return Response(
                {"detail": "La liste des modifications est vide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        parsed, errors = {}, []
        for i, item in enumerate(items):
            try:
                lot_id = int(item["lotId"])
                qte = Decimal(str(item["nouvelleQuantite"]))
            except (KeyError, TypeError, ValueError, InvalidOperation):
                errors.append(f"Ligne {i + 1} : données invalides.")
                continue

            if not qte.is_finite() or qte < 0 or qte > MAX_INT:
                errors.append(
                    f"Lot {lot_id} : quantité invalide (entier >= 0 attendu)."
                )
            elif qte != qte.to_integral_value():
                errors.append(f"Lot {lot_id} : la quantité doit être un entier.")
            elif lot_id in parsed:
                errors.append(f"Lot {lot_id} : présent plusieurs fois.")
            else:
                parsed[lot_id] = int(qte)

        if errors:
            return Response(
                {"detail": " ".join(errors)}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            lots = {
                l.pk: l for l in TLot.objects.select_for_update().filter(pk__in=parsed)
            }

            missing = sorted(set(parsed) - set(lots))
            if missing:
                return Response(
                    {"detail": f"Lot(s) introuvable(s) : {missing}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            to_update = []
            lignes = []  # une ligne d'inventaire par lot contrôlé, modifié ou non
            for lot_id, qte in parsed.items():
                lot = lots[lot_id]
                ancienne = lot.lot_art_quantite
                lignes.append({"lot": lot, "qte_theo": ancienne, "qte_phys": qte})
                if (
                    ancienne != qte
                ):  # seules les quantités réellement différentes sont réécrites
                    lot.lot_art_quantite = qte
                    to_update.append(lot)

            if to_update:
                # uniquement la quantité : aucun autre champ du lot n'est touché
                TLot.objects.bulk_update(to_update, ["lot_art_quantite"])

            # Après la mise à jour des lots, et dans la même transaction : inventaire + lignes
            inventaire = _creer_inventaire(request.user, lignes)

        return Response(
            {
                "updated": len(to_update),
                "inventaire": {"id": inventaire.inv_id, "code": inventaire.inv_code},
            },
            status=status.HTTP_200_OK,
        )


class InventaireListeView(APIView):
    """GET paginé : historique des inventaires (t_inventaire), du plus récent au plus ancien.

    ?limit=20&offset=0&search=...  (recherche sur le code ou sur l'utilisateur)
    -> {"count": n, "results": [...]}
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        params = request.query_params
        limit = _int_param(params, "limit", DEFAULT_LIMIT, 1, MAX_LIMIT)
        offset = _int_param(params, "offset", 0, 0)

        qs = TInventaire.objects.all()
        search = (params.get("search") or "").strip()
        if search:
            qs = qs.filter(
                Q(inv_code__icontains=search) | Q(inv_usercre__icontains=search)
            )

        count = qs.count()
        page = qs.order_by("-inv_date", "-inv_id")[offset : offset + limit]

        results = [
            {
                "invId": i.inv_id,
                "invCode": i.inv_code or "",
                "invDate": i.inv_date,
                "invDatecre": i.inv_datecre,
                "invUsercre": i.inv_usercre or "",
                "invEtat": i.inv_etat or "",
                "invNbligne": i.inv_nbligne,
                "invNbecart": i.inv_nbecart,
                "invNbverifie": i.inv_nbverifie,
                "invNbart": i.inv_nbart,
            }
            for i in page
        ]
        return Response({"count": count, "results": results})


class InventaireLignesView(APIView):
    """GET : toutes les lignes (t_ligne_inventaire) d'un inventaire.

    Lien : invl_inv_code == inv_code. Le nom de l'article est récupéré par invl_art_code == art_code.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        nom_article = Subquery(
            TArticle.objects.filter(art_code=OuterRef("invl_art_code")).values(
                "art_nom"
            )[:1]
        )
        lignes = (
            TLigneInventaire.objects.filter(invl_inv_code=code)
            .annotate(nomArticle=nom_article)
            .order_by("nomArticle", "invl_lot_code", "invl_id")
        )
        return Response(
            [
                {
                    "invlId": l.invl_id,
                    "lotId": l.invl_lot_id,
                    "lotCode": l.invl_lot_code or "",
                    "artCode": l.invl_art_code or "",
                    "nomArticle": l.nomArticle or "(article inconnu)",
                    "qteTheo": l.invl_qtetheo,
                    "qtePhys": l.invl_qtephys,
                    "ecart": l.invl_ecart,
                    "etat": l.invl_etat,
                    "dateCre": l.invl_datecre,
                    "userCre": l.invl_usercre or "",
                }
                for l in lignes
            ]
        )
