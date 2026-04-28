import json

from django.shortcuts import render, redirect
from sqlmanager.views import getUserCompanyScores

def leaderboard(request):
    # Get the user ID from the session
    userID = request.session.get("userID")
    
    # If the user is not logged in, redirect to login page
    if not userID:
        return redirect('login:index')

    leaderboard_data = [
        {"name": "Leaderboard", "points": 500},
        {"name": "Does", "points": 400},
        {"name": "Not", "points": 300},
        {"name": "Work", "points": 200},
        {"name": "!!!", "points": 100},
    ]
    
    # Fetch actual leaderboard data for the user's company using their email
    leaderboard_data = getUserCompanyScores(request.session.get("email"))

    leaderboard_data = sorted(leaderboard_data, key=lambda entry: entry["points"], reverse=True)


    return render(
        request,
        'leaderboard/leaderboard.html',
        {
            "leaderboard_data_json": json.dumps(leaderboard_data),
        },
    )

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