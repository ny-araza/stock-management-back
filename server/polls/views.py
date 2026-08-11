# from django.shortcuts import render
from django.conf import settings
from django.db.models import OuterRef, Q, Subquery
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import CookieJWTAuthentification
from .filters import (
    ArticleFilter,
    BcFilter,
    ClientFilter,
    EntreeFilter,
    FournisseurFilter,
    InStockFilter,
    MvtStockFilter,
    MvtStockFilterr,
    RtcFilter,
    RtfFilter,
    SortitFilter,
    VenteFilter,
)
from .models import (
    TArticle,
    TClient,
    TCmdFournis,
    TEntree,
    TFamille,
    TFournis,
    TInStock,
    TLigneEntree,
    TLigneRtc,
    TLigneRtf,
    TLigneVente,
    TLot,
    TMvtStock,
    TOutStock,
    TPrix,
    TRetourClient,
    TRetourFournis,
    TSousFamille,
    TStock,
    TUsers,
    TVente,
)
from .pagination import ListPagination
from .serializers import (
    ArticlesSerializers,
    BcSerializers,
    ClientsSerializers,
    EntreeSerializer,
    FamilleSerializers,
    FournisseurSerializers,
    InStockSerializer,
    LigneEntreeSerializer,
    LigneRtcSerializer,
    LigneRtfSerializer,
    LigneVenteSerializer,
    LoginSerializer,
    LotSerializer,
    MvtStockSerializer,
    PrixSerializer,
    RtcSerializer,
    RtfSerializer,
    SortitSerializer,
    SousFamilleSerializers,
    StockSerializers,
    TUsersSerializer,
    VenteSerializers,
)
from .services.dynamic_service import create_dynamic_instance
from .utils import generate_code_date, generate_enumeration_value, generate_reference


class UserAuthViewSet(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        response_data = {
            "status": True,
            "message": "Authentification réussi",
            "user": {
                "user_id": user.use_id,
                "use_login": user.use_login,
                "use_acc_code": user.use_acc_code,
                "use_enabled": user.use_enabled,
            },
        }

        response = Response(response_data, status=status.HTTP_200_OK)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
        )

        return response


class TUserViewset(viewsets.ModelViewSet):
    queryset = TUsers.objects.all()
    serializer_class = TUsersSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "users": serializer.data,
                }
            )

        except Exception as e:
            return Response({"status": False, "messages": e, "users": []})


# Articles views
class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = TArticle.objects.all()
    serializer_class = ArticlesSerializers
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = ArticleFilter

    def list(self, request, *args, **kwargs):
        try:
            # queryset = self.get_queryset()
            queryset = self.filter_queryset(self.get_queryset())
            queryset = queryset.order_by("art_nom")
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "articles": serializer.data,
                    }
                )
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {"status": False, "messages": "ok", "articles": serializer.data}
            )
        except Exception as e:
            return Response({"status": False, "messages": e, "articles": []})


class CurrentUserViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]

    def list(self, request):
        """
        Cette méthode intercepte le GET sur /api/me/
        Grâce à l'authentification JWT, request.user
        contient l'utilisateur connecté.
        """
        try:
            user = request.user
            return Response(
                {
                    "status": True,
                    "user": {
                        "user_id": user.use_id,
                        "use_login": user.use_login,
                        "use_acc_code": user.use_acc_code,
                        "use_enabled": user.use_enabled,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": f"Impossible de récupérer l'utilisateur : {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# view client
class ClientViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]
    queryset = TClient.objects.all()
    serializer_class = ClientsSerializers
    pagination_class = ListPagination

    # Activation des filtres et du tri
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = ClientFilter

    def list(self, request, *args, **kwargs):
        try:
            # queryset = self.get_queryset()
            queryset = self.filter_queryset(self.get_queryset())
            search = request.query_params.get("search", "").strip()

            if search:
                for word in search.split():
                    queryset = queryset.filter(
                        Q(cli_code__icontains=search)
                        | Q(cli_nom__icontains=search)
                        | Q(cli_email__icontains=search)
                        | Q(cli_tel1__icontains=search)
                        | Q(cli_tel2__icontains=search)
                        | Q(cli_adresse__icontains=search)
                        | Q(cli_nif__icontains=search)
                        | Q(cli_stat__icontains=search)
                        | Q(cli_rcs__icontains=search)
                        | Q(cli_type__icontains=search)
                        | Q(cli_modepay__icontains=search)
                    )
            queryset = queryset.order_by("cli_nom")
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "clients": serializer.data,
                    }
                )

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "clients": serializer.data,
                }
            )
        except Exception as e:
            return Response({"status": False, "message": e, "clients": []})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(cli_datecre=timezone.now(), cli_enabled=1)

            return Response(
                {
                    "status": True,
                    "message": "Client créé avec succès",
                    "client": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": False,
                "message": "Erreur de validation",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# view vente  list
class VenteViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]
    queryset = TVente.objects.all()
    serializer_class = VenteSerializers
    pagination_class = ListPagination
    # Activation des filtres et du tri
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = VenteFilter

    def list(self, request, *args, **kwargs):
        try:
            # queryset = self.get_queryset()
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            objets = page if page is not None else queryset
            serializer = self.get_serializer(objets, many=True)
            data = serializer.data

            # Récupération des lignes pour chaque entrée
            for vente in data:
                lignes = TLigneVente.objects.filter(vtel_vte_code=vente["vte_code"])

                vente["lignes"] = LigneVenteSerializer(lignes, many=True).data

            if page is not None:
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "ventes": data,
                    }
                )
            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "ventes": data,
                }
            )
        except Exception as e:
            return Response({"status": False, "message": str(e), "ventes": []})


