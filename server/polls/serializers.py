from .models import TUsers, TArticle, TClient, TVente, TCmdFournis
from rest_framework import serializers
from django.contrib.auth import authenticate


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
        fields = ['user_id', 'use_login', 'use_acc_code', 'use_enable']


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
