from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.account_login, name="account_login"),
    path("register/", views.account_register, name="account_register"),
    path("logout/", views.account_logout, name="account_logout"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="passwordreset"),
    path("reset-password/done/", views.ResetPasswordViewDone.as_view(), name="passwordresetview"),
]
