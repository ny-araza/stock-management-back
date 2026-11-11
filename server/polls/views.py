# from django.shortcuts import render
from datetime import timedelta
from pickletools import float8

from django.conf import settings
from django.contrib.postgres.forms.hstore import ValidationError
from django.db import transaction
from django.db.models import (
    Case,
    Exists,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Sum,
    When,
)
from django.utils import timezone
from django.utils.regex_helper import get_quantifier
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action, api_view
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

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
    TAutorisation,
    TClient,
    TCmdFournis,
    TEntree,
    TFamille,
    TFournis,
    TInStock,
    TLigneCmdFournis,
    TLigneEntree,
    TLigneProforma,
    TLigneRtc,
    TLigneRtf,
    TLigneVente,
    TLot,
    TMvtStock,
    TOutStock,
    TPrix,
    TProforma,
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
    ProformaSerializers,
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
    authentication_classes = [SessionAuthentication]

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
    authentication_classes = [SessionAuthentication]

    def list(self, request):
        """
        Cette méthode intercepte le GET sur /api/me/
        Grâce à l'authentification JWT, request.user
        contient l'utilisateur connecté.
        """
        try:
            user = request.user

            # Récupérer les autorisations de l'utilisateur
            authorizations = TAutorisation.objects.filter(
                aut_acc_code=user.use_acc_code
            ).values("aut_acc_code", "aut_men_code", "aut_acces")

            return Response(
                {
                    "status": True,
                    "user": {
                        "user_id": user.use_id,
                        "use_login": user.use_login,
                        "use_acc_code": user.use_acc_code,
                        "use_enabled": user.use_enabled,
                    },
                    # Ajout des autorisations
                    "authorizations": list(authorizations),
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
    authentication_classes = [SessionAuthentication]
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
            queryset = queryset.order_by("-cli_datecre")
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
    authentication_classes = [SessionAuthentication]
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
            queryset = queryset.order_by("-vte_datecre")
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

    def retrieve(self, request, *args, **kwargs):
        try:
            vente = self.get_object()

            serializer = self.get_serializer(vente)
            data = serializer.data

            lignes = TLigneVente.objects.filter(vtel_vte_code=vente.vte_code)

            data["lignes"] = LigneVenteSerializer(lignes, many=True).data

            return Response(
                {
                    "status": True,
                    "message": "Vente récupérée avec succès",
                    "vente": data,
                }
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                },
                status=500,
            )


# liste BC
class BcViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    queryset = TCmdFournis.objects.all()
    serializer_class = BcSerializers
    pagination_class = ListPagination

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = BcFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            queryset = queryset.order_by("-cmf_datecre")

            page = self.paginate_queryset(queryset)

            if page is not None:
                commandes = page
            else:
                commandes = queryset

            serializer = self.get_serializer(commandes, many=True)
            bc_list = serializer.data

            # Récupérer les IDs des bons de commande
            commande_ids = [commande.cmf_code for commande in commandes]
            # Récupérer toutes les lignes associées en une seule requête
            lignes = TLigneCmdFournis.objects.filter(cmfl_cmf_code__in=commande_ids)
            # Organiser les lignes par ID du bon de commande
            lignes_par_commande = {}

            for ligne in lignes:
                commande_id = ligne.cmfl_cmf_code
                if commande_id not in lignes_par_commande:
                    lignes_par_commande[commande_id] = []

                lignes_par_commande[commande_id].append(
                    {
                        "cmfl_id": ligne.cmfl_id,
                        "cmfl_cmf_code": ligne.cmfl_cmf_code,
                        "cmfl_Quantite": ligne.cmfl_quantite,
                        "cmfl_PrixAchat": ligne.cmfl_prixachat,
                        "cmfl_Tva": ligne.cmfl_tva,
                        "cmfl_TotalHT": ligne.cmfl_totalht,
                        "cmfl_Art_Code": ligne.cmfl_art_code,
                        "cmfl_fou_Code": ligne.cmfl_fou_code,
                        "cmfl_TotalTTC": ligne.cmfl_totalttc,
                        "cmfl_pri_id": ligne.cmfl_pri_id,
                    }
                )
            # Ajouter les lignes à chaque bon de commande
            for commande in bc_list:
                commande_id = commande["cmf_code"]
                commande["ligne"] = lignes_par_commande.get(commande_id, [])
                fournisseur = TFournis.objects.filter(
                    fou_code=commande["cmf_fou_code"]
                ).first()

                commande["fournisseur"] = (
                    FournisseurSerializers(fournisseur).data if fournisseur else None
                )
            # Réponse paginée
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
                        "commandes": bc_list,
                    }
                )

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "commandes": bc_list,
                }
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "commandes": [],
                }
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            # Récupérer le bon de commande
            commande = self.get_object()

            # Sérialiser les informations principales
            serializer = self.get_serializer(commande)
            data = serializer.data

            # Récupérer toutes les lignes liées au bon de commande
            lignes = TLigneCmdFournis.objects.filter(cmfl_cmf_code=commande.cmf_code)

            # Construire la liste des articles
            lignes_data = []

            for ligne in lignes:
                lignes_data.append(
                    {
                        "cmfl_id": ligne.cmfl_id,
                        "cmfl_cmf_code": ligne.cmfl_cmf_code,
                        "cmfl_Quantite": ligne.cmfl_quantite,
                        "cmfl_PrixAchat": ligne.cmfl_prixachat,
                        "cmfl_Tva": ligne.cmfl_tva,
                        "cmfl_TotalHT": ligne.cmfl_totalht,
                        "cmfl_Art_Code": ligne.cmfl_art_code,
                        "cmfl_fou_Code": ligne.cmfl_fou_code,
                        "cmfl_TotalTTC": ligne.cmfl_totalttc,
                        "cmfl_pri_id": ligne.cmfl_pri_id,
                    }
                )

            # Ajouter les lignes au bon de commande
            data["ligne"] = lignes_data
            fournisseur = TFournis.objects.filter(fou_code=data["cmf_fou_code"]).first()

            data["fournisseur"] = (
                FournisseurSerializers(fournisseur).data if fournisseur else None
            )

            return Response(
                {
                    "status": True,
                    "message": "Bon de commande récupéré avec succès",
                    "commandes": data,
                }
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                },
                status=500,
            )

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                commande = self.get_object()

                # Récupérer les lignes envoyées par React
                data = request.data.copy()
                lignes_data = data.pop("ligne", None)

                # Modifier les informations principales du BC
                serializer = self.get_serializer(commande, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                # Modifier les lignes uniquement si elles sont présentes
                if lignes_data is not None:
                    lignes_ids = []

                    for ligne_data in lignes_data:
                        ligne_id = ligne_data.get("cmfl_id")

                        valeurs = {
                            "cmfl_cmf_id": commande.cmf_id,
                            "cmfl_cmf_code": commande.cmf_code,
                            "cmfl_quantite": ligne_data.get("cmfl_Quantite", 0),
                            "cmfl_prixachat": ligne_data.get("cmfl_PrixAchat", 0),
                            "cmfl_tva": ligne_data.get("cmfl_Tva", 0),
                            "cmfl_totalht": ligne_data.get("cmfl_TotalHT", 0),
                            "cmfl_art_code": ligne_data.get("cmfl_Art_Code"),
                            "cmfl_fou_code": ligne_data.get(
                                "cmfl_fou_Code", commande.cmf_fou_code
                            ),
                            "cmfl_totalttc": ligne_data.get("cmfl_TotalTTC", 0),
                            "cmfl_pri_id": ligne_data.get("cmfl_pri_id"),
                        }

                        if ligne_id:
                            # Modifier une ligne existante
                            ligne = TLigneCmdFournis.objects.filter(
                                cmfl_id=ligne_id,
                                cmfl_cmf_code=commande.cmf_code,
                            ).first()

                            if not ligne:
                                return Response(
                                    {
                                        "status": False,
                                        "message": f"Ligne {ligne_id} introuvable.",
                                    },
                                    status=status.HTTP_404_NOT_FOUND,
                                )

                            for champ, valeur in valeurs.items():
                                setattr(ligne, champ, valeur)

                            ligne.save()
                            lignes_ids.append(ligne.cmfl_id)

                        else:
                            # Ajouter une nouvelle ligne
                            nouvelle_ligne = TLigneCmdFournis.objects.create(**valeurs)
                            lignes_ids.append(nouvelle_ligne.cmfl_id)

                    # Supprimer les anciennes lignes retirées du formulaire
                    TLigneCmdFournis.objects.filter(
                        cmfl_cmf_code=commande.cmf_code
                    ).exclude(cmfl_id__in=lignes_ids).delete()

                return Response(
                    {
                        "status": True,
                        "message": "Bon de commande modifié avec succès.",
                        "commandes": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# liste BC
class FournisseurViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
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
            queryset = queryset.order_by("-fou_datecre")
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
    authentication_classes = [SessionAuthentication]
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
    authentication_classes = [SessionAuthentication]
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
            elif table_name == "t_retour_fournis":
                prefix = "rtf"
            elif table_name == "t_ligne_rtf":
                prefix = "rtfl"
            elif table_name == "t_retour_client":
                prefix = "rtc"
            elif table_name == "t_ligne_rtc":
                prefix = "rtcl"
            elif table_name == "t_ligne_proforma":
                prefix = "prol"
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
            search = request.GET.get("search", "").strip()

            if not search:
                return Response({"status": True, "articles": []})

            # Recherche des articles par nom
            article_codes = TArticle.objects.filter(
                art_nom__icontains=search
            ).values_list("art_code", flat=True)

            # Recherche des prix/articles par code ou nom
            articles = list(
                TPrix.objects.filter(
                    Q(pri_art_code__icontains=search)
                    | Q(pri_art_code__in=article_codes)
                ).values("pri_id", "pri_art_code", "pri_achat", "pri_vte", "pri_tva", "pri_unitevente")
            )

            if not articles:
                return Response(
                    {
                        "status": False,
                        "message": "Pas d'article correspondant",
                        "articles": [],
                    }
                )
            # Codes des articles trouvés
            codes = list(set(a["pri_art_code"] for a in articles))

            # Informations des articles
            articles_data = TArticle.objects.filter(art_code__in=codes).values(
                "art_code", "art_nom"
            )

            def get_quantite(code: str) -> int:
                total_quantite_lots = (
                    TLot.objects.filter(
                        lot_art_code=code, lot_dateper__gt=timezone.now().date()
                    ).aggregate(total=Sum("lot_art_quantite"))
                )["total"] or 0
                return total_quantite_lots

            # Dictionnaire des articles
            articles_dict = {article["art_code"]: article for article in articles_data}
            # Récupération de TOUS les lots des articles
            lots = TLot.objects.filter(
                lot_art_code__in=codes, lot_dateper__gt=timezone.now().date()
            ).values(
                "lot_id", "lot_art_code", "lot_code", "lot_dateper", "lot_art_quantite"
            )

            # Regrouper les lots par article
            lots_par_article = {}

            for lot in lots:
                article_code = lot["lot_art_code"]

                if article_code not in lots_par_article:
                    lots_par_article[article_code] = []

                lots_par_article[article_code].append(
                    {
                        "lot_id": lot["lot_id"],
                        "lot_code": lot["lot_code"],
                        "lot_datePeremption": lot["lot_dateper"],
                        "lot_quantite": lot["lot_art_quantite"],
                    }
                )
            return Response(
                {
                    "status": True,
                    "articles": [
                        {
                            "id": a["pri_id"],
                            "code": a["pri_art_code"],
                            "prix_ht": a["pri_achat"],
                            "prix_vte": a["pri_vte"],
                            "pri_tva": a["pri_tva"],
                            "pri_unitevente": a["pri_unitevente"],
                            "nom_article": articles_dict.get(a["pri_art_code"], {}).get(
                                "art_nom", ""
                            ),
                            "quantite_stock": get_quantite(a["pri_art_code"]),
                            # Tableau des lots
                            "lots": lots_par_article.get(a["pri_art_code"], []),
                        }
                        for a in articles
                    ],
                }
            )

        except Exception as e:
            return Response({"status": False, "message": str(e), "articles": []})


class ExpiredArticlesStock(APIView):
    """
    Retourne, pour chaque article ayant des lots périmés :
    - le total périmé de l'article
    - le détail des lots périmés
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            today = timezone.now().date()

            # Tous les lots périmés avec du stock restant
            lots = list(
                TLot.objects.filter(
                    lot_dateper__lte=today,
                    lot_art_quantite__gt=0,
                ).values(
                    "lot_id",
                    "lot_art_code",
                    "lot_code",
                    "lot_dateper",
                    "lot_art_quantite",
                )
            )

            if not lots:
                return Response({"status": True, "articles": []})

            codes = list({lot["lot_art_code"] for lot in lots})

            # Noms des articles
            articles_dict = {
                a["art_code"]: a["art_nom"]
                for a in TArticle.objects.filter(art_code__in=codes).values(
                    "art_code", "art_nom"
                )
            }

            # Un prix par article (le premier trouvé)
            prix_dict = {}
            for p in TPrix.objects.filter(pri_art_code__in=codes).values(
                "pri_id", "pri_art_code", "pri_achat", "pri_vte", "pri_tva"
            ):
                prix_dict.setdefault(p["pri_art_code"], p)

            # Regroupement des lots par article + total périmé
            grouped = {}
            for lot in lots:
                code = lot["lot_art_code"]
                grouped.setdefault(code, {"total": 0, "lots": []})
                grouped[code]["total"] += lot["lot_art_quantite"] or 0
                grouped[code]["lots"].append(
                    {
                        "lot_id": lot["lot_id"],
                        "lot_code": lot["lot_code"],
                        "lot_datePeremption": lot["lot_dateper"],
                        "lot_quantite": lot["lot_art_quantite"],
                    }
                )

            result = []
            for code, data in grouped.items():
                prix = prix_dict.get(code, {})
                result.append(
                    {
                        "id": prix.get("pri_id", 0),
                        "code": code,
                        "nom_article": articles_dict.get(code, ""),
                        "prix_ht": prix.get("pri_achat", 0),
                        "prix_vte": prix.get("pri_vte", 0),
                        "pri_tva": prix.get("pri_tva", 0),
                        "quantite_perimee": data["total"],
                        "lots": data["lots"],
                    }
                )

            return Response({"status": True, "articles": result})

        except Exception as e:
            return Response({"status": False, "message": str(e), "articles": []})


class UpdateCmfView(APIView):
    def patch(self, request, cmf_id):
        try:
            with transaction.atomic():
                command = TCmdFournis.objects.get(cmf_id=cmf_id)

                command.cmf_islivre = request.data.get(
                    "pro_islivre", command.cmf_islivre
                )
                command.cmf_enabled = request.data.get(
                    "pro_enabled", command.cmf_enabled
                )
                command.cmf_usermdf = request.data.get(
                    "pro_usermdf", command.cmf_usermdf
                )
                command.cmf_datemdf = timezone.now()

                command.save(
                    update_fields=[
                        "cmf_islivre",
                        "cmf_enabled",
                        "cmf_usermdf",
                        "cmf_datemdf",
                    ]
                )

            return Response(
                {
                    "message": "cmfforma mise à jour avec succès.",
                    "cmf_id": command.cmf_id,
                    "cmf_islivre": command.cmf_islivre,
                    "cmf_enabled": command.cmf_enabled,
                    "cmf_usermdf": command.cmf_usermdf,
                    "cmf_datemdf": command.cmf_datemdf,
                },
                status=status.HTTP_200_OK,
            )

        except TCmdFournis.DoesNotExist:
            return Response(
                {"error": "Cmf fournis introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CFAutoComplete(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            search = request.GET.get("search", "").strip()

            if not search:
                return Response({"status": True, "cmf_fournis": []})

            # Récupérer les 30 commandes fournisseurs correspondantes
            cmf_fournis = TCmdFournis.objects.filter(
                cmf_code__icontains=search, cmf_islivre=False
            ).order_by(
                Case(
                    When(cmf_code__istartswith=search, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
                "cmf_code",
            )[:30]

            result = []

            for fournisseur in cmf_fournis:
                # ==========================================
                # LIGNES DE LA COMMANDE
                # ==========================================

                lignes = TLigneCmdFournis.objects.filter(
                    cmfl_cmf_code=fournisseur.cmf_code
                )

                # Récupérer les codes articles
                art_codes = [
                    ligne.cmfl_art_code for ligne in lignes if ligne.cmfl_art_code
                ]

                # Récupérer les articles
                articles = TArticle.objects.filter(art_code__in=art_codes)

                # Dictionnaire des articles
                articles_dict = {article.art_code: article for article in articles}

                # ==========================================
                # INFORMATIONS DU FOURNISSEUR
                # ==========================================

                fournisseur_obj = TFournis.objects.filter(
                    fou_code=fournisseur.cmf_fou_code
                ).first()

                # ==========================================
                # DONNÉES DE LA COMMANDE
                # ==========================================

                fournisseur_data = BcSerializers(fournisseur).data

                # ==========================================
                # AJOUTER LE FOURNISSEUR
                # ==========================================

                fournisseur_data["fournisseur"] = (
                    FournisseurSerializers(fournisseur_obj).data
                    if fournisseur_obj
                    else None
                )

                # ==========================================
                # AJOUTER LES LIGNES
                # ==========================================

                fournisseur_data["ligne"] = []

                for ligne in lignes:
                    article = articles_dict.get(ligne.cmfl_art_code)

                    fournisseur_data["ligne"].append(
                        {
                            "cmfl_cmf_code": ligne.cmfl_cmf_code,
                            "cmfl_Quantite": ligne.cmfl_quantite,
                            "cmfl_PrixAchat": ligne.cmfl_prixachat,
                            "cmfl_Tva": ligne.cmfl_tva,
                            "cmfl_montant_tva": (ligne.cmfl_tva / 100)
                            * (ligne.cmfl_totalht),
                            "cmfl_TotalHT": ligne.cmfl_totalht,
                            "cmfl_Art_Code": ligne.cmfl_art_code,
                            "cmfl_fou_Code": ligne.cmfl_fou_code,
                            "cmfl_TotalTTC": ligne.cmfl_totalttc,
                            "cmfl_pri_id": ligne.cmfl_id,
                            # Informations de l'article
                            "art_nom": (article.art_nom if article else ""),
                        }
                    )

                result.append(fournisseur_data)

            return Response({"status": True, "cmf_fournis": result})

        except Exception as e:
            return Response({"status": False, "message": str(e), "cmf_fournis": []})


class RTCAutoComplete(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            search = request.GET.get("search", "").strip()

            if not search:
                return Response({"status": True, "ventes": []})

            # Récupérer les 30 commandes fournisseurs correspondantes
            ventes = TVente.objects.filter(
                vte_code__icontains=search, vte_paye=False
            ).order_by(
                Case(
                    When(vte_code__istartswith=search, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
                "vte_code",
            )[:30]

            result = []

            for vente in ventes:
                # ==========================================
                # LIGNES DE LA COMMANDE
                # ==========================================

                lignes = TLigneVente.objects.filter(vtel_vte_code=vente.vte_code)

                # Récupérer les codes articles
                art_codes = [
                    ligne.vtel_art_code for ligne in lignes if ligne.vtel_art_code
                ]

                # Récupérer les articles
                articles = TArticle.objects.filter(art_code__in=art_codes)

                # Dictionnaire des articles
                articles_dict = {article.art_code: article for article in articles}

                # ==========================================
                # INFORMATIONS DU FOURNISSEUR
                # ==========================================

                client_obj = TClient.objects.filter(cli_code=vente.vte_cli_code).first()

                # ==========================================
                # DONNÉES DE LA COMMANDE
                # ==========================================

                vente_data = VenteSerializers(vente).data

                # ==========================================
                # AJOUTER LE FOURNISSEUR
                # ==========================================

                vente_data["client"] = (
                    ClientsSerializers(client_obj).data if client_obj else None
                )

                # ==========================================
                # AJOUTER LES LIGNES
                # ==========================================

                vente_data["ligne"] = []

                for ligne in lignes:
                    article = articles_dict.get(ligne.vtel_art_code)

                    vente_data["ligne"].append(
                        {
                            "vtel_rtc_code": ligne.vtel_rtc_code,
                            "vtel_Quantite": ligne.vtel_quantite,
                            "vtel_PrixAchat": ligne.vtel_prixachat,
                            "vtel_Tva": ligne.vtel_tva,
                            "vtel_montant_tva": (ligne.vtel_tva / 100)
                            * (ligne.vtel_totalht),
                            "vtel_TotalHT": ligne.vtel_totalht,
                            "vtel_Art_Code": ligne.vtel_art_code,
                            "vtel_fou_Code": ligne.vtel_fou_code,
                            "vtel_TotalTTC": ligne.vtel_totalttc,
                            "vtel_pri_id": ligne.vtel_id,
                            # Informations de l'article
                            "art_nom": (article.art_nom if article else ""),
                        }
                    )

                result.append(vente_data)

            return Response({"status": True, "ventes": result})

        except Exception as e:
            return Response({"status": False, "message": str(e), "ventes": []})


class UpdateProformaView(APIView):
    def patch(self, request, pro_id):
        try:
            with transaction.atomic():
                proforma = TProforma.objects.get(pro_id=pro_id)

                proforma.pro_islivre = request.data.get(
                    "pro_islivre", proforma.pro_islivre
                )
                proforma.pro_enabled = request.data.get(
                    "pro_enabled", proforma.pro_enabled
                )
                proforma.pro_usermdf = request.data.get(
                    "pro_usermdf", proforma.pro_usermdf
                )
                proforma.pro_datemdf = timezone.now()

                proforma.save(
                    update_fields=[
                        "pro_islivre",
                        "pro_enabled",
                        "pro_usermdf",
                        "pro_datemdf",
                    ]
                )

            return Response(
                {
                    "message": "Proforma mise à jour avec succès.",
                    "pro_id": proforma.pro_id,
                    "pro_islivre": proforma.pro_islivre,
                    "pro_enabled": proforma.pro_enabled,
                    "pro_usermdf": proforma.pro_usermdf,
                    "pro_datemdf": proforma.pro_datemdf,
                },
                status=status.HTTP_200_OK,
            )

        except TProforma.DoesNotExist:
            return Response(
                {"error": "Proforma introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateVente(APIView):
    def patch(self, request, vte_id):
        try:
            with transaction.atomic():
                vente = TVente.objects.get(vte_id=vte_id)

                vente.vte_valide = request.data.get("vte_valide", vente.vte_valide)
                vente.vte_paye = request.data.get("vte_paye", vente.vte_paye)
                vente.vte_usermdf = request.data.get("vte_usermdf", vente.vte_usermdf)
                vente.vte_datemdf = timezone.now()

                vente.save(
                    update_fields=[
                        "vte_valide",
                        "vte_paye",
                        "vte_usermdf",
                        "vte_datemdf",
                    ]
                )

            return Response(
                {
                    "message": "vente mise à jour avec succès.",
                    "vte_id": vente.vte_id,
                    "vte_valide": vente.vte_valide,
                    "vte_paye": vente.vte_paye,
                    "vte_usermdf": vente.vte_usermdf,
                    "vte_datemdf": vente.vte_datemdf,
                },
                status=status.HTTP_200_OK,
            )

        except TVente.DoesNotExist:
            return Response(
                {"error": "vente introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateCF(APIView):
    def patch(self, request, cmf_id):
        try:
            with transaction.atomic():
                cf = TCmdFournis.objects.get(cmf_id=cmf_id)

                cf.cmf_valide = request.data.get("cmf_is_livre", cf.cmf_is_livre)
                cf.cmf_paye = request.data.get("cmf_paye", cf.cmf_is_paye)
                cf.cmf_usermdf = request.data.get("cmf_usermdf", cf.cmf_usermdf)
                cf.cmf_datemdf = timezone.now()

                cf.save(
                    update_fields=[
                        "cmf_valide",
                        "cmf_paye",
                        "cmf_usermdf",
                        "cmf_datemdf",
                    ]
                )

            return Response(
                {
                    "message": "cf mise à jour avec succès.",
                    "cmf_id": cf.cmf_id,
                    "cmf_valide": cf.cmf_valide,
                    "cmf_paye": cf.cmf_paye,
                    "cmf_usermdf": cf.cmf_usermdf,
                    "cmf_datemdf": cf.cmf_datemdf,
                },
                status=status.HTTP_200_OK,
            )

        except TCmdFournis.DoesNotExist:
            return Response(
                {"error": "cf introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProformaAutoComplete(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            search = request.GET.get("search", "").strip()

            if not search:
                return Response({"status": True, "proforma": []})

            # Récupérer les 30 commandes fournisseurs correspondantes
            list_proforma = TProforma.objects.filter(
                pro_code__icontains=search,
                pro_islivre=False,
            ).order_by(
                Case(
                    When(pro_code__istartswith=search, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
                "pro_code",
            )[:30]

            result = []

            for p in list_proforma:
                # ==========================================
                # LIGNES DE LA COMMANDE
                # ==========================================

                lignes = TLigneProforma.objects.filter(prol_pro_code=p.pro_code)

                # Récupérer les codes articles
                art_codes = [
                    ligne.prol_art_code for ligne in lignes if ligne.prol_art_code
                ]

                # Récupérer les articles
                articles = TArticle.objects.filter(art_code__in=art_codes)

                # Dictionnaire des articles
                articles_dict = {article.art_code: article for article in articles}

                # ==========================================
                # INFORMATIONS DU FOURNISSEUR
                # ==========================================

                p_obj = TClient.objects.filter(cli_code=p.pro_cli_code).first()

                # ==========================================
                # DONNÉES DE LA COMMANDE
                # ==========================================

                client_data = ProformaSerializers(p).data

                # ==========================================
                # AJOUTER LE FOURNISSEUR
                # ==========================================

                client_data["client"] = ClientsSerializers(p_obj).data if p_obj else []

                # ==========================================
                # AJOUTER LES LIGNES
                # ==========================================

                client_data["ligne"] = []

                for ligne in lignes:
                    article = articles_dict.get(ligne.prol_art_code)

                    client_data["ligne"].append(
                        {
                            "prol_pro_code": ligne.prol_pro_code,
                            "prol_quantite": ligne.prol_quantite,
                            "prol_prixvente": ligne.prol_prixunit,
                            "prol_tva": ligne.prol_tva,
                            "prol_montant_tva": (ligne.prol_tva / 100)
                            * (ligne.prol_totalht),
                            "prol_totalht": ligne.prol_totalht,
                            "prol_art_code": ligne.prol_art_code,
                            "prol_cli_code": ligne.prol_cli_code,
                            "prol_totalttc": ligne.prol_totalttc,
                            "prol_pri_id": ligne.prol_id,
                            "prol_lot_id": ligne.prol_lot_id,
                            "prol_lot_dateper": ligne.prol_lot_dateper,
                            # Informations de l'article
                            "art_nom": (article.art_nom if article else ""),
                        }
                    )

                result.append(client_data)

            return Response({"status": True, "proforma": result})

        except Exception as e:
            return Response({"status": False, "message": str(e), "proforma": []})


class BLAutoComplete(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            search = request.GET.get("search", "").strip()

            if not search:
                return Response({"status": True, "t_entree": []})

            # Récupérer les 30 commandes fournisseurs correspondantes
            entree = TEntree.objects.filter(
                ent_code__icontains=search,
            ).order_by(
                Case(
                    When(ent_code__istartswith=search, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
                "ent_code",
            )[:30]

            result = []

            for ligne in entree:
                # ==========================================
                # LIGNES DE LA COMMANDE
                # ==========================================

                lignes = TLigneEntree.objects.filter(entl_ent_code=ligne.ent_code)

                # Récupérer les codes articles
                art_codes = [
                    ligne.entl_art_code for ligne in lignes if ligne.entl_art_code
                ]

                # Récupérer les articles
                articles = TArticle.objects.filter(art_code__in=art_codes)

                # Dictionnaire des articles
                articles_dict = {article.art_code: article for article in articles}

                # ==========================================
                # INFORMATIONS DU FOURNISSEUR
                # ==========================================

                fournisseur_obj = TFournis.objects.filter(
                    fou_code=ligne.ent_fou_code
                ).first()

                # ==========================================
                # DONNÉES DE LA COMMANDE
                # ==========================================

                fournisseur_data = EntreeSerializer(ligne).data

                # ==========================================
                # AJOUTER LE FOURNISSEUR
                # ==========================================

                fournisseur_data["fournisseur"] = (
                    FournisseurSerializers(fournisseur_obj).data
                    if fournisseur_obj
                    else None
                )

                # ==========================================
                # AJOUTER LES LIGNES
                # ==========================================

                fournisseur_data["ligne"] = []

                for ligne in lignes:
                    article = articles_dict.get(ligne.entl_art_code)

                    fournisseur_data["ligne"].append(
                        {
                            "entl_cmf_code": ligne.entl_ent_code,
                            "entl_quantite": ligne.entl_quantite,
                            "entl_prixunit": ligne.entl_prix,
                            "entl_tva": ligne.entl_tva,
                            "entl_ht": ligne.entl_ht,
                            "entl_art_code": ligne.entl_art_code,
                            "entl_fou_Code": ligne.entl_fou_code,
                            "entl_ttc": ligne.entl_ttc,
                            "entl_pri_id": ligne.entl_id,
                            "entl_dateper": ligne.entl_dateper,
                            "entl_montant_tva": (ligne.entl_tva / 100)
                            * (ligne.entl_ht),
                            # Informations de l'article
                            "art_nom": (article.art_nom if article else ""),
                            "entl_lot_id": ligne.entl_lot,
                            "entl_remise": ligne.entl_remise,
                            "entl_montant_remise": (ligne.entl_remise / 100)
                            * ligne.entl_ht,
                        }
                    )

                result.append(fournisseur_data)

            return Response({"status": True, "t_entree": result})

        except Exception as e:
            return Response({"status": False, "message": str(e), "t_entree": []})


class FAAutoComplete(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            search = request.GET.get("search", "").strip()

            if not search:
                return Response({"status": True, "t_vente": []})

            # Récupérer les 30 commandes fournisseurs correspondantes
            entree = TVente.objects.filter(
                vte_code__icontains=search, vte_valide=True
            ).order_by(
                Case(
                    When(vte_code__istartswith=search, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
                "vte_code",
            )[:10]

            result = []

            for ligne in entree:
                # ==========================================
                # LIGNES DE LA COMMANDE
                # ==========================================

                lignes = TLigneVente.objects.filter(vtel_vte_code=ligne.vte_code)
                # Récupérer les codes articles
                art_codes = [
                    ligne.vtel_art_code for ligne in lignes if ligne.vtel_art_code
                ]

                # Récupérer les articles
                articles = TArticle.objects.filter(art_code__in=art_codes)

                # Dictionnaire des articles
                articles_dict = {article.art_code: article for article in articles}

                # ==========================================
                # INFORMATIONS DU FOURNISSEUR
                # ==========================================

                fournisseur_obj = TClient.objects.filter(
                    cli_code=ligne.vte_cli_code
                ).first()

                # ==========================================
                # DONNÉES DE LA COMMANDE
                # ==========================================

                fournisseur_data = VenteSerializers(ligne).data

                # ==========================================
                # AJOUTER LE CLIENT
                # ==========================================

                fournisseur_data["client"] = (
                    ClientsSerializers(fournisseur_obj).data
                    if fournisseur_obj
                    else None
                )

                # ==========================================
                # AJOUTER LES LIGNES
                # ==========================================

                fournisseur_data["ligne"] = []

                for ligne in lignes:
                    article = articles_dict.get(ligne.vtel_art_code)
                    fournisseur_data["ligne"].append(
                        {
                            "vtel_vte_code": ligne.vtel_vte_code,
                            "vtel_quantite": ligne.vtel_quantite,
                            "vtel_tva": ligne.vtel_tva,
                            "vtel_ht": ligne.vtel_ht,
                            "vtel_art_code": ligne.vtel_art_code,
                            "vtel_cli_code": ligne.vtel_cli_code,
                            "vtel_ttc": ligne.vtel_ttc,
                            "vtel_prixunit": ligne.vtel_prixunit,
                            "vtel_lot_code": ligne.vtel_lot_id,
                            "vtel_dateper": ligne.vtel_lot_dateper,
                            "vtel_pri_id": ligne.vtel_pri_id,
                            "vtel_montant_tva": (ligne.vtel_tva / 100)
                            * (ligne.vtel_ht),
                            # Informations de l'article
                            "art_nom": (article.art_nom if article else ""),
                        }
                    )

                result.append(fournisseur_data)

            return Response({"status": True, "t_vente": result})

        except Exception as e:
            return Response({"status": False, "message": str(e), "t_vente": []})


class StockViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
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

            # Sérialisation du stock
            serializer = self.get_serializer(stock)
            stock_data = serializer.data

            # Récupérer tous les lots de l'article
            lots = TLot.objects.filter(
                lot_art_code=art_code, lot_dateper__gt=timezone.now().date()
            ).values("lot_id", "lot_code", "lot_dateper", "lot_art_quantite")

            # Calcul du total des quantités de tous les lots
            total_quantite_lots = (
                TLot.objects.filter(
                    lot_art_code=art_code, lot_dateper__gt=timezone.now().date()
                ).aggregate(total=Sum("lot_art_quantite"))
            )["total"] or 0

            # Ajouter les lots
            stock_data["lots"] = [
                {
                    "lot_id": lot["lot_id"],
                    "lot_code": lot["lot_code"],
                    "lot_dateper": lot["lot_dateper"],
                    "lot_qte": lot["lot_art_quantite"],
                }
                for lot in lots
            ]

            # Ajouter le total des quantités des lots
            stock_data["total_quantite_lots"] = total_quantite_lots

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "stock": stock_data,
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

            # Garder uniquement la dernière ligne de chaque article
            queryset = queryset.filter(stk_id=Subquery(derniere_ligne))

            # Pagination
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)

                data = serializer.data

                for stock in data:
                    art_code = stock["stk_art_code"]

                    # Récupérer l'article
                    article = TArticle.objects.filter(art_code=art_code).first()

                    stock["article_table"] = (
                        ArticlesSerializers(article).data if article else None
                    )

                    # Calculer le total des quantités des lots
                    total_quantite_lots = (
                        TLot.objects.filter(lot_art_code=art_code).aggregate(
                            total=Sum("lot_art_quantite")
                        )
                    )["total"] or 0

                    # Ajouter le total dans le JSON
                    stock["total_quantite_lots"] = total_quantite_lots

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

            # Sans pagination
            serializer = self.get_serializer(queryset, many=True)

            data = serializer.data

            for stock in data:
                art_code = stock["stk_art_code"]

                # Récupérer l'article
                article = TArticle.objects.filter(art_code=art_code).first()

                stock["article_table"] = (
                    ArticlesSerializers(article).data if article else None
                )

                # Calculer le total des quantités des lots
                total_quantite_lots = (
                    TLot.objects.filter(lot_art_code=art_code).aggregate(
                        total=Sum("lot_art_quantite")
                    )
                )["total"] or 0

                # Ajouter le total
                stock["total_quantite_lots"] = total_quantite_lots

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
    authentication_classes = [SessionAuthentication]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = EntreeFilter
    lookup_field = "ent_id"

    # Champs modifiables d'une ligne d'entrée
    LIGNE_FIELDS = [
        "entl_quantite",
        "entl_prixunit",
        "entl_ttc",
        "entl_art_code",
        "entl_pri_id",
        "entl_tva",
        "entl_ht",
        "entl_lot",
        "entl_dateper",
        "entl_prix",
        "entl_remise",
        "entl_usermdf",
    ]

    # ==========================================
    # CONSTRUCTION DE LA RÉPONSE
    # ==========================================

    def get_entree_data(self, entree):
        """
        Retourne une entrée avec ses lignes et son fournisseur.
        """

        data = EntreeSerializer(entree).data

        lignes = TLigneEntree.objects.filter(entl_ent_code=entree.ent_code)

        fournisseur = TFournis.objects.filter(fou_code=entree.ent_fou_code).first()

        data["lignes"] = LigneEntreeSerializer(lignes, many=True).data

        data["fournisseur"] = (
            FournisseurSerializers(fournisseur).data if fournisseur else None
        )

        return data

    # ==========================================
    # LIST
    # ==========================================

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by("-ent_datecre")

        page = self.paginate_queryset(queryset)

        objets = page if page is not None else queryset

        data = [self.get_entree_data(entree) for entree in objets]

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

    # ==========================================
    # RETRIEVE
    # ==========================================

    def retrieve(self, request, *args, **kwargs):
        entree = self.get_object()

        return Response(
            {
                "status": True,
                "message": "Entrée fournisseur récupérée avec succès.",
                "entree": self.get_entree_data(entree),
            }
        )

    # ==========================================
    # UPDATE / PATCH
    # ==========================================

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", request.method == "PATCH")

        with transaction.atomic():
            entree = self.get_object()

            data = request.data.copy()

            # Récupérer les lignes envoyées par React
            lignes_data = data.pop("lignes", None)

            # Ne pas modifier les données calculées ou en lecture seule
            data.pop("fournisseur", None)

            # Vérifier si l'entrée est déjà payée
            if entree.ent_is_paye:
                raise ValidationError("Impossible de modifier une entrée déjà payée.")

            # ======================================
            # MODIFICATION DE L'ENTRÉE PRINCIPALE
            # ======================================

            serializer = self.get_serializer(entree, data=data, partial=partial)

            serializer.is_valid(raise_exception=True)
            entree = serializer.save()

            # ======================================
            # MODIFICATION DES LIGNES
            # ======================================

            if lignes_data is not None:
                if not isinstance(lignes_data, list):
                    raise ValidationError(
                        {
                            "lignes": "Les lignes doivent être envoyées sous forme de liste."
                        }
                    )

                ids_envoyes = []

                for ligne_data in lignes_data:
                    ligne_data = dict(ligne_data)

                    ligne_id = ligne_data.pop("entl_id", None)

                    # Retirer les champs non modifiables
                    ligne_data.pop("entl_ent_code", None)
                    ligne_data.pop("entl_fou_code", None)
                    ligne_data.pop("entl_datecre", None)
                    ligne_data.pop("entl_usercre", None)

                    champs = {
                        key: value
                        for key, value in ligne_data.items()
                        if key in self.LIGNE_FIELDS
                    }

                    if ligne_id:
                        # Vérifier que la ligne appartient bien à cette entrée
                        try:
                            ligne = TLigneEntree.objects.get(
                                entl_id=ligne_id, entl_ent_code=entree.ent_code
                            )
                        except TLigneEntree.DoesNotExist:
                            raise ValidationError(
                                {
                                    "lignes": (
                                        f"La ligne {ligne_id} "
                                        "n'appartient pas à cette entrée."
                                    )
                                }
                            )

                        for champ, valeur in champs.items():
                            setattr(ligne, champ, valeur)

                        ligne.entl_ent_code = entree.ent_code
                        ligne.entl_fou_code = entree.ent_fou_code

                        ligne.save()

                        ids_envoyes.append(ligne.entl_id)

                    else:
                        # Création d'une nouvelle ligne
                        nouvelle_ligne = TLigneEntree.objects.create(
                            entl_ent_code=entree.ent_code,
                            entl_fou_code=entree.ent_fou_code,
                            **champs,
                        )

                        ids_envoyes.append(nouvelle_ligne.entl_id)

                # Supprimer les anciennes lignes absentes du formulaire
                TLigneEntree.objects.filter(entl_ent_code=entree.ent_code).exclude(
                    entl_id__in=ids_envoyes
                ).delete()

            # ======================================
            # RÉPONSE FINALE
            # ======================================

            return Response(
                {
                    "status": True,
                    "message": "Entrée fournisseur modifiée avec succès.",
                    "entree": self.get_entree_data(entree),
                },
                status=status.HTTP_200_OK,
            )

    # ==========================================
    # PARTIAL UPDATE
    # ==========================================

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class SortitViewSet(viewsets.ModelViewSet):
    queryset = TOutStock.objects.all()
    serializer_class = SortitSerializer
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = SortitFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by(
                "-out_datecre"
            )
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
    authentication_classes = [SessionAuthentication]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = InStockFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by("-in_datecre")
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
    authentication_classes = [SessionAuthentication]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = MvtStockFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by(
                "-mvt_datecre"
            )
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
    queryset = TMvtStock.objects.all().order_by("-mvt_datecre")

    serializer_class = MvtStockSerializer

    pagination_class = ListPagination

    permission_classes = [IsAuthenticated]

    authentication_classes = [SessionAuthentication]

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

    ordering = ["-mvt_datecre"]


class RtfViewSet(viewsets.ModelViewSet):
    queryset = TRetourFournis.objects.all()
    serializer_class = RtfSerializer
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = RtfFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by(
                "-rtf_datecre"
            )
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
    authentication_classes = [SessionAuthentication]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = RtcFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by(
                "-rtc_datecre"
            )
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


# checjk if the datepay is <= toaday


class NotificationPaiementView(viewsets.ModelViewSet):
    serializer_class = EntreeSerializer
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        today = timezone.localdate()
        date_limite = today + timedelta(days=2)

        return TEntree.objects.filter(
            ent_is_paye=False,
            ent_datepay__isnull=False,
            ent_datepay__lte=date_limite,
        ).order_by("-ent_datecre", "ent_datepay", "-ent_id")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)

            objets = page if page is not None else queryset

            serializer = self.get_serializer(objets, many=True)

            data = serializer.data

            if page is not None:
                return Response(
                    {
                        "status": True,
                        "message": "ok",
                        "date_aujourd_hui": timezone.localdate(),
                        "date_limite": timezone.localdate() + timedelta(days=2),
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "notifications": data,
                    }
                )

            return Response(
                {
                    "status": True,
                    "message": "ok",
                    "date_aujourd_hui": timezone.localdate(),
                    "date_limite": timezone.localdate() + timedelta(days=2),
                    "count": len(data),
                    "notifications": data,
                }
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e),
                    "notifications": [],
                }
            )


class LotViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        methods=["post"],
        url_path="deduire-quantite",
    )
    def deduire_quantite(self, request):
        lot_id = request.data.get("lot_id")
        art_code = request.data.get("art_code")
        quantite = request.data.get("quantite")
        op = request.data.get("op", "sortie")

        print(lot_id, art_code, quantite)

        if not lot_id or not art_code or quantite is None:
            return Response(
                {"error": ("lot_id, art_code et quantite sont obligatoires.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantite = int(quantite)
        except (TypeError, ValueError):
            return Response(
                {"error": "La quantité doit être un entier."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantite < 0:
            return Response(
                {"error": "La quantité doit être supérieure à 0."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            lot = TLot.objects.get(
                lot_id=lot_id,
                lot_art_code=art_code,
            )
        except TLot.DoesNotExist:
            return Response(
                {"error": "Lot introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        ancienne_quantite = lot.lot_art_quantite

        if ancienne_quantite < quantite:
            return Response(
                {
                    "error": "Stock insuffisant.",
                    "stock_disponible": ancienne_quantite,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if op == "sortie":
            lot.lot_art_quantite = ancienne_quantite - quantite
        else:
            lot.lot_art_quantite = ancienne_quantite + quantite
        lot.save(update_fields=["lot_art_quantite"])

        return Response(
            {
                "message": "Quantité déduite avec succès.",
                "lot_id": lot.lot_id,
                "art_code": lot.lot_art_code,
                "ancienne_quantite": ancienne_quantite,
                "quantite_deduite": quantite,
                "nouvelle_quantite": lot.lot_art_quantite,
            },
            status=status.HTTP_200_OK,
        )
