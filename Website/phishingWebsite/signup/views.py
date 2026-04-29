from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from sqlmanager.views import *


def signup(request):
    return render(request, 'signup/signup.html')

# Receives the userdata from the front-end, and posts them into the database
# using the insertUserData function from the SQL-manager.
def goToDashboard(request):
    tableName = 'UserData'

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        companyCode = request.POST.get("company")

        company = getCompany(companyCode)
        
        
        data = {
            "name": name, 
            "email": email, 
            "password": password, 
            "company": company
            }
        
        insertUserData(tableName, data)
        
    
        return redirect('login:index')
    return render(request, 'login/loginPage.html')

# Renderes the companycreation page, if the button is clicked.
def companyCreation(request):
    return render(request, 'signup/companyCreation.html')

# Creates the company in the database and inserts the company information into the db.
def createCompany(request):
    if request.method == "POST":
        companyName = request.POST.get("companyName")
        encryptedEmail = request.POST.get("encryptedEmail")
        companyCode = request.POST.get("companyCode")
        iv = request.POST.get("iv")
        CVRNumber = request.POST.get("CVRNumber")
        
        insertData("CompanyTable", {
            "CompanyName": companyName,
            "AdminEmail": encryptedEmail,
            "CompanyCode": companyCode,
            "CVRNumber": CVRNumber,
            "IV": iv
        })
        # Here you would typically create the company in the database and generate a unique company code
        # For demonstration, we will just print the values and return a success message
        
        return redirect('signup:signup')

    return render(request, 'signup/companyCreation.html')
