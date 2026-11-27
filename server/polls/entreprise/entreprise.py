from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from polls.models import TEntreprise
from polls.serializers import TEntrepriseSerializer


class TEntrepriseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TEntreprise.objects.all()
    serializer_class = TEntrepriseSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "entreprises": serializer.data,
                }
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "entreprises": [],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
