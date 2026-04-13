from django.shortcuts import render, redirect

# Create your views here.
def leaderboard(request):
    userID = request.session.get("userID")
    
    if not userID:
        return redirect('login:index')
    
    return render(request, 'leaderboard/leaderboard.html')

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