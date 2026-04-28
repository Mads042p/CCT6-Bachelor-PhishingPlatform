from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from sqlmanager.views import *

# Process the log-in request from the user.
def index(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print(f"Email: {email}, Password: {password}")
        # Gets the hashed version of the password using their email to look up the right password.
        dbPassword = getHashedPassword("UserData", email)
        
        #If the password match what we have stored, the user is authenticated and a session is created.
        if dbPassword[3] == password:            
            request.session['userID'] = dbPassword[0] # User ID
            request.session['name'] = dbPassword[1] # User Name
            request.session['email'] = dbPassword[2] # User Email
            request.session['company'] = dbPassword[4] # Company Name
            
            return redirect("dashboard:dashboard")
        else: 
            return render(request, 'login/loginPage.html', {'error': 'Invalid credentials'})

    return render(request, 'login/loginPage.html')

def loginSuccess(request):
    return HttpResponse("Login Success")

def logout(request):
    request.session.flush()
    return redirect('landingPage:index')
