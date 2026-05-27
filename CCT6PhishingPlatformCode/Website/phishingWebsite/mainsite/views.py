from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

def index(request):
    try:
        return redirect('landingPage:index')
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}")
        return HttpResponse("An error occurred", status=500)

