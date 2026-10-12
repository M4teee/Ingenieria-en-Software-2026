from django.shortcuts import render

# Create your views here.
def hola(req):
  return render(req, 'hola.html', {})