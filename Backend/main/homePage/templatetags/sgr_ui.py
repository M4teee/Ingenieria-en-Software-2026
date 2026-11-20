"""Etiquetas de presentación del sistema de diseño SGR.

Solo transforman datos ya disponibles en la plantilla (estado, nombres) en
estructuras de UI. No consultan la base ni cambian reglas de negocio.
"""

from django import template
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()

# Recorrido normal de un pedido (Pedido.TRANSICIONES_PERMITIDAS).
RECORRIDO = [
    ('registrado', 'Registrado'),
    ('asignado', 'Asignado'),
    ('retirado', 'Retirado'),
    ('en_viaje', 'En viaje'),
    ('entregado', 'Entregado'),
]

ICONOS_ESTADO = {
    'registrado': 'circle-dot',
    'asignado': 'user',
    'retirado': 'package',
    'en_viaje': 'truck',
    'entregado': 'circle-check',
    'fallido': 'circle-x',
    'cancelado': 'ban',
}

ICONOS_VEHICULO = {
    'bicicleta': 'bike',
    'moto': 'bike',
    'auto': 'car',
    'camion': 'truck',
}

DESCRIPCION_PUBLICA = {
    'registrado': 'El comercio registró tu pedido. Pronto se le asignará un repartidor.',
    'asignado': 'Un repartidor tiene asignado tu pedido y va a retirarlo del comercio.',
    'retirado': 'El repartidor retiró tu pedido del comercio.',
    'en_viaje': 'Tu pedido está en camino a la dirección de entrega.',
    'entregado': 'Tu pedido fue entregado.',
    'fallido': 'No se pudo completar la entrega. El comercio va a contactarte.',
    'cancelado': 'El pedido fue cancelado.',
}


@register.simple_tag
def icon(nombre, clase=''):
    """SVG del sprite de Lucide; siempre decorativo (el texto acompaña)."""
    return format_html(
        '<svg class="icon {}" aria-hidden="true" focusable="false"><use href="{}#i-{}"></use></svg>',
        clase,
        static('sgr/icons.svg'),
        nombre,
    )


@register.filter
def icono_estado(estado):
    return ICONOS_ESTADO.get(estado, 'circle-dot')


@register.filter
def icono_vehiculo(vehiculo):
    return ICONOS_VEHICULO.get(vehiculo, 'truck')


@register.filter
def descripcion_publica(estado):
    return DESCRIPCION_PUBLICA.get(estado, '')


@register.filter
def iniciales(valor):
    """Iniciales de un usuario (nombre completo o usuario) o de un texto."""
    if hasattr(valor, 'get_username'):
        valor = valor.get_full_name() or valor.get_username()
    partes = str(valor).split()
    return ''.join(parte[0] for parte in partes[:2]).upper()


TITULO_PUBLICO = {
    'fallido': 'No se pudo entregar',
}


@register.filter
def titulo_publico(estado_clave, etiqueta=''):
    """Titular para el cliente: evita la jerga interna en el estado fallido."""
    return TITULO_PUBLICO.get(estado_clave, etiqueta)


@register.simple_tag
def pasos_estado(estado):
    """Lista de pasos del recorrido con su condición: hecho, actual, pendiente.

    Fallido y cancelado se muestran como paso final en lugar de "Entregado",
    a continuación del último paso alcanzable desde ese estado.
    """
    claves = [clave for clave, _ in RECORRIDO]
    if estado in claves:
        actual = claves.index(estado)
        return [
            {
                'clave': clave,
                'etiqueta': etiqueta,
                'condicion': 'hecho' if i < actual else 'actual' if i == actual else 'pendiente',
                'final': estado == 'entregado' and i == actual,
            }
            for i, (clave, etiqueta) in enumerate(RECORRIDO)
        ]

    # Fallido ocurre desde "en viaje"; cancelado, desde registrado/asignado.
    previos = RECORRIDO[:4] if estado == 'fallido' else RECORRIDO[:1]
    pasos = [
        {'clave': clave, 'etiqueta': etiqueta, 'condicion': 'hecho', 'final': False}
        for clave, etiqueta in previos
    ]
    pasos.append({
        'clave': estado,
        'etiqueta': 'Fallido' if estado == 'fallido' else 'Cancelado',
        'condicion': 'actual',
        'final': True,
    })
    return pasos
