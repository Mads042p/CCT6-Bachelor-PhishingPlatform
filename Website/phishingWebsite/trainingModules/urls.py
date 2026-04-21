from django.urls import path
from . import views

app_name = 'trainingModules'

urlpatterns = [
    path('', views.trainingModules, name='trainingModules'),
    path('goToDashboard/', views.goToDashboard, name='goToDashboard'),
    path("goToLeaderboard/", views.goToLeaderboard, name="goToLeaderboard"),
    path("goToModules/", views.goToModules, name="goToModules"),
    path("goToAchievements/", views.goToAchievements, name="goToAchievements"),
    path("goToAdminDashboard/", views.goToAdminDashboard, name="goToAdminDashboard"),
    path("phishingExplained/", views.phishingExplained, name="phishingExplained"),
    path("updateUserScore/", views.updateUserScore, name="updateUserScore"),
]