from django.shortcuts import render, redirect
from sqlmanager.views import *
from datetime import datetime
from django.http import JsonResponse
from django.http import HttpResponse
import json
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def trainingModules(request):
    try:
        userID = request.session.get("userID")
        
        if not userID:
            return redirect('login:index')
        
        return render(request, 'trainingModules/trainingModules.html')
    except Exception as e:
        logger.error(f"Error in trainingModules view: {str(e)}")
        return HttpResponse("An error occurred while loading training modules", status=500)


def goToDashboard(request):
    try:
        return redirect('dashboard:dashboard')
    except Exception as e:
        logger.error(f"Error redirecting to dashboard: {str(e)}")
        return HttpResponse("An error occurred", status=500)

def goToAdminDashboard(request):
    try:
        return redirect('adminDashboard:adminDashboard')
    except Exception as e:
        logger.error(f"Error redirecting to admin dashboard: {str(e)}")
        return HttpResponse("An error occurred", status=500)

def goToLeaderboard(request):
    try:
        return redirect('leaderboard:leaderboard')
    except Exception as e:
        logger.error(f"Error redirecting to leaderboard: {str(e)}")
        return HttpResponse("An error occurred", status=500)
   
def goToModules(request):
    try:
        return redirect('trainingModules:trainingModules')
    except Exception as e:
        logger.error(f"Error redirecting to modules: {str(e)}")
        return HttpResponse("An error occurred", status=500)
    
def goToAchievements(request):
    try:
        return redirect('achievements:achievements')
    except Exception as e:
        logger.error(f"Error redirecting to achievements: {str(e)}")
        return HttpResponse("An error occurred", status=500)

def phishingExplained(request):
    try:
        quizID = "Module1"
        try:
            quizData = getQuiz(quizID)
        except Exception as e:
            logger.error(f"Error fetching quiz data for {quizID}: {str(e)}")
            quizData = {}

        return render(request, 'trainingModules/phishingExplained.html', {"quizData": quizData})
    except Exception as e:
        logger.error(f"Error in phishingExplained view: {str(e)}")
        return HttpResponse("An error occurred while loading phishing module", status=500)

def emailTraining(request):
    try:
        return render(request, 'trainingModules/emailTraining.html')
    except Exception as e:
        logger.error(f"Error in emailTraining view: {str(e)}")
        return HttpResponse("An error occurred while loading email training", status=500)

def staticTraining(request):
    try:
        return render(request, 'trainingModules/staticTraining.html')
    except Exception as e:
        logger.error(f"Error in staticTraining view: {str(e)}")
        return HttpResponse("An error occurred while loading static training", status=500)

def updateUserScore(request):
    '''
    Receives a POST with JSON payload: "quizID", "score", "total"
    '''
    try:
        if request.method == "POST":
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in updateUserScore request: {str(e)}")
                return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

            quizID = data.get("quizID")
            score = data.get("score")
            total = data.get("total")
            userID = request.session.get("userID")
            
            if not quizID or score is None or total is None or not userID:
                logger.warning(f"Missing required parameters in updateUserScore")
                return JsonResponse({"status": "error", "message": "Missing required parameters"}, status=400)
            
            try:
                # Calculate score to put in database, from 0 to 100
                if total == 0:
                    logger.warning(f"Total score is 0 for quiz {quizID}")
                    return JsonResponse({"status": "error", "message": "Invalid total score"}, status=400)
                    
                score = int(score/total * 100)

                previousScore = getScore(userID, quizID)
                
                # Either insert score into database if the quiz was completed for the first time, or update the score
                if not previousScore:
                    upsertScore(userID, quizID, score, datetime.now().strftime("%d-%m-%Y %H:%M"))
                elif score > previousScore:
                    upsertScore(userID, quizID, score, datetime.now().strftime("%d-%m-%Y %H:%M"))
            except Exception as e:
                logger.error(f"Error updating user score for user {userID}, quiz {quizID}: {str(e)}")
                return JsonResponse({"status": "error", "message": "Error updating score"}, status=500)
        
        return JsonResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Unexpected error in updateUserScore: {str(e)}")
        return JsonResponse({"status": "error", "message": "An unexpected error occurred"}, status=500)