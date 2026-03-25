from django.shortcuts import render, redirect

# Create your views here.
def trainingModules(request):
    return render(request, 'trainingModules/trainingModules.html')


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

def phishingExplained(request):
    return render(request, 'trainingModules/phishingExplained.html')