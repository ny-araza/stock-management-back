from .models import TUsers
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