# liste BC
class BcViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]
    queryset = TCmdFournis.objects.all()
    serializer_class = BcSerializers
    pagination_class = ListPagination
    # Activation des filtres et du tri
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = BcFilter

    def list(self, request, *args, **kwargs):
        try:
            # queryset = self.get_queryset()
            queryset = self.filter_queryset(self.get_queryset())
            search = request.query_params.get("search", "").strip()

            if search:
                for word in search.split():
                    queryset = queryset.filter(Q(cmf_code__icontains=search))
            queryset = queryset.order_by("cmf_code")
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "bc_list": serializer.data,
                    }
                )

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "bc_list": serializer.data,
                }
            )
        except Exception as e:
            return Response({"status": False, "message": str(e), "bc_list": []})


# liste BC
class FournisseurViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]
    queryset = TFournis.objects.all()
    serializer_class = FournisseurSerializers
    pagination_class = ListPagination
    # Activation des filtres et du tri
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = FournisseurFilter

    def list(self, request, *args, **kwargs):
        try:
            # queryset = self.get_queryset()
            queryset = self.filter_queryset(self.get_queryset())
            search = request.query_params.get("search", "").strip()

            if search:
                for word in search.split():
                    queryset = queryset.filter(
                        Q(fou_code__icontains=search) | Q(fou_nom__icontains=search)
                    )
            queryset = queryset.order_by("fou_code")
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "fournisseur": serializer.data,
                    }
                )

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "fournisseur": serializer.data,
                }
            )
        except Exception as e:
            return Response({"status": False, "message": str(e), "fournisseur": []})


class FamilleViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]
    queryset = TFamille.objects.all()
    serializer_class = FamilleSerializers

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "famille": serializer.data,
                }
            )
        except Exception as e:
            return Response({"status": False, "message": str(e), "famille": []})


class SousFamilleViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]
    queryset = TSousFamille.objects.all()
    serializer_class = SousFamilleSerializers

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            search = request.query_params.get("search", "").strip()

            if search:
                for word in search.split():
                    queryset = queryset.filter(Q(sof_fam_id__icontains=search))
            queryset = queryset.order_by("sof_nom")
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "sous_famille": serializer.data,
                }
            )
        except Exception as e:
            return Response({"status": False, "message": str(e), "sous_famille": []})


# logOut
class LogoutView(APIView):
    def post(self, request):
        try:
            response = Response({"status": True, "message": "Deconexion reussie"})

            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response
        except Exception as e:
            return response({"status": False, "message": e})


