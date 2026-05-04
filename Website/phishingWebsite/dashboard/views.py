from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

def dashboard(request):
    try:
        userID = request.session.get("userID")
        
        if not userID:
            return redirect('login:index')

        return render(request, 'dashboard/dashboard.html')
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