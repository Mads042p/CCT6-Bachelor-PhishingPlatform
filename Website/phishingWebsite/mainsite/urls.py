from django.contrib import admin
from django.urls import include, path
from . import views

app_name = 'mainsite'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('', views.index, name='index'),
    path('achievements/', include('achievements.urls')),
    path('adminDashboard/', include('adminDashboard.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('leaderboard/', include('leaderboard.urls')),
    path('signup/', include('signup.urls')),
    path('trainingModules/', include('trainingModules.urls')),
]