# get last client code
@api_view(["GET"])
def generate_reference_view(request):
    table_name = request.GET.get("table_name")
    pk_field = request.GET.get("pk_field")

    if not table_name or not pk_field:
        return Response(
            {"error": "Les parametres 'table_name'et 'pk_field' sont obligé"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        reference = generate_reference(table_name, pk_field)
        return Response({"reference": reference}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def generate_enumeration(request):
    enu_code = request.GET.get("enu_code")
    if not enu_code:
        return Response(
            {
                "success": False,
                "error": "enu_code ne doit pas etre vide",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    result = generate_enumeration_value(enu_code)
    return Response(
        {"success": True, "nom_enumeration": result}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
def dynamic_create_view(request):
    try:
        table_name = request.data.get("table")
        data = request.data.get("data")
        print("===> data ", data)
        # get the 3 first word in table
        prefix = ""
        try:
            if table_name == "t_sous_famille":
                prefix = "sof"
            elif table_name == "t_in_stock":
                prefix = "in"
            elif table_name == "t_out_stock":
                prefix = "out"
            elif table_name == "t_cmd_fournis":
                prefix = "cmf"
            elif table_name == "t_ligne_cmd_fournis":
                prefix = "cmfl"
            elif table_name == "t_ligne_entree":
                prefix = "entl"
            elif table_name == "t_stock":
                prefix = "stk"
            elif table_name == "t_vente":
                prefix = "vte"
            elif table_name == "t_ligne_vente":
                prefix = "vtel"
            else:
                for i in range(2, 5):
                    prefix += table_name[i]
        except Exception:
            raise Exception("Table name no conforme with norm")

        if not table_name or not data or not prefix:
            return Response(
                {"status": False, "error": "table et data sont obligatoires"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data.update(
            {
                f"{prefix}_datecre": timezone.now(),
                f"{prefix}_usercre": request.user.use_login,
            }
        )
        instance = create_dynamic_instance(table_name, data)

        return Response(
            {"status": True, "message": "Créé avec succès", "id": instance.pk},
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"status": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )


class NombreVenteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            result = {}
            nombre_ventes = TVente.objects.count()
            nombre_cmd = TCmdFournis.objects.count()
            nombre_frns = TFournis.objects.count()
            nombre_clts = TClient.objects.count()
            result.update(
                {
                    "nombre_ventes": nombre_ventes,
                    "nombre_cmd": nombre_cmd,
                    "nombre_frns": nombre_frns,
                    "nombre_clts": nombre_clts,
                }
            )
            return Response(
                {
                    "nombre": result,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def generate_date_code(request):
    table_name = request.GET.get("table_name")
    is_insert = request.GET.get("is_insert")

    if is_insert == "0":
        is_insert = False
    else:
        is_insert = True

    if not table_name:
        return Response(
            {
                "success": False,
                "error": "table_name ne doit pas etre vide",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    result = generate_code_date(table_name, is_insert)
    return Response({"success": True, "code": result}, status=status.HTTP_200_OK)


class ArticleAutoComplete(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            search = request.GET.get("search", "")
            print(search)
            articles = TPrix.objects.filter(pri_art_code__icontains=search).values(
                "pri_id", "pri_art_code", "pri_achat"
            )

            if not articles:
                raise Exception("Pas d'article code correspondant")

            nom_articles = (
                TArticle.objects.filter(art_code__icontains=articles[0]["pri_art_code"])
                .values("art_nom")
                .first()
            )
            article_name = ""
            if nom_articles:
                article_name = nom_articles["art_nom"]
            return Response(
                {
                    "status": True,
                    "articles": [
                        {
                            "id": a["pri_id"],
                            "code": a["pri_art_code"],
                            "prix_ht": a["pri_achat"],
                            "nom_article": article_name,
                        }
                        for a in articles
                    ],
                }
            )
        except Exception as e:
            return Response({"status": False, "message": str(e), "articles": []})


class StockViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]
    queryset = TStock.objects.all()
    serializer_class = StockSerializers
    pagination_class = ListPagination

    @action(detail=False, methods=["get"], url_path="article/(?P<art_code>[^/.]+)")
    def stock_article(self, request, art_code=None):
        try:
            stock = (
                TStock.objects.filter(stk_art_code=art_code).order_by("-stk_id").first()
            )

            if not stock:
                return Response(
                    {
                        "status": False,
                        "message": f"Aucun stock trouvé pour l'article {art_code}.",
                        "stock": None,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = self.get_serializer(stock)

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "stock": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "stock": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            search = request.query_params.get("search", "").strip()

            # Recherche
            if search:
                for word in search.split():
                    queryset = queryset.filter(Q(stk_art_code__icontains=word))

            # Récupérer le dernier stk_id pour chaque article
            derniere_ligne = (
                TStock.objects.filter(stk_art_code=OuterRef("stk_art_code"))
                .order_by("-stk_id")
                .values("stk_id")[:1]
            )

            # Garder uniquement la dernière ligne de chaque stk_art_code
            queryset = queryset.filter(stk_id=Subquery(derniere_ligne))

            # Pagination
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)

                data = serializer.data

                for stock in data:
                    article = TArticle.objects.filter(
                        art_code=stock["stk_art_code"]
                    ).first()

                    stock["article_table"] = (
                        ArticlesSerializers(article).data if article else None
                    )

                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "stock": data,
                    }
                )

            serializer = self.get_serializer(queryset, many=True)

            data = serializer.data

            for stock in data:
                article = TArticle.objects.filter(
                    art_code=stock["stk_art_code"]
                ).first()

                stock["article_table"] = (
                    ArticlesSerializers(article).data if article else None
                )

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "stock": data,
                }
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "stock": [],
                }
            )


class EntreeViewSet(viewsets.ModelViewSet):
    queryset = TEntree.objects.all()
    serializer_class = EntreeSerializer
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = EntreeFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by("ent_id")
            page = self.paginate_queryset(queryset)

            objets = page if page is not None else queryset
            serializer = self.get_serializer(objets, many=True)
            data = serializer.data

            # Récupération des lignes pour chaque entrée
            for entree in data:
                lignes = TLigneEntree.objects.filter(entl_ent_code=entree["ent_code"])

                entree["lignes"] = LigneEntreeSerializer(lignes, many=True).data

            if page is not None:
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "entree": data,
                    }
                )

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "entree": data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "entree": [],
                }
            )


class SortitViewSet(viewsets.ModelViewSet):
    queryset = TOutStock.objects.all()
    serializer_class = SortitSerializer
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = SortitFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by("out_id")
            page = self.paginate_queryset(queryset)

            objets = page if page is not None else queryset
            serializer = self.get_serializer(objets, many=True)
            data = serializer.data

            for sortie in data:
                lignes = TLot.objects.filter(lot_id=sortie["out_lot_id"])

                sortie["lot"] = LotSerializer(lignes, many=True).data

            if page is not None:
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "sortie": data,
                    }
                )

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "sortie": data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "sortie": [],
                }
            )


