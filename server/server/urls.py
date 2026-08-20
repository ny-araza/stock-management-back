from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from polls import views
from polls.vente.views import ValiderVenteView

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

router.register(
    r'stock',
    views.StockViewSet,
    basename="stock"
    )

router.register(
    r'entree_stock',
    views.EntreeViewSet,
    basename="entree_stock"
    )

router.register(
    r'sortit_stock',
    views.SortitViewSet,
    basename="sortit_stock"
    )

router.register(
    r'in_stock',
    views.InStockViewSet,
    basename="in_stock"
    )

router.register(
    r'mvt_stock',
    views.MvtStockViewSet,
    basename="mvt_stock"
    )

router.register(
    r"mvt_stockkk",
    views.MvtStockViewSett,
    basename="mvt-stockk"
)

router.register(
    r"retours_fournisseur",
    views.RtfViewSet,
    basename="retours_fournisseur"
)

router.register(
    r"retours_client",
    views.RtcViewSet,
    basename="retours_client"
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
        "api/generate-date-code/",
        views.generate_date_code,
        name="generate-date-code"
    ),
    path(
        "api/generate-enumeration/",
        views.generate_enumeration,
        name="generate-enumeration"
    ),
    path(
        "api/insert-database/",
        views.dynamic_create_view,
        name="dynamic-create-client-fournis"
        ),
    path(
        "api/nombres/",
        views.NombreVenteAPIView.as_view(),
        name="nombre"),
    path(
        "api/articles-autocomplete/",
        views.ArticleAutoComplete.as_view(),
        name="articles-autocomplete"
    ),
    path(
        "api/cmf-fournis-autocomplete/",
        views.CFAutoComplete.as_view(),
        name="cmf-fournis-autocomplete"
    ),
    path(
        "api/bl-autocomplete/",
        views.BLAutoComplete.as_view(),
        name="bl-autocomplete"
    ),
    path(
        "api/fa-autocomplete/",
        views.FAAutoComplete.as_view(),
        name="fa-autocomplete"
    ),
    path("api/vente/valider/", ValiderVenteView.as_view(), name="valider-vente"),
]
