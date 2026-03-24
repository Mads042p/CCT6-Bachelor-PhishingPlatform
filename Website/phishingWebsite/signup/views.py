from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from sqlmanager.views import *


# Create your views here.
def signup(request):
    return render(request, 'signup/signup.html')

def goToDashboard(request):
    tableName = 'UserData'

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        company = request.POST.get("company")
        isAdmin = request.POST.get("isAdmin")
        
        if isAdmin == "true":
            isAdmin = 1
        else:
            isAdmin = 0
        
        print(f"Name: {name}, Email: {email}, Password: {password}, Company: {company}, isAdmin: {isAdmin}")

        data = (name, email, password, company, isAdmin)
        InsertData(tableName, data)
        
    
        return redirect('dashboard:dashboard')
    return render(request, 'login/loginPage.html')


def companyCreation(request):
    return render(request, 'signup/companyCreation.html')

def goToDashboard(request):
    return redirect('dashboard:dashboard')

def createCompany(request):
    if request.method == "POST":
        companyName = request.POST.get("companyName")
        adminEmail = request.POST.get("adminEmail")
        companyCode = request.POST.get("companyCode")
        print(f"Company Name: {companyName}, Admin Email: {adminEmail}, companyCode: {companyCode}")
        
        # Here you would typically create the company in the database and generate a unique company code
        # For demonstration, we will just print the values and return a success message
        
        return HttpResponse(f"Company '{companyName}' created successfully with admin email '{adminEmail}'!")
    
    return goToDashboard(request)