class InStockViewSet(viewsets.ModelViewSet):
    queryset = TInStock.objects.all()
    serializer_class = InStockSerializer
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = InStockFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by("in_id")
            page = self.paginate_queryset(queryset)

            objets = page if page is not None else queryset
            serializer = self.get_serializer(objets, many=True)
            data = serializer.data

            for sortie in data:
                lignes = TLot.objects.filter(lot_id=sortie["in_lot_id"])

                sortie["lot"] = LotSerializer(lignes, many=True).data

            if page is not None:
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "entree": data,
                    }
                )

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "entree": data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "entree": [],
                }
            )


class MvtStockViewSet(viewsets.ModelViewSet):
    queryset = TMvtStock.objects.all()
    serializer_class = MvtStockSerializer
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = MvtStockFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by("mvt_id")
            page = self.paginate_queryset(queryset)

            objets = page if page is not None else queryset
            serializer = self.get_serializer(objets, many=True)
            data = serializer.data

            if page is not None:
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "mvt": data,
                    }
                )

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "mvt": data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "mvt": [],
                }
            )


class MvtStockViewSett(viewsets.ModelViewSet):
    queryset = TMvtStock.objects.all().order_by("-mvt_id")

    serializer_class = MvtStockSerializer

    pagination_class = ListPagination

    permission_classes = [IsAuthenticated]

    authentication_classes = [CookieJWTAuthentification]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = MvtStockFilterr

    ordering_fields = [
        "mvt_id",
        "mvt_qte",
        "mvt_date",
        "mvt_datecre",
        "mvt_datemdf",
    ]

    ordering = ["-mvt_id"]


class RtfViewSet(viewsets.ModelViewSet):
    queryset = TRetourFournis.objects.all()
    serializer_class = RtfSerializer
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = RtfFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by("rtf_id")
            page = self.paginate_queryset(queryset)

            objets = page if page is not None else queryset
            serializer = self.get_serializer(objets, many=True)
            data = serializer.data

            # Récupération des lignes pour chaque entrée
            for entree in data:
                lignes = TLigneRtf.objects.filter(rtfl_rtf_code=entree["rtf_code"])

                entree["lignes"] = LigneRtfSerializer(lignes, many=True).data

            if page is not None:
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "retour_fournisseur": data,
                    }
                )

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "retour_fournisseur": data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "retour_fournisseur": [],
                }
            )


class RtcViewSet(viewsets.ModelViewSet):
    queryset = TRetourClient.objects.all()
    serializer_class = RtcSerializer
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = RtcFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by("rtc_id")
            page = self.paginate_queryset(queryset)

            objets = page if page is not None else queryset
            serializer = self.get_serializer(objets, many=True)
            data = serializer.data

            # Récupération des lignes pour chaque entrée
            for entree in data:
                lignes = TLigneRtc.objects.filter(rtcl_rtc_code=entree["rtc_code"])

                entree["lignes"] = LigneRtcSerializer(lignes, many=True).data

            if page is not None:
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "retour_client": data,
                    }
                )

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "retour_client": data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "retour_client": [],
                }
            )
