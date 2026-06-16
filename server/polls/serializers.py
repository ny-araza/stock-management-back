from .models import TUsers
from rest_framework import serializers


class TUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TUsers
        fields = "__all__"
