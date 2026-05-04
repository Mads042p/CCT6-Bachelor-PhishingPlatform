from django.shortcuts import render
from django.shortcuts import redirect
from sqlmanager.views import *
from django.http import HttpResponseForbidden, HttpResponse
import logging

logger = logging.getLogger(__name__)

def adminDashboard(request):
    try:
        isAdmin = request.session.get("isAdmin")
        
        if not isAdmin:
            return HttpResponseForbidden("Admins only")

        company = request.session.get("company")
        
        if not company:
            logger.warning(f"Admin dashboard access without company information")
            return HttpResponse("Company information not found", status=400)

        try:
            rows = getEmployees(company)
            employees = []

            for row in rows:
                employee = {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2]
                }
                employees.append(employee)
                
        except Exception as e:
            logger.error(f"Error fetching employees for company {company}: {str(e)}")
            employees = []

        return render(request, 'adminDashboard/adminDashboard.html', {"employees": employees, "company": company})
    except Exception as e:
        logger.error(f"Error in adminDashboard view: {str(e)}")
        return HttpResponse("An error occurred while loading the admin dashboard", status=500)

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