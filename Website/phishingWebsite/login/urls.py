from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path("", views.index, name="index"),
    path("loginSuccess/", views.loginSuccess, name="loginSuccess"),
    path("logout/", views.logout, name="logout"),
]