from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def index (request):
    return HttpResponse('<H1> hello all</h1>')

def clients(request):
    return render(request, 'projManagement/clients.html')
def home(request):
    return render(request,'projManagement/home.html')
def missions(request):
    return render(request,'projManagement/missions.html')