from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import StockInsuffisantError, valider_vente


class ValiderVenteView(APIView):
    def post(self, request):
        try:
            vente = valider_vente(request.data)
            return Response(
                {
                    "status": True,
                    "message": "Vente enregistrée avec succès",
                    "code": vente.vte_code,
                },
                status=status.HTTP_201_CREATED,
            )
        except StockInsuffisantError as e:
            return Response(
                {
                    "status": False,
                    "error": str(e),
                    "art_code": e.art_code,
                    "disponible": e.disponible,
                    "demande": e.demande,
                },
                status=status.HTTP_409_CONFLICT,
            )
        except KeyError as e:
            return Response(
                {"status": False, "error": f"Champ manquant : {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"status": False, "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
