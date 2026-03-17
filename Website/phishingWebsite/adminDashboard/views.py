from django.shortcuts import render
from django.shortcuts import redirect

def adminDashboard(request):
    return render(request, 'adminDashboard/adminDashboard.html')

def goToDashboard(request):
    return redirect('dashboard:dashboard')