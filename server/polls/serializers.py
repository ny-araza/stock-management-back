from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import (
    TAcces,
    TArticle,
    TClient,
    TCmdFournis,
    TEntree,
    TEntreprise,
    TFamille,
    TFournis,
    TInStock,
    TLigneEntree,
    TLigneRtc,
    TLigneRtf,
    TLigneVente,
    TListMenu,
    TLot,
    TMvtStock,
    TOutStock,
    TPrix,
    TProforma,
    TRetourClient,
    TRetourFournis,
    TSousFamille,
    TStock,
    TUsers,
    TVente,
)


class TEntrepriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TEntreprise
        fields = "__all__"


class PermissionSerializer(serializers.Serializer):
    men_code = serializers.IntegerField()
    acces = serializers.BooleanField()


class UserAccessSerializer(serializers.Serializer):
    use_login = serializers.CharField(max_length=25)
    use_acc_code = serializers.CharField(max_length=25)
    use_enabled = serializers.BooleanField(default=True)
    password = serializers.CharField(
        write_only=True, required=False, allow_blank=True, trim_whitespace=False
    )
    permissions = PermissionSerializer(many=True, required=False)

    @property
    def instance_user(self):
        return self.context.get("instance")

    def validate_use_login(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Le login est requis.")
        qs = TUsers.objects.filter(use_login=value)
        if self.instance_user is not None:
            qs = qs.exclude(pk=self.instance_user.pk)
        if qs.exists():
            raise serializers.ValidationError("Ce login est déjà utilisé.")
        return value

    def validate_use_acc_code(self, value):
        value = value.strip()
        if not TAcces.objects.filter(acc_code=value).exists():
            raise serializers.ValidationError("Code d'accès inconnu.")
        return value

    def validate_permissions(self, value):
        codes = [p["men_code"] for p in value]
        if len(codes) != len(set(codes)):
            raise serializers.ValidationError("Menu en double dans les permissions.")
        existing = set(
            TListMenu.objects.filter(men_code__in=codes).values_list(
                "men_code", flat=True
            )
        )
        unknown = sorted(set(codes) - existing)
        if unknown:
            raise serializers.ValidationError(f"Menus inconnus : {unknown}")
        return value

    def validate(self, attrs):
        # Mot de passe obligatoire à la création, optionnel à la modification
        if self.instance_user is None and not attrs.get("password"):
            raise serializers.ValidationError(
                {"password": "Le mot de passe est requis."}
            )
        return attrs


class TUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TUsers
        fields = "__all__"


# AUth login
class LoginSerializer(serializers.Serializer):
    use_login = serializers.CharField(required=True)
    use_pwd = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get("use_login")
        password = data.get("use_pwd")
        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise serializers.ValidationError("Identifiants invalidés.")
        else:
            raise serializers.ValidationError("Tous les champs sont requis.")

        data["user"] = user
        return data


# Articles
class ArticlesSerializers(serializers.ModelSerializer):
    class Meta:
        model = TArticle
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    use_login = serializers.CharField(required=True)
    use_acc_code = serializers.CharField()
    use_enabled = serializers.BooleanField()

    class Meta:
        model = TUsers
        fields = ["user_id", "use_login", "use_acc_code", "use_enabled"]


class ClientsSerializers(serializers.ModelSerializer):
    class Meta:
        model = TClient
        fields = "__all__"


class VenteSerializers(serializers.ModelSerializer):
    class Meta:
        model = TVente
        fields = "__all__"


class BcSerializers(serializers.ModelSerializer):
    class Meta:
        model = TCmdFournis
        fields = "__all__"


class ProformaSerializers(serializers.ModelSerializer):
    class Meta:
        model = TProforma
        fields = "__all__"


class FournisseurSerializers(serializers.ModelSerializer):
    class Meta:
        model = TFournis
        fields = "__all__"


class FamilleSerializers(serializers.ModelSerializer):
    class Meta:
        model = TFamille
        fields = "__all__"


class SousFamilleSerializers(serializers.ModelSerializer):
    class Meta:
        model = TSousFamille
        fields = "__all__"


class StockSerializers(serializers.ModelSerializer):
    class Meta:
        model = TStock
        fields = "__all__"


class LigneEntreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TLigneEntree
        fields = "__all__"


class LigneRtfSerializer(serializers.ModelSerializer):
    class Meta:
        model = TLigneRtf
        fields = "__all__"


class LigneRtcSerializer(serializers.ModelSerializer):
    class Meta:
        model = TLigneRtc
        fields = "__all__"


class LigneVenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TLigneVente
        fields = "__all__"


class EntreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TEntree
        fields = "__all__"


class SortitSerializer(serializers.ModelSerializer):
    class Meta:
        model = TOutStock
        fields = "__all__"


class LotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TLot
        fields = "__all__"


class PrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = TPrix
        fields = "__all__"


class InStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TInStock
        fields = "__all__"


class MvtStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMvtStock
        fields = "__all__"


class RtfSerializer(serializers.ModelSerializer):
    class Meta:
        model = TRetourFournis
        fields = "__all__"


class RtcSerializer(serializers.ModelSerializer):
    class Meta:
        model = TRetourClient
        fields = "__all__"
