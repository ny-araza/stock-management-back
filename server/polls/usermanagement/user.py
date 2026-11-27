from django.db import transaction
from django.utils import timezone
from polls.models import TAutorisation, TListMenu, TUsers
from polls.serializers import UserAccessSerializer
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# ---------- helpers ----------
def actor_login(request):
    return getattr(request.user, "use_login", None) or "system"


def serialize_user(user):
    return {
        "use_id": user.use_id,
        "use_login": user.use_login,
        "use_acc_code": user.use_acc_code,
        "use_enabled": bool(user.use_enabled),
    }


def read_permissions(acc_code):
    if not acc_code:
        return []
    rows = TAutorisation.objects.filter(aut_acc_code=acc_code)
    return [
        {"men_code": r.aut_men_code, "acces": bool(r.aut_acces)}
        for r in rows
        if r.aut_men_code is not None
    ]


def save_permissions(acc_code, permissions, actor):
    """Upsert une ligne t_autorisation par (profil, menu)."""
    now = timezone.now()
    for p in permissions:
        updated = TAutorisation.objects.filter(
            aut_acc_code=acc_code, aut_men_code=p["men_code"]
        ).update(aut_acces=int(p["acces"]), aut_usermdf=actor, aut_datemdf=now)
        if not updated:
            TAutorisation.objects.create(
                aut_acc_code=acc_code,
                aut_men_code=p["men_code"],
                aut_acces=int(p["acces"]),
                aut_usermdf=actor,
                aut_datemdf=now,
            )


def user_detail(user):
    return {**serialize_user(user), "permissions": read_permissions(user.use_acc_code)}


# ---------- views ----------
class MenusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        menus = (
            TListMenu.objects.exclude(men_enabled=0)
            .order_by("men_code")
            .values("men_code", "men_desc", "men_vbox")
        )
        return Response(list(menus))


class ProfileView(APIView):
    """Consultation et modification des autorisations d'un profil."""

    permission_classes = [IsAuthenticated]

    def get(self, request, acc_code):
        return Response(read_permissions(acc_code))

    @transaction.atomic
    def put(self, request, acc_code):
        permissions = request.data.get("permissions")

        if permissions is None:
            return Response(
                {"detail": "Le champ permissions est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        actor = actor_login(request)

        save_permissions(acc_code, permissions, actor)

        return Response(
            {
                "status": True,
                "message": "Autorisations enregistrées avec succès.",
                "permissions": read_permissions(acc_code),
            },
            status=status.HTTP_200_OK,
        )


class UsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = TUsers.objects.order_by("use_login")
        return Response([serialize_user(u) for u in users])

    @transaction.atomic
    def post(self, request):
        serializer = UserAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        actor = actor_login(request)
        now = timezone.now()

        user = TUsers(
            use_login=data["use_login"],
            use_acc_code=data["use_acc_code"],
            use_enabled=int(data["use_enabled"]),
            use_datecre=now,
            use_usercre=actor,
            use_datemdf=now,
            use_usermdf=actor,
        )
        user.set_password(data["password"])
        user.save()

        save_permissions(user.use_acc_code, data.get("permissions", []), actor)
        return Response(user_detail(user), status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return TUsers.objects.get(pk=pk)
        except TUsers.DoesNotExist:
            raise NotFound("Utilisateur introuvable.")

    def get(self, request, pk):
        return Response(user_detail(self.get_object(pk)))

    @transaction.atomic
    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserAccessSerializer(data=request.data, context={"instance": user})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        actor = actor_login(request)

        user.use_login = data["use_login"]
        user.use_acc_code = data["use_acc_code"]
        user.use_enabled = int(data["use_enabled"])
        user.use_datemdf = timezone.now()
        user.use_usermdf = actor
        if data.get("password"):
            user.set_password(data["password"])
        user.save()

        save_permissions(user.use_acc_code, data.get("permissions", []), actor)
        return Response(user_detail(user))
