from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from sqlmanager.views import *
import logging

logger = logging.getLogger(__name__)

def achievements(request):
    try:
        # Get User ID from session cookie
        userID = request.session.get("userID")
        
        if not userID:
            return redirect('login:index')
        
        try:
            assignAchievements(userID)
        except Exception as e:
            logger.error(f"Error assigning achievements for user {userID}: {str(e)}")
            # Continues without achievemnents, empty page

        # All Achievements
        try:
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
        except Exception as e:
            logger.error(f"Error fetching achievements: {str(e)}")
            achievements_list = []
    
    except Exception as e:
        logger.error(f"Error in achievements view: {str(e)}")
        return HttpResponse("An error occurred while loading achievements", status=500)

    try:     
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
    except Exception as e:
        logger.error(f"Error fetching user achievements for user {userID}: {str(e)}")
        userAchievements = []

    try:
        completedAchievements = []
        for row in rows:
            completedAchievements.append(row[0])

        for achievement in achievements_list:
            if achievement["id"] in completedAchievements:
                achievement["completed"] = True
    except Exception as e:
        logger.error(f"Error marking completed achievements for user {userID}: {str(e)}")
    
    try:
        return render(request, 'achievements/achievements.html', {"achievements": achievements_list})
    except Exception as e:
        logger.error(f"Error rendering achievements page for user {userID}: {str(e)}")
        return HttpResponse("An error occurred while loading achievements", status=500)

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

def assignAchievements(userID):
    achTrainingComplete(userID)
    achAPlusStudent(userID)
    achTheGameIsAfoot(userID)
    achMaster(userID)