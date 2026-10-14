from django.shortcuts import render

# Create your views here.
def form(req):
  return render(req, 'clienteFinal/index.html', {})