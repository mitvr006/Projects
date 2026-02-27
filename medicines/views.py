from django.http import HttpResponse

def home(request):
    return HttpResponse("Medical Management System Running Successfully")
