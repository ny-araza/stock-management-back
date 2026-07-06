# from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from .models import TUsers, TArticle, TClient
from .serializers import TUsersSerializer, LoginSerializer, \
            ArticlesSerializers, ClientsSerializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .authentication import CookieJWTAuthentification
from .pagination import ListPagination
from django.utils import timezone
from django.db.models import Q
from .utils import generate_reference
from rest_framework.decorators import api_view
from .services.dynamic_service import create_dynamic_instance


class UserAuthViewSet(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)},
                            status=status.HTTP_401_UNAUTHORIZED)

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
                "use_enabled": user.use_enabled
            }
        }

        response = Response(response_data, status=status.HTTP_200_OK)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
        )

        return response


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


# Articles views
class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = TArticle.objects.all()
    serializer_class = ArticlesSerializers
    pagination_class = ListPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return Response({
                    "status": True,
                    "message": "ok",
                    "count": self.paginator.page.paginator.count,
                    "next": self.paginator.get_next_link(),
                    "previous": self.paginator.get_previous_link(),
                    "articles": serializer.data,
                })
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": False,
                "messages": "ok",
                "articles": serializer.data
            })
        except Exception as e:
            return Response({
                "status": False,
                "messages": e,
                "articles": []
            })


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
            return Response({
                "status": True,
                "user": {
                    "user_id": user.use_id,
                    "use_login": user.use_login,
                    "use_acc_code": user.use_acc_code,
                    "use_enabled": user.use_enabled
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "message": f"Impossible de récupérer l'utilisateur : {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)


# view client
class ClientViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentification]
    queryset = TClient.objects.all()
    serializer_class = ClientsSerializers
    pagination_class = ListPagination

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            search = request.query_params.get("search", "").strip()

            if search:
                for word in search.split():
                    queryset = queryset.filter(
                        Q(cli_code__icontains=search) |
                        Q(cli_nom__icontains=search) |
                        Q(cli_email__icontains=search) |
                        Q(cli_tel1__icontains=search) |
                        Q(cli_tel2__icontains=search) |
                        Q(cli_adresse__icontains=search) |
                        Q(cli_nif__icontains=search) |
                        Q(cli_stat__icontains=search) |
                        Q(cli_rcs__icontains=search) |
                        Q(cli_type__icontains=search) |
                        Q(cli_modepay__icontains=search)
                    )
            queryset = queryset.order_by('cli_nom')
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return Response({
                    "status": True,
                    "message": "ok",
                    "count": self.paginator.page.paginator.count,
                    "total_pages": self.paginator.page.paginator.num_pages,
                    "current_page": self.paginator.page.number,
                    "next": self.paginator.get_next_link(),
                    "previous": self.paginator.get_previous_link(),
                    "clients": serializer.data,
                })

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": True,
                "message": "ok",
                "clients": serializer.data,
            })
        except Exception as e:
            return Response({
                "status": False,
                "message": e,
                "clients": []
            })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                cli_datecre=timezone.now(),
                cli_enabled=1
            )

            return Response({
                "status": True,
                "message": "Client créé avec succès",
                "client": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "message": "Erreur de validation",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# logOut
class LogoutView(APIView):
    def post(self, request):
        try:
            response = Response({
                "status": True,
                "message": "Deconexion reussie"
                })

            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response
        except Exception as e:
            return response({
                "status": False,
                "message": e
            })


# get last client code
@api_view(["GET"])
def generate_reference_view(request):
    table_name = request.GET.get("table_name")
    pk_field = request.GET.get("pk_field")

    print(table_name, pk_field)
    if not table_name or not pk_field:
        return Response(
            {
                "error": "Les parametres 'table_name'"
                "et 'pk_field' sont obligé"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        reference = generate_reference(table_name, pk_field)
        print(reference)
        return Response(
            {
                "reference": reference
            },
            status=status.HTTP_200_OK
        )
    except ValueError as e:
        return Response(
            {
                "error": str(e)
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
def dynamic_create_view(request):
    try:
        table_name = request.data.get("table")
        data = request.data.get("data")

        if not table_name or not data:
            return Response(
                {
                    "status": False,
                    "error": "table et data sont obligatoires"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        data.update({
            "cli_datecre": timezone.now(),
            "cli_usercre": request.user.use_login
        })
        instance = create_dynamic_instance(table_name, data)

        print("this is the data ===> ", data)
        return Response(
            {
                "status": True,
                "message": "Créé avec succès",
                "id": instance.pk
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {
                "status": False,
                "error": str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
