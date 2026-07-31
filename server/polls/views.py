# from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
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
    FournisseurFilter,
    VenteFilter,
)
from .models import (
    TArticle,
    TClient,
    TCmdFournis,
    TFamille,
    TFournis,
    TPrix,
    TSousFamille,
    TUsers,
    TVente,
)
from .pagination import ListPagination
from .serializers import (
    ArticlesSerializers,
    BcSerializers,
    ClientsSerializers,
    FamilleSerializers,
    FournisseurSerializers,
    LoginSerializer,
    SousFamilleSerializers,
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
            search = request.query_params.get("search", "").strip()

            if search:
                for word in search.split():
                    queryset = queryset.filter(
                        Q(vte_code__icontains=search)
                        | Q(vte_cli_nom__icontains=search)
                        | Q(vte_payeclient__icontains=search)
                        | Q(vet_operateur__icontains=search)
                    )
            queryset = queryset.order_by("vte_code")
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
                        "ventes": serializer.data,
                    }
                )

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "ventes": serializer.data,
                }
            )
        except Exception as e:
            return Response({"status": False, "message": e, "ventes": []})


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

    print(table_name, pk_field)
    if not table_name or not pk_field:
        return Response(
            {"error": "Les parametres 'table_name'et 'pk_field' sont obligé"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        reference = generate_reference(table_name, pk_field)
        print(reference)
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
            elif table_name == "t_cmd_fournis":
                prefix = "cmf"
            elif table_name == "t_ligne_cmd_fournis":
                prefix = "cmfl"
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
        search = request.GET.get("search", "")
        print(search)
        articles = TPrix.objects.filter(pri_art_code__icontains=search).values(
            "pri_id", "pri_art_code", "pri_achat"
        )
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
