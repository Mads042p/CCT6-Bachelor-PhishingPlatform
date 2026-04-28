from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from sqlmanager.views import *

def achievements(request):
    # Get User ID from session cookie
    userID = request.session.get("userID")
    assignAchievements(userID)
    
    if not userID:
        return redirect('login:index')

    # All Achievements
    rows = GetData("Achievements")
    achievements = []

    for row in rows:
        achievement = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "completed": False
        }
        achievements.append(achievement)

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
    
    for achievement in achievements:
        if achievement["id"] in completedAchievements:
            achievement["completed"] = True
    
    return render(request, 'achievements/achievements.html', {"achievements": achievements})

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