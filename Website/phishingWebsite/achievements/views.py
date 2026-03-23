from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

def achievements(request):
    return render(request, 'achievements/achievements.html')

def goToDashboard(request):
    return redirect('dashboard:dashboard')

def goToAdminDashboard(request):
    return redirect('adminDashboard:adminDashboard')

def goToLeaderboard(request):
    return redirect('leaderboard:leaderboard')
   
def goToModules(request):
    return redirect('trainingModules:trainingModules')
    
def goToAchievements(request):
    return redirect('achievements:achievements')