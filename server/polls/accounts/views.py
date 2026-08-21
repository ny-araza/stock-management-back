import hashlib

from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.middleware.csrf import get_token
from django.utils import timezone
from polls.models import TAutorisation, TUsers
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def hash_password_sha256(raw_password: str) -> str:
    """Le mot de passe est stocké en SHA-256 brut, sans sel."""
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def serialize_user(user: TUsers) -> dict:
    return {
        "user_id": user.use_id,
        "use_login": user.use_login,
        "use_acc_code": user.use_acc_code,
        "use_enabled": bool(user.use_enabled),
    }


class CsrfView(APIView):
    """
    À appeler une fois au chargement de l'app (avant login) pour que
    Django dépose le cookie 'csrftoken' que le frontend devra renvoyer
    en header X-CSRFToken sur chaque requête POST/PUT/DELETE.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        use_login = (request.data.get("use_login") or "").strip()
        use_pwd = request.data.get("use_pwd") or ""
        print(use_login, use_pwd)
        if not use_login or not use_pwd:
            return Response(
                {"status": False, "message": "Identifiants requis"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = TUsers.objects.get(use_login=use_login)
        except TUsers.DoesNotExist:
            return Response(
                {"status": False, "message": "Identifiants incorrects"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.use_enabled:
            return Response(
                {"status": False, "message": "Compte désactivé"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if hash_password_sha256(use_pwd) != user.use_pwd:
            return Response(
                {"status": False, "message": "Identifiants incorrects"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Ouvre une session Django : dépose le cookie de session httpOnly.
        # backend explicite requis car on ne passe pas par authenticate().
        django_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        return Response({"status": True, "user": serialize_user(user)})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        django_logout(request)
        return Response({"status": True})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        autorisations = TAutorisation.objects.filter(aut_acc_code=user.use_acc_code)

        return Response(
            {
                "status": True,
                "user": serialize_user(user),
                "authorizations": [
                    {
                        "aut_acc_code": a.aut_acc_code,
                        "aut_men_code": a.aut_men_code,
                        "aut_acces": a.aut_acces,
                    }
                    for a in autorisations
                ],
            }
        )


class CreateUserView(APIView):
    permission_classes = [
        IsAuthenticated
    ]  # seul un utilisateur connecté peut créer un compte

    def post(self, request):
        use_login = (request.data.get("use_login") or "").strip()
        use_pwd = request.data.get("use_pwd") or ""
        use_acc_code = (request.data.get("use_acc_code") or "").strip()
        use_enabled = request.data.get("use_enabled", 1)

        if not use_login or not use_pwd:
            return Response(
                {"status": False, "message": "Login et mot de passe requis"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(use_pwd) < 4:
            return Response(
                {
                    "status": False,
                    "message": "Mot de passe trop court (4 caractères minimum)",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if TUsers.objects.filter(use_login=use_login).exists():
            return Response(
                {"status": False, "message": "Ce login existe déjà"},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            use_enabled = int(use_enabled)
        except (TypeError, ValueError):
            use_enabled = 1

        user = TUsers.objects.create(
            use_login=use_login,
            use_pwd=hash_password_sha256(use_pwd),  # jamais le mot de passe en clair
            use_acc_code=use_acc_code,
            use_enabled=use_enabled,
            use_datecre=timezone.now(),
            use_usercre=request.user.use_login,  # trace qui a créé le compte
        )

        return Response(
            {
                "status": True,
                "message": "Utilisateur créé",
                "user": serialize_user(user),
            },
            status=status.HTTP_201_CREATED,
        )
