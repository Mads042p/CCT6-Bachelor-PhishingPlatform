from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from sqlmanager.views import *

import smtplib
import ssl
from email.message import EmailMessage

def index(request):
    return render(request, 'landingPage/index.html')

def about(request):
    return render(request, 'landingPage/about.html')

def newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            insertData('NewsletterEmails', {'email': email})
        return redirect('/')
    return redirect('/')

def sendEmail(request):
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

    conttext = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=conttext) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, to, em.as_string())
    return redirect('/')

