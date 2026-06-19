from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from polls import views

router = DefaultRouter()

router.register(r'users', views.TUserViewset)
router.register(r'articles', views.ArticlesViewSet)
router.register(r'me', views.CurrentUserViewSet, basename='me')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', views.UserAuthViewSet.as_view(), name="user_login"),
]
