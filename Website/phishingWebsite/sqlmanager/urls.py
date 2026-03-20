from django.urls import path
from . import views

app_name = 'sqlmanager'

urlpatterns = [
    path('', views.index, name='index'),
    path(views.getHashedPassword, name='getHashedPassword'),
]