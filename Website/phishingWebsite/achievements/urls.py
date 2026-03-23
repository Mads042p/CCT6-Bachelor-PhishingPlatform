from django.urls import path
from . import views

app_name = 'achievements'

urlpatterns = [
    path('', views.achievements, name='achievements'),
    path('goToDashboard/', views.goToDashboard, name='goToDashboard'),
    path("goToLeaderboard/", views.goToLeaderboard, name="goToLeaderboard"),
    path("goToModules/", views.goToModules, name="goToModules"),
    path("goToAchievements/", views.goToAchievements, name="goToAchievements"),
    path("goToAdminDashboard/", views.goToAdminDashboard, name="goToAdminDashboard"),
]