# main/repartidor/views.py

from datetime import timedelta
from io import BytesIO

from PIL import Image

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import FileResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import mimetypes
from django.views.decorators.http import require_GET, require_POST

from .models import HistorialEstado, Pedido, Repartidor
from .forms import ActualizarEstadoForm, MAX_FOTOGRAFIA_BYTES


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


def _exigir_repartidor_activo(usuario):
    if not usuario.is_active or not Repartidor.objects.filter(user=usuario).exists():
        raise PermissionDenied


def login_pin(req):
    if req.method == 'POST':
        pin = req.POST.get('pin', '').strip()
        repartidor = Repartidor.objects.filter(
            pin=pin,
            user__is_active=True,
        ).select_related('user').first()
        if len(pin) != 4 or not pin.isdigit():
            repartidor = None
        if repartidor is None:
            return render(req, 'repartidor/login_pin.html', {
                'error': 'PIN incorrecto. Verifique los dígitos',
            })
        login(req, repartidor.user)
        return redirect('repartidor')
    return render(req, 'repartidor/login_pin.html', {})


@login_required(login_url='repartidor_login_pin')
def home(req):
    repartidor = Repartidor.objects.filter(user=req.user).first()
    if repartidor is None or not req.user.is_active:
        raise PermissionDenied
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
                if repartidor:
                    repartidor.disponible = False
                    repartidor.save(update_fields=['disponible'])
        expirado = True

    pedido_activo = Pedido.objects.filter(
        repartidor=req.user,
        estado__in=['asignado', 'retirado', 'en_viaje']
    ).first()
    pedidos_cerrados = Pedido.objects.filter(
        repartidor=req.user,
        estado__in=['entregado', 'fallido', 'cancelado'],
    ).select_related('comercio').order_by('-fecha_creacion')

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
            'perfil_repartidor': repartidor,
            'disponible': bool(repartidor and repartidor.disponible and req.user.disponible),
            'pedidos_cerrados': pedidos_cerrados,
        }
    )


@login_required(login_url='repartidor_login_pin')
def detalle_pedido(req, pedido_id):
    repartidor = Repartidor.objects.filter(user=req.user, user__is_active=True).first()
    if repartidor is None:
        raise PermissionDenied

    pedido = get_object_or_404(
        Pedido.objects.select_related('comercio'),
        pk=pedido_id,
        repartidor=req.user,
    )
    if (
        pedido.estado == 'asignado'
        and pedido.fecha_hora_asignacion is not None
        and pedido.fecha_hora_aceptacion is None
    ):
        return redirect('repartidor')

    return render(req, 'repartidor/detalle_pedido.html', {
        'pedido': pedido,
        'historial': pedido.historial.select_related('usuario').order_by('fecha', 'pk'),
    })


@login_required
@require_GET
def ver_fotografia(req, historial_id):
    evento = get_object_or_404(
        HistorialEstado.objects.select_related('pedido'),
        pk=historial_id,
    )
    if not req.user.is_staff and evento.pedido.repartidor_id != req.user.pk:
        raise Http404
    if not evento.fotografia:
        raise Http404

    tipo_contenido = mimetypes.guess_type(evento.fotografia.name)[0] or 'application/octet-stream'
    respuesta = FileResponse(
        evento.fotografia.open('rb'),
        content_type=tipo_contenido,
    )
    respuesta['X-Content-Type-Options'] = 'nosniff'
    return respuesta


@login_required(login_url='repartidor_login_pin')
@require_POST
@transaction.atomic
def aceptar(req, pedido_id):
    _exigir_repartidor_activo(req.user)
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


@login_required(login_url='repartidor_login_pin')
@require_POST
@transaction.atomic
def rechazar(req, pedido_id):
    _exigir_repartidor_activo(req.user)
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


