# main/repartidor/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def home(req):
  if (req.user.is_superuser):
    return redirect('admin:index')
  else:
    return render(req, 'repartidor/index.html', {})