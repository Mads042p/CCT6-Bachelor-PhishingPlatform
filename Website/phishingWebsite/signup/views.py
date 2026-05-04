from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from sqlmanager.views import *
import logging

logger = logging.getLogger(__name__)

def signup(request):
    try:
        return render(request, 'signup/signup.html')
    except Exception as e:
        logger.error(f"Error in signup view: {str(e)}")
        return HttpResponse("An error occurred while loading the signup page", status=500)

# Receives the userdata from the front-end, and posts them into the database
# using the insertUserData function from the SQL-manager.
def goToDashboard(request):
    try:
        tableName = 'UserData'

        if request.method == "POST":
            name = request.POST.get("name")
            email = request.POST.get("email")
            password = request.POST.get("password")
            companyCode = request.POST.get("company")

            # Validate required fields
            if not name or not email or not password:
                return render(request, 'signup/signup.html', {'error': 'Please fill in all required fields'})
            
            try:
                company = getCompany(companyCode)
                
                if not company:
                    logger.warning(f"Signup attempt with invalid company code: {companyCode}")
                    return render(request, 'signup/signup.html', {'error': 'Invalid company code'})
                
                data = {
                    "name": name, 
                    "email": email, 
                    "password": password, 
                    "company": company
                    }
                
                insertUserData(tableName, data)
                return redirect('login:index')
            except Exception as e:
                logger.error(f"Error during signup for email {email}: {str(e)}")
                return render(request, 'signup/signup.html', {'error': 'An error occurred during signup. Please try again.'})
        
        return render(request, 'signup/signup.html')
    except Exception as e:
        logger.error(f"Unexpected error in goToDashboard (signup): {str(e)}")
        return HttpResponse("An error occurred during signup", status=500)

# Renderes the companycreation page, if the button is clicked.
def companyCreation(request):
    try:
        return render(request, 'signup/companyCreation.html')
    except Exception as e:
        logger.error(f"Error in companyCreation view: {str(e)}")
        return HttpResponse("An error occurred while loading the company creation page", status=500)

# Creates the company in the database and inserts the company information into the db.
def createCompany(request):
    try:
        if request.method == "POST":
            companyName = request.POST.get("companyName")
            encryptedEmail = request.POST.get("encryptedEmail")
            companyCode = request.POST.get("companyCode")
            iv = request.POST.get("iv")
            CVRNumber = request.POST.get("CVRNumber")
            
            # Validate required fields
            if not companyName or not encryptedEmail or not companyCode or not CVRNumber:
                logger.warning("Company creation attempt with missing required fields")
                return render(request, 'signup/companyCreation.html', {'error': 'Please fill in all required fields'})
            
            try:
                insertData("CompanyTable", {
                    "CompanyName": companyName,
                    "AdminEmail": encryptedEmail,
                    "CompanyCode": companyCode,
                    "CVRNumber": CVRNumber,
                    "IV": iv
                })
                logger.info(f"New company created: {companyName} with code {companyCode}")
                return redirect('signup:signup')
            except Exception as e:
                logger.error(f"Error inserting company data for {companyName}: {str(e)}")
                return render(request, 'signup/companyCreation.html', {'error': 'An error occurred while creating the company. Please try again.'})

        return render(request, 'signup/companyCreation.html')
    except Exception as e:
        logger.error(f"Unexpected error in createCompany: {str(e)}")
        return HttpResponse("An error occurred during company creation", status=500)
