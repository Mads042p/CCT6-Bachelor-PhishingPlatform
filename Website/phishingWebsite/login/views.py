from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from sqlmanager.views import *

def index(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print(f"Email: {email}, Password: {password}")
                
        dbPassword = getHashedPassword("UserData", email)
        
        if dbPassword[3] == password:            
            request.session['userID'] = dbPassword[0] # User ID
            request.session['name'] = dbPassword[1] # User Name
            request.session['email'] = dbPassword[2] # User Email
            request.session['company'] = dbPassword[4] # Company Name
            request.session['isAdmin'] = dbPassword[5] # isAdmin
            
            return redirect("dashboard:dashboard")
        else: 
            return render(request, 'login/loginPage.html', {'error': 'Invalid credentials'})

    return render(request, 'login/loginPage.html')

def loginSuccess(request):
    return HttpResponse("Login Success")

def logout(request):
    request.session.flush()
    return redirect('landingPage:index')
