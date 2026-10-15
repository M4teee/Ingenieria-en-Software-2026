# main/repartidor/views.py

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Repartidor


def login_pin(req):
    if req.method == 'POST':
        pin = req.POST.get('pin', '').strip()
        repartidor = Repartidor.objects.filter(pin=pin).first() if pin else None
        if repartidor is None:
            return render(req, 'repartidor/login_pin.html', {
                'error': 'PIN inválido. Verificá el código e intentá de nuevo.',
            })
        login(req, repartidor.user)
        return redirect('repartidor')
    return render(req, 'repartidor/login_pin.html', {})


@login_required(login_url='repartidor_login_pin')
def home(req):
    if req.user.is_superuser:
        return redirect('admin:index')

    repartidor = Repartidor.objects.filter(user=req.user).first()
    if repartidor is None:
        return render(req, 'repartidor/index.html', {
            'sin_perfil': True,
        })

    return render(req, 'repartidor/index.html', {
        'disponible': repartidor.disponible,
    })


@login_required(login_url='repartidor_login_pin')
@require_POST
def toggle_disponibilidad(req):
    repartidor = Repartidor.objects.filter(user=req.user).first()
    if repartidor is None:
        messages.error(req, 'No se encontró tu perfil de repartidor.')
        return redirect('repartidor')

    repartidor.disponible = not repartidor.disponible
    repartidor.save(update_fields=['disponible'])

    if repartidor.disponible:
        messages.success(req, 'Ahora estás Disponible.')
    else:
        messages.success(req, 'Ahora estás No disponible.')

    return redirect('repartidor')
