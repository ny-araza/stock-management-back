from django.urls import path

from polls.accounts.views import (
    CreateUserView,
    CsrfView,
    LoginView,
    LogoutView,
    MeView,
    UpdateLotView,
    UpdateUserView,
)

urlpatterns = [
    path("api/csrf/", CsrfView.as_view(), name="csrf"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/me/", MeView.as_view(), name="me"),
    path("api/user/create/", CreateUserView.as_view(), name="create-user"),
    path("api/user/update/<int:user_id>", UpdateUserView.as_view(), name="update-user"),
    path("api/lot/update/<int:lot_id>", UpdateLotView.as_view(), name="update-lot"),
]
