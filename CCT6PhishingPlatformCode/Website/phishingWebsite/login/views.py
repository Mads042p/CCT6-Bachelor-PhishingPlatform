from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import JsonResponse
from sqlmanager.views import *
import logging

logger = logging.getLogger(__name__)

# Process the log-in request from the user.
def index(request):
    try:
        if request.method == "POST":
            email = (request.POST.get("email") or "").lower()
            password = request.POST.get("password")
            
            if not email or not password:
                logger.warning("Login attempt with missing email or password")
                return JsonResponse({'success': False, 'message': 'Please provide both email and password'}, status=400)
            
            try:
                # Gets the hashed version of the password using their email to look up the right password.
                dbPassword = getHashedPassword("UserData", email)
                
                if not dbPassword:
                    logger.warning(f"Login attempt with non-existent email: {email}")
                    return JsonResponse({'success': False, 'message': 'Incorrect email or password'}, status=400)
                
                #If the password match what we have stored, the user is authenticated and a session is created.
                if dbPassword[3] == password:            
                    request.session['userID'] = dbPassword[0] # User ID
                    request.session['name'] = dbPassword[1] # User Name
                    request.session['email'] = dbPassword[2] # User Email
                    request.session['company'] = dbPassword[4] # Company Name
                    request.session['isAdmin'] = dbPassword[5] # isAdmin
                    logger.info(f"User {email} logged in successfully")
                    return redirect("dashboard:dashboard")
                else: 
                    logger.warning(f"Failed login attempt for user {email}")
                    return JsonResponse({'success': False, 'message': 'Incorrect email or password'}, status=400)
            except IndexError:
                logger.error(f"Database returned incomplete user data for email {email}")
                return JsonResponse({'success': False, 'message': 'An error occurred during login'}, status=500)
            except Exception as e:
                logger.error(f"Error retrieving user data for {email}: {str(e)}")
                return JsonResponse({'success': False, 'message': 'An error occurred during login'}, status=500)

        return render(request, 'login/loginPage.html')
    except Exception as e:
        logger.error(f"Unexpected error in login view: {str(e)}")
        return JsonResponse({'success': False, 'message': 'An unexpected error occurred'}, status=500)

def loginSuccess(request):
    try:
        return HttpResponse("Login Success")
    except Exception as e:
        logger.error(f"Error in loginSuccess: {str(e)}")
        return HttpResponse("An error occurred", status=500)

def logout(request):
    try:
        request.session.flush()
        logger.info(f"User session flushed")
        return redirect('landingPage:index')
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return HttpResponse("An error occurred during logout", status=500)
