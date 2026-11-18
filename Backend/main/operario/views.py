from uuid import UUID, uuid4
import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, OuterRef, Prefetch, Subquery
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache

from main.despacho import (
    aplicar_asignacion as _aplicar_asignacion,
    despacho_automatico as _despacho_automatico,
    procesar_asignaciones_vencidas,
)
from main.operario.models import Comercio, Devolucion
from main.repartidor.models import HistorialEstado, Pedido, Repartidor
from main.users.models import User

from .forms import (
    AsignarPedidoForm,
    ComercioForm,
    MENSAJE_COMERCIO_INACTIVO,
    MENSAJE_COMERCIO_DUPLICADO,
    MENSAJE_VEHICULO_INCOMPATIBLE,
    PedidoForm,
    RegenerarPinForm,
    RepartidorForm,
)


MAX_INTENTOS_CODIGO = Pedido.INTENTOS_CODIGO


def _pin_aleatorio(disponibles):
    return secrets.choice(disponibles)


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


def _pedidos_sin_repartidor(pedidos):
    return [
        pedido for pedido in pedidos
        if pedido.estado == 'registrado' and pedido.repartidor_id is None
    ]


@login_required
def inicio(request):
    _exigir_operario(request)
    procesar_asignaciones_vencidas(request.user)
    pedidos = _pedidos_en_curso()
    return render(request, 'operario/inicio.html', {
        'pedidos': pedidos,
        'pedidos_sin_repartidor': _pedidos_sin_repartidor(pedidos),
    })


@login_required
def entregas_fallidas(request):
    _exigir_operario(request)

    eventos_falla = HistorialEstado.objects.filter(
        pedido_id=OuterRef('pk'),
        estado_nuevo='fallido',
    ).order_by('-fecha', '-pk')
    eventos_falla_prefetch = (
        HistorialEstado.objects.filter(estado_nuevo='fallido')
        .select_related('usuario')
        .order_by('-fecha', '-pk')
    )
    pedidos = (
        Pedido.objects.filter(estado='fallido')
        .select_related('comercio')
        .annotate(fecha_falla=Subquery(eventos_falla.values('fecha')[:1]))
        .prefetch_related(
            Prefetch(
                'historial',
                queryset=eventos_falla_prefetch,
                to_attr='eventos_falla',
            ),
            Prefetch(
                'devolucion_confirmada',
                queryset=Devolucion.objects.select_related('usuario'),
                to_attr='evento_devolucion_hu34',
            ),
        )
        .order_by(F('fecha_falla').asc(nulls_last=True), 'pk')
    )

    entregas = []
    for pedido in pedidos:
        eventos = pedido.eventos_falla
        entregas.append({
            'pedido': pedido,
            # Si hubiera varios eventos de falla, se muestra el último intento.
            'evento': eventos[0] if eventos else None,
            'devolucion': pedido.evento_devolucion_hu34,
        })

    return render(request, 'operario/entregas_fallidas.html', {
        'entregas': entregas,
    })


@login_required
@require_POST
@transaction.atomic
def confirmar_devolucion(request, pedido_id):
    _exigir_operario(request)
    pedido = get_object_or_404(
        Pedido.objects.select_for_update(),
        pk=pedido_id,
    )
    if pedido.estado != 'fallido':
        return HttpResponseBadRequest(
            'Solo se puede confirmar la devolución de un pedido Fallido.'
        )

    Devolucion.objects.get_or_create(
        pedido=pedido,
        defaults={'usuario': request.user},
    )
    messages.success(request, 'Devolución registrada')
    return redirect('operario:entregas_fallidas')


@login_required
def historial_pedidos(request):
    _exigir_operario(request)

    comercio = request.GET.get('comercio', '').strip()
    estado = request.GET.get('estado', '').strip()

    pedidos = Pedido.objects.select_related('comercio').all()

    if comercio:
        pedidos = pedidos.filter(comercio__nombre__icontains=comercio)

    if estado:
        pedidos = pedidos.filter(estado=estado)

    pedidos = pedidos.order_by('-pk')

    return render(request, 'operario/historial_pedidos.html', {
        'pedidos': pedidos,
        'comercio_buscado': comercio,
        'estado_seleccionado': estado,
        'estados': Pedido.ESTADOS,
    })


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
    mensaje = (
        'Comercio reactivado exitosamente'
        if comercio.activo
        else 'Comercio deshabilitado exitosamente'
    )
    return JsonResponse({
        'nombre': comercio.nombre,
        'activo': comercio.activo,
        'mensaje': mensaje,
    })


