from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("goToLeaderboard/", views.goToLeaderboard, name="goToLeaderboard"),
    path("goToModules/", views.goToModules, name="goToModules"),
    path("goToAchievements/", views.goToAchievements, name="goToAchievements"),
    path("goToAdminDashboard/", views.goToAdminDashboard, name="goToAdminDashboard"),
]