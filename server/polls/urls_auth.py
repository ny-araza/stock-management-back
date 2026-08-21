from django.urls import path

from polls.accounts.views import CsrfView, LoginView, LogoutView, MeView, CreateUserView

urlpatterns = [
    path("api/csrf/", CsrfView.as_view(), name="csrf"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/me/", MeView.as_view(), name="me"),
    path("api/user/create/", CreateUserView.as_view(), name="create-user"),
]
