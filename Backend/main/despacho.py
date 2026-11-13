from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from main.repartidor.models import HistorialEstado, Pedido, Repartidor


MENSAJE_EXPIRACION = 'Desasignado por expiración del tiempo de espera (5 minutos)'


def expirado(pedido):
    return (
        pedido.fecha_hora_asignacion is None
        or timezone.now() - pedido.fecha_hora_asignacion
        >= timedelta(seconds=Pedido.LIMITE_ACEPTACION_SEGUNDOS)
    )


def liberar_pedido(pedido, usuario, incidencia):
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


def candidato_repartidor(vehiculo):
    ocupados = Pedido.objects.filter(
        estado__in=('asignado', 'retirado', 'en_viaje'),
        repartidor__isnull=False,
    ).values('repartidor_id')
    return (
        Repartidor.objects.select_related('user')
        .filter(disponible=True, user__is_active=True, vehiculo=vehiculo)
        .exclude(user_id__in=ocupados)
        .order_by(F('disponible_desde').asc(nulls_last=True), 'pk')
        .first()
    )


def aplicar_asignacion(pedido, perfil, usuario, incidencia):
    estado_anterior = pedido.estado
    pedido.repartidor = perfil.user
    pedido.estado = 'asignado'
    pedido.fecha_hora_asignacion = timezone.now()
    pedido.fecha_hora_aceptacion = None
    pedido.save(update_fields=[
        'repartidor', 'estado', 'fecha_hora_asignacion', 'fecha_hora_aceptacion',
    ])
    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior=estado_anterior,
        estado_nuevo='asignado',
        usuario=usuario,
        incidencia=incidencia,
    )


def despacho_automatico(pedido, usuario):
    if pedido.vehiculo_requerido not in dict(Repartidor.VEHICULOS):
        return None
    perfil = candidato_repartidor(pedido.vehiculo_requerido)
    if perfil is None:
        return None
    aplicar_asignacion(
        pedido,
        perfil,
        usuario,
        f'Asignación automática a {perfil.user.get_full_name() or perfil.user.username}',
    )
    return perfil


def liberar_asignacion_vencida(pedido, usuario):
    """Libera una asignación expirada, da de baja al repartidor y reintenta la cascada."""
    repartidor = pedido.repartidor
    liberar_pedido(pedido, usuario, MENSAJE_EXPIRACION)
    if repartidor is not None:
        Repartidor.objects.filter(user=repartidor).update(
            disponible=False, disponible_desde=None,
        )
    return despacho_automatico(pedido, usuario)


def procesar_asignaciones_vencidas(usuario):
    """Libera y reintenta en cascada las asignaciones que superaron los 5 minutos."""
    vencidas = Pedido.objects.filter(
        estado='asignado',
        fecha_hora_asignacion__isnull=False,
        fecha_hora_aceptacion__isnull=True,
    )
    for pk in list(vencidas.values_list('pk', flat=True)):
        with transaction.atomic():
            pedido = Pedido.objects.select_for_update().filter(
                pk=pk, estado='asignado', fecha_hora_aceptacion__isnull=True,
            ).first()
            if pedido is None or not expirado(pedido):
                continue
            liberar_asignacion_vencida(pedido, usuario)