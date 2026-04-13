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

        data = {
            "name": name, 
            "email": email, 
            "password": password, 
            "company": company, 
            "isAdmin": isAdmin
            }
        
        print("type is: ", type(data))
        insertData(tableName, data)
        
    
        return redirect('login:index')
    return render(request, 'login/loginPage.html')


def companyCreation(request):
    return render(request, 'signup/companyCreation.html')

def createCompany(request):
    if request.method == "POST":
        companyName = request.POST.get("companyName")
        encryptedEmail = request.POST.get("encryptedEmail")
        companyCode = request.POST.get("companyCode")
        iv = request.POST.get("iv")
        CVRNumber = request.POST.get("CVRNumber")
        print(f"Company Name: {companyName}, Encrypted Email: {encryptedEmail}, companyCode: {companyCode}, IV: {iv}")
        
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
