# from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import TUsers
from .serializers import TUsersSerializer


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
