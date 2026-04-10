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
        
        dbPassword = getHashedPassword(tableName, email)
        #element 0 is the userID, element 1 is the hashed password
        if dbPassword[1] == password:
            
            request.session['userID'] = dbPassword[0]
            
            return redirect("dashboard:dashboard")
        else: 
            return render(request, 'login/loginPage.html', {'error': 'Invalid credentials'})

    return render(request, 'login/loginPage.html')

def loginSuccess(request):
    return HttpResponse("Login Success")