@login_required
@never_cache
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
@require_POST
@never_cache
def regenerar_pin_repartidor(request, repartidor_id):
    _exigir_operario(request)

    perfiles = Repartidor.objects.select_related('user').order_by('user__username')

    with transaction.atomic():
        perfil = get_object_or_404(
            Repartidor.objects.select_for_update(of=('self',)),
            pk=repartidor_id,
        )

        formulario = RegenerarPinForm(request.POST, repartidor=perfil)
        if not formulario.is_valid():
            error_msg = formulario.errors['pin'][0]
            messages.error(request, error_msg)
            return render(request, 'operario/repartidores.html', {
                'repartidores': perfiles,
                'error_pin': error_msg,
                'repartidor_error_id': perfil.pk,
            })

        nuevo_pin = formulario.cleaned_data['pin']
        try:
            with transaction.atomic():
                perfil.pin = nuevo_pin
                perfil.save(update_fields=['pin'])
        except IntegrityError:
            error_msg = 'Ese PIN ya está asignado a otro repartidor.'
            messages.error(request, error_msg)
            return render(request, 'operario/repartidores.html', {
                'repartidores': perfiles,
                'error_pin': error_msg,
                'repartidor_error_id': perfil.pk,
            })

    return render(request, 'operario/repartidores.html', {
        'repartidores': perfiles,
        'pin_actualizado': nuevo_pin,
        'pin_regenerado': nuevo_pin,
        'repartidor_pin': perfil,
    })


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
@never_cache
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
    procesar_asignaciones_vencidas(request.user)
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
            'repartidor_id': pedido.repartidor_id,
            'creado': timezone.localtime(pedido.fecha_creacion).strftime('%d/%m/%Y %H:%M'),
            'url': reverse('operario:detalle_pedido', args=[pedido.pk]),
            'sin_repartidor': (
                pedido.estado == 'registrado' and pedido.repartidor_id is None
            ),
            'url_reintentar': reverse(
                'operario:reintentar_asignacion', args=[pedido.pk]
            ),
        } for pedido in pedidos],
    })


