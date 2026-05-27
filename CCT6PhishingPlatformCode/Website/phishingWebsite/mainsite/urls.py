from django.contrib import admin
from django.urls import include, path
from . import views

app_name = 'mainsite'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('achievements/', include('achievements.urls')),
    path('adminDashboard/', include('adminDashboard.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('leaderboard/', include('leaderboard.urls')),
    path('signup/', include('signup.urls')),
    path('trainingModules/', include('trainingModules.urls')),
    path('landingPage/', include('landingPage.urls')),
]
