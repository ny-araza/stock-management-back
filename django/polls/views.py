# from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


def index(request):
    data = {
        "message": "Bonjour",
        "status": "ok",
        "items": [1, 2, 3]
    }
    return JsonResponse(data)
