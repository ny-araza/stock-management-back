from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from polls import views

router = DefaultRouter()

router.register(r'users', views.TUserViewset)
router.register(r'articles', views.ArticlesViewSet)
router.register(r'me', views.CurrentUserViewSet, basename='me')
router.register(r'clients', views.ClientViewSet, basename="clients")
router.register(r'ventes', views.VenteViewSet, basename="ventes")
router.register(r'bc-list', views.BcViewSet, basename="bc-list")
router.register(
    r'fournisseurs',
    views.FournisseurViewSet,
    basename="founrisseurs"
    )
router.register(
    r'familles',
    views.FamilleViewSet,
    basename="familles"
    )
router.register(
    r'sous-familles',
    views.SousFamilleViewSet,
    basename="sous-familles"
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', views.UserAuthViewSet.as_view(), name="user_login"),
    path('api/logout/', views.LogoutView.as_view(), name="logout"),
    path(
        "api/generate-reference/",
        views.generate_reference_view,
        name="generate-reference"
    ),
    path(
        "api/generate-enumeration/",
        views.generate_enumeration,
        name="generate-enumeration"
    ),
    path(
        "api/create-client-fournis/",
        views.dynamic_create_view,
        name="dynamic-create-client-fournis"
        ),
    path(
        "api/nombres/",
        views.NombreVenteAPIView.as_view(),
        name="nombre"),
]
