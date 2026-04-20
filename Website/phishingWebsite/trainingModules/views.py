from django.shortcuts import render, redirect
from sqlmanager.views import *

# Create your views here.
def trainingModules(request):
    userID = request.session.get("userID")
    
    if not userID:
        return redirect('login:index')
    
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
    quizData = getQuiz("Module1")
    print(quizData)
    return render(request, 'trainingModules/phishingExplained.html', {"quizData": quizData})