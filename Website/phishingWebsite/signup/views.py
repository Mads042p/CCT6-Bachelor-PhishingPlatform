from django.shortcuts import render, redirect

# Create your views here.
def signup(request):
    return render(request, 'signup/signup.html')

def goToDashboard(request):
    return redirect('dashboard:dashboard')