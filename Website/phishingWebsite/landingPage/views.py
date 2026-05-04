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

def sendEmail(request):
    try:
        subject = "Phishing Email from python"
        body = "This is a phishing email sent from a python script."
        sender = "lkmklm@gmail.com"
        to = "tobias.steenberg@outlook.dk"
        password = "wbkz tlhu wqzg ekxq"

        em = EmailMessage()
        em['From'] = sender
        em['To'] = to
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(sender, password)
                smtp.sendmail(sender, to, em.as_string())
            logger.info(f"Email sent successfully to {to}")
        except smtplib.SMTPAuthenticationError:
            logger.error(f"SMTP authentication failed for sender {sender}")
            return HttpResponse("Email authentication failed", status=500)
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending email: {str(e)}")
            return HttpResponse("Error sending email", status=500)
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return HttpResponse("Error sending email", status=500)
            
        return redirect('/')
    except Exception as e:
        logger.error(f"Unexpected error in sendEmail: {str(e)}")
        return HttpResponse("An unexpected error occurred", status=500)

