from django.urls import path
from . import views

app_name = 'trainingModules'

urlpatterns = [
    path('', views.trainingModules, name='trainingModules'),
    path('goToDashboard/', views.goToDashboard, name='goToDashboard'),
]