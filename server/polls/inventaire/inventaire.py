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
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from polls.models import TArticle, TLot  # adapter l'import si besoin

MAX_INT = 2_147_483_647  # lot_art_quantite est un IntegerField
DEFAULT_LIMIT = 20
MAX_LIMIT = 200
MAX_EXCLUDE_IDS = 5000

FIELDS = ("lotId", "lotCode", "lotArtCode", "lotArtQuantite", "nomArticle")


def _lots_valides():
    """Seuls les lots actifs (lot_enabled=1) ayant une date de péremption (lot_dateper) sont concernés par l'inventaire."""
    return TLot.objects.filter(lot_dateper__isnull=False)


def _base_queryset():
    """Lots + nom de l'article.

    TLot n'a pas de ForeignKey vers TArticle : le lien se fait par
    lot_art_code == art_code, via une sous-requête.
    """
    nom_article = Subquery(
        TArticle.objects.filter(art_code=OuterRef("lot_art_code")).values("art_nom")[:1]
    )
    return _lots_valides().annotate(
        lotId=F("lot_id"),
        lotCode=F("lot_code"),
        lotArtCode=F("lot_art_code"),
        lotArtQuantite=F("lot_art_quantite"),
        nomArticle=nom_article,
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
            for lot_id, qte in parsed.items():
                lot = lots[lot_id]
                if lot.lot_art_quantite != qte:  # ignore les lignes inchangées
                    lot.lot_art_quantite = qte
                    to_update.append(lot)

            if to_update:
                # uniquement la quantité : aucun autre champ du lot n'est touché
                TLot.objects.bulk_update(to_update, ["lot_art_quantite"])

        return Response({"updated": len(to_update)}, status=status.HTTP_200_OK)
