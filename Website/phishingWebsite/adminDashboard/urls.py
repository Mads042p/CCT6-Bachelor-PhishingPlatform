from django.urls import path
from . import views

app_name = 'adminDashboard'

urlpatterns = [
    path('', views.adminDashboard, name='adminDashboard'),
    path('goToDashboard/', views.goToDashboard, name='goToDashboard'),
]