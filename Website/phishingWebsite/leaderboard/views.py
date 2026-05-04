import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from sqlmanager.views import getUserCompanyScores
import logging

logger = logging.getLogger(__name__)

def leaderboard(request):
    try:
        # Get the user ID from the session
        userID = request.session.get("userID")
        
        # If the user is not logged in, redirect to login page
        if not userID:
            return redirect('login:index')

        email = request.session.get("email")
        
        if not email:
            logger.warning(f"Leaderboard access without email in session")
            return HttpResponse("User email not found in session", status=400)
        
        leaderboard_data = []
        try:
            # Fetch actual leaderboard data for the user's company using their email
            leaderboard_data = getUserCompanyScores(email)
        except Exception as e:
            logger.error(f"Error fetching leaderboard data for user {email}: {str(e)}")
            leaderboard_data = []

        if leaderboard_data:
            try:
                leaderboard_data = sorted(leaderboard_data, key=lambda entry: entry.get("points", 0), reverse=True)
            except Exception as e:
                logger.error(f"Error sorting leaderboard data: {str(e)}")
        
        try:
            leaderboard_json = json.dumps(leaderboard_data)
        except Exception as e:
            logger.error(f"Error converting leaderboard data to JSON: {str(e)}")
            leaderboard_json = json.dumps([])

        return render(
            request,
            'leaderboard/leaderboard.html',
            {
                "leaderboard_data_json": leaderboard_json,
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error in leaderboard view: {str(e)}")
        return HttpResponse("An error occurred while loading the leaderboard", status=500)

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