from django import forms
from django.core.exceptions import ValidationError

from main.operario.models import Comercio
from main.repartidor.models import Pedido, Repartidor


MENSAJE_COMERCIO_INACTIVO = (
    'El comercio seleccionado se encuentra inhabilitado para nuevos pedidos'
)


class ComercioActivoField(forms.ModelChoiceField):
    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            comercio = Comercio.objects.get(pk=value)
        except (Comercio.DoesNotExist, TypeError, ValueError):
            return super().to_python(value)

        if not comercio.activo:
            raise ValidationError(self.error_messages['inactive'], code='inactive')

        return super().to_python(value)


class PedidoForm(forms.Form):
    clave_idempotencia = forms.UUIDField(widget=forms.HiddenInput)
    comercio = ComercioActivoField(
        queryset=Comercio.objects.filter(activo=True),
        label='Comercio',
        error_messages={'inactive': MENSAJE_COMERCIO_INACTIVO},
    )
    direccion_destino = forms.CharField(
        max_length=255,
        label='Dirección de destino',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'street-address'}),
    )
    especificaciones_traslado = forms.CharField(
        label='Especificaciones de traslado',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
    fecha_hora_estimada_entrega = forms.DateTimeField(
        label='Fecha y hora estimadas de entrega',
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comercio'].widget.attrs['class'] = 'form-select'


class AsignarPedidoForm(forms.Form):
    repartidor = forms.ModelChoiceField(
        queryset=Repartidor.objects.none(),
        label='Repartidor disponible',
        empty_label='Seleccioná un repartidor',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        activos = Pedido.objects.filter(
            estado__in=('asignado', 'retirado', 'en_viaje'),
            repartidor__isnull=False,
        ).values('repartidor_id')
        self.fields['repartidor'].queryset = (
            Repartidor.objects.select_related('user')
            .filter(disponible=True, user__is_active=True)
            .exclude(user_id__in=activos)
            .order_by('user__username')
        )
