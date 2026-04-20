from django.shortcuts import render
from django.shortcuts import redirect
from sqlmanager.views import *

def adminDashboard(request):
    userID = request.session.get("userID")
    
    if not userID:
        return redirect('login:index')
    # Hard-coded company
    company = request.session.get("company")

    rows = getEmployees(company)
    employees = []

    for row in rows:
        employee = {
            "id": row[0],
            "name": row[1],
            "email": row[2]
        }
        employees.append(employee)

    return render(request, 'adminDashboard/adminDashboard.html', {"employees": employees, "company": company})

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