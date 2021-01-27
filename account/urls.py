from django.urls import path
from django.contrib.auth import logout
from . import views


urlpatterns = [
    path("my_account/", views.my_account, name="my_account"),
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path("my_favorites/", views.my_favorites, name="my_favorites"),
    path("save/", views.save, name="save"),
    path("mail_save/", views.mail_save, name="mail_save"),
    path("delete/", views.delete, name="delete"),
]

app_name = "account"
