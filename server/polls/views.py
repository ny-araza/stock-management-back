# from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import TUsers
from .serializers import TUsersSerializer, LoginSerializer


class UserAuthViewSet(APIView):
    permission_classes = [AllowAny]

    def post(sefl, request):
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        return Response({
            "status": True,
            "message": "Authentification réussi",
            "user": {
                "user_id": user.use_id,
                "use_login": user.use_login,
                "use_acc_code": user.use_acc_code,
                "use_enabled": user.use_enabled
            }
        }, status=status.HTTP_200_OK)


class TUserViewset(viewsets.ModelViewSet):
    queryset = TUsers.objects.all()
    serializer_class = TUsersSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return Response({
                "status": True,
                "message": "ok",
                "users": serializer.data,
            })

        except Exception as e:
            return Response({
                "status": False,
                "messages": e,
                "users": []
            })