@login_required
def detalle_pedido(request, pedido_id):
    _exigir_operario(request)
    procesar_asignaciones_vencidas(request.user)
    pedido = get_object_or_404(
        Pedido.objects.select_related('comercio', 'repartidor')
        .prefetch_related('historial__usuario'),
        pk=pedido_id,
    )
    formulario = (
        AsignarPedidoForm(pedido=pedido) if pedido.estado == 'registrado' else None
    )
    pedidos_sin_repartidor = list(
        Pedido.objects.filter(estado='registrado', repartidor__isnull=True)
        .select_related('comercio')
        .order_by('fecha_creacion', 'pk')
    )
    return render(request, 'operario/detalle_pedido.html', {
        'pedido': pedido,
        'historial': pedido.historial.all(),
        'formulario_asignacion': formulario,
        'pedidos_sin_repartidor': pedidos_sin_repartidor,
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

    formulario = AsignarPedidoForm(request.POST, pedido=pedido)
    if not formulario.is_valid():
        messages.error(request, 'Elegí un repartidor disponible para asignar el pedido.')
        return redirect('operario:detalle_pedido', pedido_id=pedido.pk)

    perfil = formulario.cleaned_data['repartidor']
    if perfil is None:
        if _despacho_automatico(pedido, request.user) is None:
            messages.error(
                request,
                'Pedido sin repartidor disponible. No hay candidatos para el vehículo requerido.',
            )
        else:
            messages.success(
                request,
                'Pedido asignado automáticamente. El repartidor verá la solicitud al ingresar y tendrá cinco minutos para responder.',
            )
        return redirect('operario:detalle_pedido', pedido_id=pedido.pk)

    perfil = get_object_or_404(
        Repartidor.objects.select_for_update().select_related('user'),
        pk=perfil.pk,
    )
    tiene_pedido_activo = Pedido.objects.filter(
        repartidor=perfil.user,
        estado__in=('asignado', 'retirado', 'en_viaje'),
    ).exists()
    if not perfil.disponible or not perfil.user.is_active or tiene_pedido_activo:
        messages.error(request, 'El repartidor seleccionado ya no está disponible.')
        return redirect('operario:detalle_pedido', pedido_id=pedido.pk)
    vehiculo_pedido = pedido.vehiculo_requerido
    if (
        vehiculo_pedido in dict(Repartidor.VEHICULOS)
        and perfil.vehiculo != vehiculo_pedido
    ):
        messages.error(request, MENSAJE_VEHICULO_INCOMPATIBLE)
        return redirect('operario:detalle_pedido', pedido_id=pedido.pk)

    _aplicar_asignacion(
        pedido,
        perfil,
        request.user,
        f'Asignado por operario a {perfil.user.get_full_name() or perfil.user.username}',
    )
    messages.success(request, 'Pedido asignado. El repartidor verá la solicitud al ingresar y tendrá cinco minutos para responder.')
    return redirect('operario:detalle_pedido', pedido_id=pedido.pk)


@login_required
@require_POST
@transaction.atomic
def reintentar_asignacion(request, pedido_id):
    _exigir_operario(request)
    pedido = get_object_or_404(Pedido.objects.select_for_update(), pk=pedido_id)
    if pedido.estado != 'registrado' or pedido.repartidor_id is not None:
        messages.error(request, 'El pedido ya no está pendiente de repartidor.')
        return redirect('operario:detalle_pedido', pedido_id=pedido.pk)

    if _despacho_automatico(pedido, request.user) is None:
        messages.error(
            request,
            'Pedido sin repartidor disponible. No hay candidatos para el vehículo requerido.',
        )
    else:
        messages.success(
            request,
            'Pedido asignado. El repartidor verá la solicitud al ingresar y tendrá cinco minutos para responder.',
        )
    return redirect('operario:detalle_pedido', pedido_id=pedido.pk)


@login_required
@require_POST
@transaction.atomic
def cancelar_pedido(request, pedido_id):
    _exigir_operario(request)
    pedido = get_object_or_404(
        Pedido.objects.select_for_update(of=('self',)).select_related('repartidor'),
        pk=pedido_id,
    )
    if pedido.estado not in ('registrado', 'asignado'):
        return HttpResponseBadRequest('No se puede cancelar un pedido en su estado actual.')

    estado_anterior = pedido.estado
    repartidor = pedido.repartidor
    pedido.estado = 'cancelado'
    pedido.fecha_hora_aceptacion = None
    pedido.save(update_fields=['estado', 'fecha_hora_aceptacion'])

    incidencia = 'Cancelación solicitada por operario.'
    if repartidor is not None:
        incidencia += f' Baja de asignación para repartidor {repartidor.username}.'
        perfil = Repartidor.objects.select_for_update().filter(user=repartidor).first()
        if perfil is not None:
            perfil.disponible = True
            perfil.disponible_desde = timezone.now()
            perfil.save(update_fields=['disponible', 'disponible_desde'])

    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior=estado_anterior,
        estado_nuevo='cancelado',
        usuario=request.user,
        incidencia=incidencia,
    )
    messages.success(request, 'Pedido cancelado.')
    return redirect('operario:detalle_pedido', pedido_id=pedido.pk)


def _codigo_de_solicitud(request):
    try:
        return UUID(request.POST.get('clave_idempotencia', ''))
    except (TypeError, ValueError, AttributeError):
        return None


def _datos_coinciden_con_pedido(pedido, datos):
    if pedido.comercio_id != datos['comercio'].pk:
        return False
    if pedido.direccion_destino != datos['direccion_destino']:
        return False
    if pedido.datos_destinatario != datos['datos_destinatario']:
        return False
    if pedido.tamano_paquete != datos['tamano_paquete']:
        return False
    if pedido.vehiculo_requerido != datos['vehiculo_requerido']:
        return False
    if pedido.especificaciones_traslado != datos['especificaciones_traslado']:
        return False

    fecha_pedido = pedido.fecha_hora_estimada_entrega
    fecha_datos = datos['fecha_hora_estimada_entrega']
    if fecha_pedido and fecha_datos:
        if abs((fecha_pedido - fecha_datos).total_seconds()) > 60:
            return False
    elif fecha_pedido != fecha_datos:
        return False

    perfil = datos.get('repartidor')
    if perfil is not None:
        if pedido.repartidor_id != perfil.user_id:
            return False
    else:
        evento_asig = pedido.historial.filter(estado_nuevo='asignado').order_by('fecha', 'pk').first()
        if evento_asig and 'Asignado por operario' in (evento_asig.incidencia or ''):
            return False
    return True


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
                        perfil = datos.get('repartidor')
                        if perfil is not None:
                            _aplicar_asignacion(
                                pedido,
                                perfil,
                                usuario,
                                f'Asignado por operario a {perfil.user.get_full_name() or perfil.user.username}',
                            )
                        else:
                            _despacho_automatico(pedido, usuario)
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
@never_cache
def cargar_pedido(request):
    if not request.user.is_operario:
        raise PermissionDenied

    if request.method == 'POST':
        formulario = PedidoForm(request.POST)
        if formulario.is_valid():
            clave = formulario.cleaned_data.get('clave_idempotencia')
            pedido_existente = None
            if clave:
                pedido_existente = (
                    Pedido.objects.filter(clave_idempotencia=clave)
                    .select_related('comercio', 'repartidor')
                    .prefetch_related('historial')
                    .first()
                )

            if pedido_existente:
                if _datos_coinciden_con_pedido(pedido_existente, formulario.cleaned_data):
                    return redirect(
                        'operario:pedido_registrado',
                        pedido_id=pedido_existente.pk,
                    )
                else:
                    formulario.cleaned_data['clave_idempotencia'] = uuid4()

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
            clave = _codigo_de_solicitud(request)
            if clave and Pedido.objects.filter(clave_idempotencia=clave).exists():
                data = formulario.data.copy()
                data['clave_idempotencia'] = str(uuid4())
                formulario.data = data
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
@never_cache
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
