from django.shortcuts import render, redirect

# Create your views here.
def leaderboard(request):
    return render(request, 'leaderboard/leaderboard.html')

def goToDashboard(request):
    return redirect('dashboard:dashboard')