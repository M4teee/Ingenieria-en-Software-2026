# main/repartidor/views.py

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import HistorialPedido, Pedido, RepartidorPerfil, ESTADOS_PEDIDO

LIMITE_SEGUNDOS = Pedido.LIMITE_ACEPTACION_SEGUNDOS

def _nombre_repartidor(user):
    return user.get_full_name() or user.username

def _expirado(pedido):
    return (pedido.fecha_hora_asignacion is None or
            timezone.now() - pedido.fecha_hora_asignacion >= timedelta(seconds=LIMITE_SEGUNDOS))

@login_required
def home(req):
    if req.user.is_superuser:
        return redirect('admin:index')

    perfil, _ = RepartidorPerfil.objects.get_or_create(user=req.user)

    # Expiración perezosa: si la asignación superó los 5 minutos sin respuesta,
    # libera el pedido y marca al repartidor como no disponible (Escenario 3).
    asignado = (Pedido.objects.filter(repartidor=req.user, estado='asignado')
                          .order_by('fecha_hora_asignacion').first())
    expirado = False
    if asignado and _expirado(asignado):
        with transaction.atomic():
            pedido = (Pedido.objects.select_for_update()
                      .filter(pk=asignado.pk, estado='asignado').first())
            if pedido and _expirado(pedido):
                pedido.repartidor = None
                pedido.fecha_hora_asignacion = None
                pedido.estado = 'registrado'
                pedido.save()
                HistorialPedido.objects.create(
                    pedido=pedido,
                    descripcion=(f'Desasignado por expiración del tiempo de espera '
                                 f'({LIMITE_SEGUNDOS // 60} minutos)'),
                )
                perfil.disponible = False
                perfil.save()
        expirado = True
        asignado = None

    segundos_restantes = None
    if asignado:
        transcurridos = (timezone.now() - asignado.fecha_hora_asignacion).total_seconds()
        segundos_restantes = max(0, int(LIMITE_SEGUNDOS - transcurridos))

    contexto = {
        'asignado': asignado,
        'segundos_restantes': segundos_restantes,
        'disponible': perfil.disponible,
        'expirado': expirado,
        'estados': dict(ESTADOS_PEDIDO),
    }
    return render(req, 'repartidor/index.html', contexto)

@login_required
@require_POST
def aceptar(req, pedido_id):
    with transaction.atomic():
        pedido = (Pedido.objects.select_for_update()
                  .filter(pk=pedido_id, repartidor=req.user, estado='asignado')
                  .first())
        if pedido is None:
            return HttpResponseBadRequest('El pedido no está asignado a este repartidor.')
        if _expirado(pedido):
            # Se agotaron los 5 minutos: liberar el pedido (Escenario 3).
            pedido.repartidor = None
            pedido.fecha_hora_asignacion = None
            pedido.estado = 'registrado'
            pedido.save()
            HistorialPedido.objects.create(
                pedido=pedido,
                descripcion=(f'Desasignado por expiración del tiempo de espera '
                             f'({LIMITE_SEGUNDOS // 60} minutos)'),
            )
            perfil, _ = RepartidorPerfil.objects.get_or_create(user=req.user)
            perfil.disponible = False
            perfil.save()
            return redirect('repartidor')

        pedido.estado = 'retirado'
        pedido.fecha_hora_asignacion = None
        pedido.save()
        HistorialPedido.objects.create(
            pedido=pedido,
            descripcion=f'Aceptado por repartidor {_nombre_repartidor(req.user)}',
        )
    return redirect('repartidor')

@login_required
@require_POST
def rechazar(req, pedido_id):
    with transaction.atomic():
        pedido = (Pedido.objects.select_for_update()
                  .filter(pk=pedido_id, repartidor=req.user, estado='asignado')
                  .first())
        if pedido is None:
            return HttpResponseBadRequest('El pedido no está asignado a este repartidor.')

        if _expirado(pedido):
            descripcion = (f'Desasignado por expiración del tiempo de espera '
                           f'({LIMITE_SEGUNDOS // 60} minutos)')
        else:
            pedido.fecha_hora_asignacion = None
            descripcion = f'Rechazado por repartidor {_nombre_repartidor(req.user)}'
        pedido.repartidor = None
        pedido.estado = 'registrado'
        pedido.save()
        HistorialPedido.objects.create(pedido=pedido, descripcion=descripcion)

        perfil, _ = RepartidorPerfil.objects.get_or_create(user=req.user)
        perfil.disponible = False
        perfil.save()
    return redirect('repartidor')
