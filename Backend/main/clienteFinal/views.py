from django.shortcuts import render
from django.views.decorators.http import require_GET # para restringir el acceso a una vista, permitiendo únicamente solicitudes que usen el método HTTP GET.
from django.http import Http404 #para poder lanzar excepción que devuelva una página de error 404 si el usuario busca un pedido que no existe.
from main.repartidor.models import HistorialEstado, Pedido


# Estados definidos en la Entrevista 02: (texto visible, color de Bootstrap)
ESTADOS = {
    'registrado': ('Registrado', 'secondary'),
    'asignado': ('Asignado', 'info'),
    'retirado': ('Retirado', 'info'),
    'en_viaje': ('En viaje', 'primary'),
    'entregado': ('Entregado', 'success'),
    'fallido': ('Fallido', 'danger'),
    'cancelado': ('Cancelado', 'dark'),
}

# Create your views here.

def form(req):
  return render(req, 'clienteFinal/index.html', {})

def obtener_pedido(codigo):
    pedido = (
        Pedido.objects.select_related('comercio')
        .filter(codigo=codigo)
        .first()
    )
    if pedido is None:
        return None

    return {
        'estado': pedido.estado,
        'comercio': pedido.comercio.nombre if pedido.comercio else '',
        'llegada_estimada': pedido.fecha_hora_estimada_entrega,
    }

def obtener_historial(codigo):
    historial = []
    cambios = HistorialEstado.objects.filter(
        pedido__codigo=codigo
    ).order_by('fecha', 'pk')

    for cambio in cambios:
        # Eventos de auditoría sin transición (por ejemplo, aceptar un viaje)
        # no deben aparecer como un segundo paso del mismo estado en el timeline.
        if cambio.estado_anterior == cambio.estado_nuevo:
            continue
        etiqueta, clase = ESTADOS[cambio.estado_nuevo]
        historial.append({
            'etiqueta': etiqueta,
            'clase': clase,
            'fecha': cambio.fecha,
        })
    return historial

def debe_mostrar_tiempo(estado, llegada_estimada):
    """La hora estimada solo se muestra si el pedido está en viaje y hay un valor."""
    return estado == 'en_viaje' and llegada_estimada is not None


@require_GET
def seguimiento(req, codigo):
    pedido = obtener_pedido(codigo)
    if pedido is None:
        raise Http404('Pedido no encontrado')

    etiqueta, clase = ESTADOS[pedido['estado']]
    llegada = pedido['llegada_estimada']

    contexto = {
        'estado': etiqueta,
        'estado_clase': clase,
        'comercio': pedido['comercio'],
        'llegada_estimada': llegada,
        'mostrar_tiempo': debe_mostrar_tiempo(pedido['estado'], llegada),
        'historial': obtener_historial(codigo),
    }
    return render(req, 'clienteFinal/seguimiento.html', contexto)

