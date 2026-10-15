# main/repartidor/views.py

from io import BytesIO

from PIL import Image

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Pedido, HistorialEstado


@login_required
def home(req):
    if req.user.is_superuser:
        return redirect('admin:index')

    pedido_activo = Pedido.objects.filter(
        repartidor=req.user,
        estado__in=['asignado', 'retirado', 'en_viaje']
    ).first()

    return render(
        req,
        'repartidor/index.html',
        {'pedido_activo': pedido_activo}
    )


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
def actualizar_estado(req, pedido_id):
    pedido = get_object_or_404(
        Pedido,
        id=pedido_id,
        repartidor=req.user
    )

    nuevo_estado = req.POST.get('estado')

    if not pedido.puede_cambiar_a(nuevo_estado):
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