from uuid import UUID, uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods

from main.operario.models import Comercio
from main.repartidor.models import HistorialEstado, Pedido, Repartidor
from main.users.models import User

from .forms import (
    AsignarPedidoForm,
    ComercioForm,
    MENSAJE_COMERCIO_INACTIVO,
    MENSAJE_COMERCIO_DUPLICADO,
    PedidoForm,
    RepartidorForm,
)


MAX_INTENTOS_CODIGO = Pedido.INTENTOS_CODIGO


class ComercioInactivoError(Exception):
    pass


class NoSePudoGenerarCodigoError(Exception):
    pass


def _exigir_operario(request):
    if not request.user.is_operario:
        raise PermissionDenied


def _pedidos_en_curso():
    return (
        Pedido.objects.filter(
            estado__in=('registrado', 'asignado', 'retirado', 'en_viaje')
        )
        .select_related('comercio', 'repartidor')
        .order_by('fecha_creacion', 'pk')
    )


@login_required
def inicio(request):
    _exigir_operario(request)
    pedidos = _pedidos_en_curso()
    return render(request, 'operario/inicio.html', {'pedidos': pedidos})

@login_required
def buscar_pedido(request):
    _exigir_operario(request)

    busqueda = request.GET.get('q', '').strip()

    if not busqueda:
        messages.error(request, 'Ingresá un código o identificador de pedido.')
        return redirect('operario:inicio')

    pedido = Pedido.objects.filter(codigo__iexact=busqueda).first()

    if pedido is None and busqueda.isdigit():
        pedido = Pedido.objects.filter(pk=int(busqueda)).first()

    if pedido is None:
        messages.error(request, 'No se encontró ningún pedido con ese código o identificador.')
        return redirect('operario:inicio')

    return redirect('operario:detalle_pedido', pedido_id=pedido.pk)


@login_required
def comercios(request):
    _exigir_operario(request)
    return render(request, 'operario/comercios.html', {
        'comercios': Comercio.objects.all(),
    })


@login_required
@require_POST
def cambiar_estado_comercio(request):
    _exigir_operario(request)

    nombre = request.POST.get('nombre', '').strip()
    activo = request.POST.get('activo')
    if not nombre or activo not in ('true', 'false'):
        return JsonResponse(
            {'error': 'Se requiere el nombre del comercio y un estado booleano válido.'},
            status=400,
        )

    comercio = get_object_or_404(Comercio, nombre=nombre)
    comercio.activo = activo == 'true'
    comercio.save(update_fields=['activo'])
    return JsonResponse({'nombre': comercio.nombre, 'activo': comercio.activo})


@login_required
def nuevo_comercio(request):
    _exigir_operario(request)

    if request.method == 'POST':
        formulario = ComercioForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Comercio dado de alta exitosamente.')
            return redirect('operario:comercios')
    else:
        formulario = ComercioForm()

    return render(request, 'operario/nuevo_comercio.html', {'form': formulario})


@login_required
def repartidores(request):
    _exigir_operario(request)
    perfiles = Repartidor.objects.select_related('user').order_by('user__username')
    return render(request, 'operario/repartidores.html', {'repartidores': perfiles})


@login_required
def estado_repartidores(request):
    _exigir_operario(request)
    perfiles = Repartidor.objects.select_related('user').order_by('user__username')
    return JsonResponse({
        'repartidores': [{
            'username': perfil.user.username,
            'disponible': perfil.disponible,
        } for perfil in perfiles],
    })


@login_required
@require_POST
def cambiar_estado_repartidor(request):
    _exigir_operario(request)

    username = request.POST.get('username', '').strip()
    activo = request.POST.get('activo')
    if not username or activo not in ('true', 'false'):
        return JsonResponse(
            {'error': 'Se requiere el usuario del repartidor y un estado booleano válido.'},
            status=400,
        )

    perfil = get_object_or_404(
        Repartidor.objects.select_related('user'), user__username=username
    )

    if activo == 'false':
        tiene_pedido_activo = Pedido.objects.filter(
            repartidor=perfil.user,
            estado__in=('asignado', 'retirado', 'en_viaje'),
        ).exists()
        if tiene_pedido_activo:
            return JsonResponse(
                {'error': 'El repartidor tiene pedidos en curso'},
                status=400,
            )

    perfil.user.is_active = activo == 'true'
    perfil.user.save(update_fields=['is_active'])
    return JsonResponse({'username': perfil.user.username, 'activo': perfil.user.is_active})


