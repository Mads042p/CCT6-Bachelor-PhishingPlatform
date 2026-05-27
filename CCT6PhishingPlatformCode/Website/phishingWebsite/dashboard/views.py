from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from sqlmanager.views import *
import logging
import random

logger = logging.getLogger(__name__)

def dashboard(request):
    try:
        userID = request.session.get("userID")
        
        if not userID:
            return redirect('login:index')
        
        rows = GetData("Achievements")
        achievements_list = []
        for row in rows:
            achievement = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "completed": False
                }
            achievements_list.append(achievement)
            
        # User's Achievements
        rows = getUserAchievements(userID)
        userAchievements = []

        for row in rows:
            userAchievement = {
                "id": row[0],
                "name": row[1],
                "description": row[2]
            }
            userAchievements.append(userAchievement)
        
        completedAchievements = []
        for row in rows:
            completedAchievements.append(row[0])

        for achievement in achievements_list:
            if achievement["id"] in completedAchievements:
                achievement["completed"] = True
        
        notCompleatedAch = [x for x in achievements_list if x["completed"] == False]
        
        ranNotAch = random.choice(notCompleatedAch)

        return render(request, 'dashboard/dashboard.html', {"ranNotAch": ranNotAch})
    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}")
        return HttpResponse("An error occurred while loading the dashboard", status=500)

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