from django.shortcuts import render
from django.views.decorators.http import require_GET # para restringir el acceso a una vista, permitiendo únicamente solicitudes que usen el método HTTP GET.
from django.http import Http404 #para poder lanzar excepción que devuelva una página de error 404 si el usuario busca un pedido que no existe.
from datetime import timedelta
from django.utils import timezone


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

# TEMPORAL: datos de prueba hasta que exista el modelo Pedido.
PEDIDOS_SIMULADOS = {
    'registrado-demo': {'estado': 'registrado', 'comercio': 'Panadería Sol', 'minutos': None},
    'viaje-demo': {'estado': 'en_viaje', 'comercio': 'Panadería Sol', 'minutos': 30},
    'entregado-demo': {'estado': 'entregado', 'comercio': 'Panadería Sol', 'minutos': 30},
    'fallido-demo': {'estado': 'fallido', 'comercio': 'Panadería Sol', 'minutos': 30},
    'cancelado-demo': {'estado': 'cancelado', 'comercio': 'Panadería Sol', 'minutos': 30},
}

# TEMPORAL: (estado, minutos atrás en que ocurrió). El último debe coincidir
# con el estado de PEDIDOS_SIMULADOS. (hasta q exista modelo).
HISTORIALES_SIMULADOS = {
    'registrado-demo': [('registrado', 90)],
    'viaje-demo': [('registrado', 120), ('asignado', 100), ('retirado', 60), ('en_viaje', 45)],
    'entregado-demo': [('registrado', 120), ('asignado', 100), ('retirado', 60), ('en_viaje', 45), ('entregado', 5)],
    'fallido-demo': [('registrado', 120), ('asignado', 100), ('retirado', 60), ('en_viaje', 45), ('fallido', 5)],
    'cancelado-demo': [('registrado', 120), ('cancelado', 90)],
}

# Create your views here.

def form(req):
  return render(req, 'clienteFinal/index.html', {})

def obtener_pedido(codigo):
    """TEMPORAL: devuelve datos simulados.

    Con el modelo real, devolver algo con las mismas claves
    (estado, comercio, llegada_estimada), por ejemplo:
    Pedido.objects.select_related('comercio').filter(codigo_seguimiento=codigo).first()
    """
    datos = PEDIDOS_SIMULADOS.get(codigo)
    if datos is None:
        return None
    minutos = datos['minutos']
    return {
        'estado': datos['estado'],
        'comercio': datos['comercio'],
        'llegada_estimada': timezone.now() + timedelta(minutes=minutos) if minutos else None,
    }

def obtener_historial(codigo):
    """TEMPORAL: devuelve datos simulados.

    Con el modelo real, devolver la misma estructura (etiqueta, clase, fecha),
    por ejemplo a partir de:
    pedido.historial.order_by('fecha_hora')
    Solo estado y fecha: nunca datos internos (repartidor, fotos).
    """
    pasos = HISTORIALES_SIMULADOS.get(codigo, [])
    ahora = timezone.now()
    historial = []
    for estado, minutos_atras in pasos:
        etiqueta, clase = ESTADOS[estado]
        historial.append({
            'etiqueta': etiqueta,
            'clase': clase,
            'fecha': ahora - timedelta(minutes=minutos_atras),
        })
    return sorted(historial, key=lambda paso: paso['fecha'])

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

