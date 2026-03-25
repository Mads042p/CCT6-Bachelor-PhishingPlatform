from django.urls import path
from . import views

app_name = 'signup'

urlpatterns = [
    path('', views.signup, name='signup'),
    path('goToDashboard/', views.goToDashboard, name='goToDashboard'),
    path('companyCreation/', views.companyCreation, name='companyCreation'),
    path('createCompany/', views.createCompany, name='createCompany'),
    path('login/', views.goToDashboard, name='loginPage'),
]

