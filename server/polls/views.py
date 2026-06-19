# from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import TUsers, TArticle
from .serializers import TUsersSerializer, LoginSerializer, ArticlesSerializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


class UserAuthViewSet(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)},
                            status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        response_data = {
            "status": True,
            "message": "Authentification réussi",
            "user": {
                "user_id": user.use_id,
                "use_login": user.use_login,
                "use_acc_code": user.use_acc_code,
                "use_enabled": user.use_enabled
            }
        }

        response = Response(response_data, status=status.HTTP_200_OK)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
        )

        return response


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


# Articles views
class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = TArticle.objects.all()
    serializer_class = ArticlesSerializers

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return Response({
                "status": True,
                "message": "ok",
                "articles": serializer.data,
            })

        except Exception as e:
            return Response({
                "status": False,
                "messages": e,
                "articles": []
            })
