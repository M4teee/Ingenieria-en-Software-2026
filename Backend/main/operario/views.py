from uuid import UUID, uuid4

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from main.operario.models import Comercio
from main.repartidor.models import HistorialEstado, Pedido

from .forms import MENSAJE_COMERCIO_INACTIVO, PedidoForm


MAX_INTENTOS_CODIGO = Pedido.INTENTOS_CODIGO


class ComercioInactivoError(Exception):
    pass


class NoSePudoGenerarCodigoError(Exception):
    pass


def _codigo_de_solicitud(request):
    try:
        return UUID(request.POST.get('clave_idempotencia', ''))
    except (TypeError, ValueError, AttributeError):
        return None


def _crear_pedido(formulario, usuario):
    datos = formulario.cleaned_data
    clave = datos['clave_idempotencia']

    try:
        with transaction.atomic():
            comercio = Comercio.objects.select_for_update().get(
                pk=datos['comercio'].pk,
                activo=True,
            )

            for _ in range(MAX_INTENTOS_CODIGO):
                codigo = Pedido.generar_codigo()
                try:
                    with transaction.atomic():
                        pedido = Pedido.objects.create(
                            codigo=codigo,
                            clave_idempotencia=clave,
                            comercio=comercio,
                            direccion_destino=datos['direccion_destino'],
                            especificaciones_traslado=(
                                datos['especificaciones_traslado']
                            ),
                            fecha_hora_estimada_entrega=(
                                datos['fecha_hora_estimada_entrega']
                            ),
                            estado='registrado',
                            repartidor=None,
                        )
                        HistorialEstado.objects.create(
                            pedido=pedido,
                            estado_anterior='',
                            estado_nuevo='registrado',
                            usuario=usuario,
                        )
                    return pedido
                except IntegrityError:
                    pedido_existente = Pedido.objects.filter(
                        clave_idempotencia=clave
                    ).first()
                    if pedido_existente:
                        return pedido_existente

                    if Pedido.objects.filter(codigo=codigo).exists():
                        continue
                    raise
    except Comercio.DoesNotExist as error:
        raise ComercioInactivoError from error

    raise NoSePudoGenerarCodigoError


@login_required
def cargar_pedido(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == 'POST':
        clave = _codigo_de_solicitud(request)
        if clave:
            pedido_existente = Pedido.objects.filter(
                clave_idempotencia=clave
            ).first()
            if pedido_existente:
                return redirect(
                    'operario:pedido_registrado',
                    pedido_id=pedido_existente.pk,
                )

        formulario = PedidoForm(request.POST)
        if formulario.is_valid():
            try:
                pedido = _crear_pedido(formulario, request.user)
            except ComercioInactivoError:
                formulario.add_error(
                    'comercio',
                    MENSAJE_COMERCIO_INACTIVO,
                )
            except NoSePudoGenerarCodigoError:
                formulario.add_error(
                    None,
                    'No se pudo generar un código de seguimiento. Intentá de nuevo.',
                )
            else:
                return redirect(
                    'operario:pedido_registrado',
                    pedido_id=pedido.pk,
                )
    else:
        formulario = PedidoForm(initial={'clave_idempotencia': uuid4()})

    return render(
        request,
        'operario/cargar_pedido.html',
        {
            'form': formulario,
            'hay_comercios_activos': Comercio.objects.filter(activo=True).exists(),
        },
    )


@login_required
def pedido_registrado(request, pedido_id):
    if not request.user.is_staff:
        raise PermissionDenied

    pedido = get_object_or_404(
        Pedido.objects.select_related('comercio'),
        pk=pedido_id,
    )
    return render(request, 'operario/pedido_registrado.html', {'pedido': pedido})
