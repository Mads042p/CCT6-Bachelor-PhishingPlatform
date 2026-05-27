from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from sqlmanager.views import *

import smtplib
import ssl
from email.message import EmailMessage
import logging

logger = logging.getLogger(__name__)

def index(request):
    try:
        return render(request, 'landingPage/index.html')
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}")
        return HttpResponse("An error occurred while loading the page", status=500)

def about(request):
    try:
        return render(request, 'landingPage/about.html')
    except Exception as e:
        logger.error(f"Error in about view: {str(e)}")
        return HttpResponse("An error occurred while loading the about page", status=500)

def newsletter(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            if email:
                try:
                    insertData('NewsletterEmails', {'email': email})
                except Exception as e:
                    logger.error(f"Error inserting newsletter email {email}: {str(e)}")
                    # Continue and redirect anyway
        return redirect('/')
    except Exception as e:
        logger.error(f"Error in newsletter view: {str(e)}")
        return redirect('/')



