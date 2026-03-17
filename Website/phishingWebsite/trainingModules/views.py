from django.shortcuts import render, redirect

# Create your views here.
def trainingModules(request):
    return render(request, 'trainingModules/trainingModules.html')


def goToDashboard(request):
    return redirect('dashboard:dashboard')