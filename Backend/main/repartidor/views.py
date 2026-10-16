# main/repartidor/views.py

from datetime import timedelta
from io import BytesIO

from PIL import Image

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import HistorialEstado, Pedido, Repartidor


def _expirado(pedido):
    return (
        pedido.fecha_hora_asignacion is None
        or timezone.now() - pedido.fecha_hora_asignacion
        >= timedelta(seconds=Pedido.LIMITE_ACEPTACION_SEGUNDOS)
    )


def _liberar_pedido(pedido, usuario, incidencia):
    estado_anterior = pedido.estado
    pedido.repartidor = None
    pedido.fecha_hora_asignacion = None
    pedido.fecha_hora_aceptacion = None
    pedido.estado = 'registrado'
    pedido.save(update_fields=[
        'repartidor', 'fecha_hora_asignacion', 'fecha_hora_aceptacion', 'estado',
    ])
    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior=estado_anterior,
        estado_nuevo='registrado',
        usuario=usuario,
        incidencia=incidencia,
    )


@login_required
def home(req):
    if req.user.is_superuser:
        return redirect('admin:index')

    perfil = Repartidor.objects.filter(user=req.user).first()
    asignado = Pedido.objects.filter(
        repartidor=req.user,
        estado='asignado',
        fecha_hora_asignacion__isnull=False,
        fecha_hora_aceptacion__isnull=True,
    ).order_by('fecha_hora_asignacion').first()
    expirado = False
    if asignado and _expirado(asignado):
        with transaction.atomic():
            pedido = Pedido.objects.select_for_update().filter(
                pk=asignado.pk, estado='asignado',
                fecha_hora_aceptacion__isnull=True,
            ).first()
            if pedido and _expirado(pedido):
                _liberar_pedido(
                    pedido,
                    req.user,
                    'Desasignado por expiración del tiempo de espera (5 minutos)',
                )
                if perfil:
                    perfil.disponible = False
                    perfil.save(update_fields=['disponible'])
        expirado = True

    pedido_activo = Pedido.objects.filter(
        repartidor=req.user,
        estado__in=['asignado', 'retirado', 'en_viaje']
    ).first()

    return render(
        req,
        'repartidor/index.html',
        {
            'pedido_activo': pedido_activo,
            'esperando_respuesta': bool(asignado and not expirado),
            'segundos_restantes': (
                max(0, int(
                    Pedido.LIMITE_ACEPTACION_SEGUNDOS
                    - (timezone.now() - asignado.fecha_hora_asignacion).total_seconds()
                )) if asignado and not expirado else None
            ),
            'expirado': expirado,
            'disponible': bool(perfil and perfil.disponible and req.user.disponible),
        }
    )


@login_required
@require_POST
@transaction.atomic
def aceptar(req, pedido_id):
    pedido = Pedido.objects.select_for_update().filter(
        pk=pedido_id,
        repartidor=req.user,
        estado='asignado',
        fecha_hora_aceptacion__isnull=True,
    ).first()
    if pedido is None:
        return HttpResponseBadRequest('El pedido no está asignado a este repartidor.')
    if _expirado(pedido):
        _liberar_pedido(
            pedido,
            req.user,
            'Desasignado por expiración del tiempo de espera (5 minutos)',
        )
        perfil = Repartidor.objects.filter(user=req.user).first()
        if perfil:
            perfil.disponible = False
            perfil.save(update_fields=['disponible'])
        return redirect('repartidor')

    pedido.fecha_hora_aceptacion = timezone.now()
    pedido.fecha_hora_asignacion = None
    pedido.save(update_fields=['fecha_hora_aceptacion', 'fecha_hora_asignacion'])
    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior='asignado',
        estado_nuevo='asignado',
        usuario=req.user,
        incidencia=f'Aceptado por repartidor {req.user.get_full_name() or req.user.username}',
    )
    messages.success(req, 'Asignación confirmada. Ya podés retirar el pedido.')
    return redirect('repartidor')


@login_required
@require_POST
@transaction.atomic
def rechazar(req, pedido_id):
    pedido = Pedido.objects.select_for_update().filter(
        pk=pedido_id,
        repartidor=req.user,
        estado='asignado',
        fecha_hora_aceptacion__isnull=True,
    ).first()
    if pedido is None:
        return HttpResponseBadRequest('El pedido no está asignado a este repartidor.')

    incidencia = (
        'Desasignado por expiración del tiempo de espera (5 minutos)'
        if _expirado(pedido)
        else f'Rechazado por repartidor {req.user.get_full_name() or req.user.username}'
    )
    _liberar_pedido(pedido, req.user, incidencia)
    perfil = Repartidor.objects.filter(user=req.user).first()
    if perfil:
        perfil.disponible = False
        perfil.save(update_fields=['disponible'])
    messages.info(req, 'El pedido se liberó para reasignación.')
    return redirect('repartidor')


def comprimir_imagen(imagen):
    img = Image.open(imagen)

    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    img.thumbnail((1280, 1280))

    buffer = BytesIO()
    img.save(
        buffer,
        format='JPEG',
        quality=75,
        optimize=True
    )
    buffer.seek(0)

    nombre = imagen.name.rsplit('.', 1)[0] + '.jpg'

    return InMemoryUploadedFile(
        buffer,
        'ImageField',
        nombre,
        'image/jpeg',
        buffer.getbuffer().nbytes,
        None
    )


@login_required
@require_POST
@transaction.atomic
def actualizar_estado(req, pedido_id):
    pedido = get_object_or_404(
        Pedido,
        id=pedido_id,
        repartidor=req.user
    )

    nuevo_estado = req.POST.get('estado')

    if nuevo_estado == 'registrado' or not pedido.puede_cambiar_a(nuevo_estado):
        messages.error(
            req,
            'La transición de estado no está permitida.'
        )
        return redirect('repartidor')

    estado_anterior = pedido.estado

    incidencia = ''

    if nuevo_estado == 'fallido':
        incidencia = (
            'Destinatario ausente. '
            'Retornar el pedido al centro de distribución.'
        )

    fotografia = req.FILES.get('fotografia')

    if fotografia and nuevo_estado not in ['retirado', 'entregado']:
        messages.error(
            req,
            'Solo se pueden adjuntar fotografías al retirar o entregar el pedido.'
        )
        return redirect('repartidor')

    if fotografia:
        fotografia = comprimir_imagen(fotografia)

    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior=estado_anterior,
        estado_nuevo=nuevo_estado,
        usuario=req.user,
        fotografia=fotografia,
        incidencia=incidencia
    )

    pedido.estado = nuevo_estado
    pedido.save()

    messages.success(
        req,
        'Estado de la entrega actualizado correctamente.'
    )

    return redirect('repartidor')