@login_required
def nuevo_repartidor(request):
    _exigir_operario(request)

    if request.method == 'POST':
        formulario = RepartidorForm(request.POST)
        if formulario.is_valid():
            datos = formulario.cleaned_data
            try:
                with transaction.atomic():
                    usuario = User.objects.create_user(
                        username=datos['usuario'],
                        password=None,
                        first_name=datos['nombre'],
                        last_name=datos['apellido'],
                        email=datos['email'],
                    )
                    Repartidor.objects.create(
                        user=usuario,
                        pin=datos['pin'],
                        dni=datos['dni'],
                        vehiculo=datos['vehiculo'],
                    )
                messages.success(request, 'Repartidor dado de alta exitosamente.')
                return redirect('operario:repartidores')
            except IntegrityError:
                formulario.add_error('dni', 'El DNI ingresado ya se encuentra registrado en el sistema.')
    else:
        formulario = RepartidorForm()

    return render(request, 'operario/nuevo_repartidor.html', {'form': formulario})


@login_required
def estado_pedidos(request):
    _exigir_operario(request)
    pedidos = _pedidos_en_curso()
    return JsonResponse({
        'pedidos': [{
            'codigo': pedido.codigo,
            'comercio': pedido.comercio.nombre if pedido.comercio else 'Sin comercio',
            'destino': pedido.direccion_destino or 'Sin destino',
            'estado': pedido.get_estado_display(),
            'estado_id': pedido.estado,
            'repartidor': (
                pedido.repartidor.get_full_name() or pedido.repartidor.username
                if pedido.repartidor else 'Sin asignar'
            ),
            'creado': timezone.localtime(pedido.fecha_creacion).strftime('%d/%m/%Y %H:%M'),
            'url': reverse('operario:detalle_pedido', args=[pedido.pk]),
        } for pedido in pedidos],
    })


@login_required
def detalle_pedido(request, pedido_id):
    _exigir_operario(request)
    pedido = get_object_or_404(
        Pedido.objects.select_related('comercio', 'repartidor')
        .prefetch_related('historial__usuario'),
        pk=pedido_id,
    )
    formulario = AsignarPedidoForm() if pedido.estado == 'registrado' else None
    return render(request, 'operario/detalle_pedido.html', {
        'pedido': pedido,
        'historial': pedido.historial.all(),
        'formulario_asignacion': formulario,
    })


@login_required
@require_POST
@transaction.atomic
def asignar_repartidor(request, pedido_id):
    _exigir_operario(request)
    pedido = get_object_or_404(Pedido.objects.select_for_update(), pk=pedido_id)
    if pedido.estado != 'registrado' or pedido.repartidor_id is not None:
        messages.error(request, 'Solo se puede asignar un pedido sin asignar y en estado Registrado.')
        return redirect('operario:detalle_pedido', pedido_id=pedido.pk)

    formulario = AsignarPedidoForm(request.POST)
    if not formulario.is_valid():
        messages.error(request, 'Elegí un repartidor disponible para asignar el pedido.')
        return redirect('operario:detalle_pedido', pedido_id=pedido.pk)

    perfil = get_object_or_404(
        Repartidor.objects.select_for_update().select_related('user'),
        pk=formulario.cleaned_data['repartidor'].pk,
    )
    tiene_pedido_activo = Pedido.objects.filter(
        repartidor=perfil.user,
        estado__in=('asignado', 'retirado', 'en_viaje'),
    ).exists()
    if not perfil.disponible or not perfil.user.is_active or tiene_pedido_activo:
        messages.error(request, 'El repartidor seleccionado ya no está disponible.')
        return redirect('operario:detalle_pedido', pedido_id=pedido.pk)

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
        usuario=request.user,
        incidencia=f'Asignado por operario a {perfil.user.get_full_name() or perfil.user.username}',
    )
    messages.success(request, 'Pedido asignado. El repartidor verá la solicitud al ingresar y tendrá cinco minutos para responder.')
    return redirect('operario:detalle_pedido', pedido_id=pedido.pk)


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
                            datos_destinatario=datos['datos_destinatario'],
                            tamano_paquete=datos['tamano_paquete'],
                            vehiculo_requerido=datos['vehiculo_requerido'],
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
    if not request.user.is_operario:
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
    if not request.user.is_operario:
        raise PermissionDenied

    pedido = get_object_or_404(
        Pedido.objects.select_related('comercio'),
        pk=pedido_id,
    )
    return render(request, 'operario/pedido_registrado.html', {'pedido': pedido})

@login_required
@require_http_methods(['GET', 'POST'])
def editar_comercio(request, comercio_id):
    _exigir_operario(request)
    comercio = get_object_or_404(Comercio, pk=comercio_id)
    
    nombre_original = comercio.nombre
    if request.method == 'POST':
        formulario = ComercioForm(request.POST, instance=comercio)
        if formulario.is_valid():
            try:
                with transaction.atomic():
                    formulario.save()
            except IntegrityError:
                formulario.add_error('nombre', MENSAJE_COMERCIO_DUPLICADO)
            else:
                messages.success(request, 'Datos del comercio actualizados')
                return redirect('operario:editar_comercio', comercio_id=comercio.pk)
    else:
        formulario = ComercioForm(instance=comercio)
        
    return render(request, 'operario/editar_comercio.html', {
        'form': formulario,
        'nombre_original': nombre_original,
    })