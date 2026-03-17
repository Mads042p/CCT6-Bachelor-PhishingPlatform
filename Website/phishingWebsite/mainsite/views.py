from django.http import HttpResponse


#Just responds "Hello World!"
def index():
    return HttpResponse("Hello, world. You're at the mainsite index.")