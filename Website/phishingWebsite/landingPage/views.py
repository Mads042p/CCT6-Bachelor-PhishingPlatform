from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from sqlmanager.views import *



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
