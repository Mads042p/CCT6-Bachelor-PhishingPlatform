from django.shortcuts import render, redirect
from sqlmanager.views import *
from datetime import datetime
from django.http import JsonResponse

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
    quizID = "Module1"
    quizData = getQuiz(quizID)
    print(quizData)

    return render(request, 'trainingModules/phishingExplained.html', {"quizData": quizData})

def emailTraining(request):
    return render(request, 'trainingmodules/emailTraining.html')

def updateUserScore(request):
    '''
    Receives a POST with JSON payload: "quizID", "score", "total"
    '''
    if request.method == "POST":
        data = json.loads(request.body)

        quizID = data.get("quizID")
        score = data.get("score")
        total = data.get("total")
        userID = request.session.get("userID")
        
        # Calculate score to put in database, from 0 to 100
        score = int(score/total * 100)

        previousScore = getScore(userID, quizID)
        
        # Either insert score into database if the quiz was completed for the first time, or update the score
        if not previousScore:
            upsertScore(userID, quizID, score, datetime.now().strftime("%d-%m-%Y %H:%M"))

        if score > previousScore:
            upsertScore(userID, quizID, score, datetime.now().strftime("%d-%m-%Y %H:%M"))
    
    return JsonResponse({"status": "ok"})