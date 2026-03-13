from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

def index(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(f"Username: {username}, Password: {password}")
        return redirect("loginSuccess")

    return render(request, 'login/loginPage.html')

def loginSuccess(request):
    return HttpResponse("Login Success")