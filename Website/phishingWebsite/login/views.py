from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from sqlmanager.views import *

tableName = "UserData"

def index(request):
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print(f"Email: {email}, Password: {password}")
        
        print(getHashedPassword(tableName, email))
        
        return redirect("login:loginSuccess")

    return render(request, 'login/loginPage.html')

def loginSuccess(request):
    return HttpResponse("Login Success")