@login_required(login_url='repartidor_login_pin')
@require_POST
def toggle_disponibilidad(req):
    _exigir_repartidor_activo(req.user)
    repartidor = Repartidor.objects.filter(user=req.user).first()
    if repartidor is None:
        messages.error(req, 'No se encontró tu perfil de repartidor.')
        return redirect('repartidor')

    tiene_pedido_activo = Pedido.objects.filter(
        repartidor=req.user,
        estado__in=['asignado', 'retirado', 'en_viaje'],
    ).exists()
    if not repartidor.disponible and tiene_pedido_activo:
        messages.error(req, 'No podés marcarte disponible mientras tengas una entrega activa.')
        return redirect('repartidor')

    repartidor.disponible = not repartidor.disponible
    repartidor.save(update_fields=['disponible'])
    messages.success(
        req,
        'Ahora estás Disponible.' if repartidor.disponible else 'Ahora estás No disponible.',
    )
    return redirect('repartidor')


def comprimir_imagen(imagen):
    img = Image.open(imagen)

    if img.mode != 'RGB':
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


@login_required(login_url='repartidor_login_pin')
@require_POST
def actualizar_estado(req, pedido_id):
    if not Repartidor.objects.filter(user=req.user, user__is_active=True).exists():
        raise PermissionDenied

    pedido = get_object_or_404(
        Pedido,
        id=pedido_id,
        repartidor=req.user
    )

    archivos = req.FILES.getlist('fotografia')
    if len(archivos) > 1:
        messages.error(req, 'Adjuntá como máximo una fotografía por cambio de estado.')
        return redirect('repartidor')
    if archivos and archivos[0].size > MAX_FOTOGRAFIA_BYTES:
        messages.error(req, 'La fotografía no puede superar los 10 MB.')
        return redirect('repartidor')

    formulario = ActualizarEstadoForm(
        req.POST,
        {'fotografia': archivos[0]} if archivos else None,
    )
    if not formulario.is_valid():
        for errores in formulario.errors.values():
            for error in errores:
                messages.error(req, error)
        return redirect('repartidor')

    nuevo_estado = formulario.cleaned_data['estado']

    if nuevo_estado == 'registrado' or not pedido.puede_cambiar_a(nuevo_estado):
        messages.error(
            req,
            'La transición de estado no está permitida.'
        )
        return redirect('repartidor')

    if (
        pedido.estado == 'asignado'
        and pedido.fecha_hora_asignacion is not None
        and pedido.fecha_hora_aceptacion is None
    ):
        messages.error(req, 'Primero confirmá la asignación del pedido.')
        return redirect('repartidor')

    estado_anterior = pedido.estado

    incidencia = ''

    if nuevo_estado == 'fallido':
        incidencia = (
            'Destinatario ausente. '
            'Retornar el pedido al centro de distribución.'
        )

    fotografia = formulario.cleaned_data['fotografia']

    if fotografia and nuevo_estado not in ['retirado', 'entregado', 'fallido']:
        messages.error(
            req,
            'Solo se pueden adjuntar fotografías al retirar, entregar o registrar una entrega fallida.'
        )
        return redirect('repartidor')

    if fotografia:
        fotografia = comprimir_imagen(fotografia)

    ruta_fotografia = None
    try:
        with transaction.atomic():
            evento = HistorialEstado(
                pedido=pedido,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                usuario=req.user,
                fotografia=fotografia,
                incidencia=incidencia,
            )
            evento.save()
            if evento.fotografia:
                ruta_fotografia = evento.fotografia.name

            pedido.estado = nuevo_estado
            pedido.save(update_fields=['estado'])

            if nuevo_estado == 'entregado':
                perfil = Repartidor.objects.select_for_update().filter(user=req.user).first()
                if perfil:
                    perfil.disponible = True
                    perfil.save(update_fields=['disponible'])
    except Exception:
        if ruta_fotografia:
            default_storage.delete(ruta_fotografia)
        raise

    messages.success(
        req,
        'Estado de la entrega actualizado correctamente.'
    )

    return redirect('repartidor')
