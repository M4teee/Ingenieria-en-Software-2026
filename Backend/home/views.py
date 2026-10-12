from django.shortcuts import render

# Create your views here.

def rootHandler(req):
  return render(req, 'home.html', {})