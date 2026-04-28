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
        companyCode = request.POST.get("company")

        company = getCompany(companyCode)
        
        
        print(f"Name: {name}, Email: {email}, Password: {password}, Company: {company}")

        data = {
            "name": name, 
            "email": email, 
            "password": password, 
            "company": company
            }
        
        print("type is: ", type(data))
        insertUserData(tableName, data)
        
    
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
