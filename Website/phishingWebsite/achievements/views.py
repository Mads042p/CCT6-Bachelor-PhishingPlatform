from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

def achievements(request):
    return render(request, 'achievements/achievements.html')

def goToDashboard(request):
    return redirect('dashboard:dashboard')