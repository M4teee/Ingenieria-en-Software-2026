from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta
from main.operario.models import Comercio
from main.repartidor.models import Pedido, Repartidor
from main.users.models import User


MENSAJE_COMERCIO_INACTIVO = (
    'El comercio seleccionado se encuentra inhabilitado para nuevos pedidos'
)

MARGEN_FECHA_ENTREGA = timedelta(minutes=10)

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
        # El navegador no sugiere fechas/horas anteriores al momento actual
        ahora = timezone.localtime(timezone.now())
        self.fields['fecha_hora_estimada_entrega'].widget.attrs['min'] = (
            ahora.strftime('%Y-%m-%dT%H:%M')
        )

    def clean_fecha_hora_estimada_entrega(self):
        fecha_hora = self.cleaned_data['fecha_hora_estimada_entrega']
        if fecha_hora < timezone.now() - MARGEN_FECHA_ENTREGA:
            raise ValidationError(
                'La fecha y hora estimadas de entrega no pueden ser anteriores al momento actual.'
            )
        return fecha_hora

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


class RepartidorForm(forms.Form):
    usuario = forms.CharField(
        max_length=150,
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username'}),
    )
    nombre = forms.CharField(
        max_length=150,
        required=False,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'given-name'}),
    )
    apellido = forms.CharField(
        max_length=150,
        required=False,
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'family-name'}),
    )
    email = forms.EmailField(
        required=False,
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
    )
    vehiculo = forms.ChoiceField(
        choices=[('', 'Seleccioná un vehículo'), *Repartidor.VEHICULOS],
        label='Vehículo',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    pin = forms.CharField(
        max_length=4,
        min_length=4,
        label='PIN de 4 dígitos',
        validators=[RegexValidator(
            regex=r'^\d{4}$',
            message='El PIN debe contener exactamente 4 dígitos numéricos.',
        )],
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'inputmode': 'numeric', 'autocomplete': 'new-password'},
        ),
    )

    def clean_usuario(self):
        usuario = self.cleaned_data['usuario']
        if User.objects.filter(username__iexact=usuario).exists():
            raise ValidationError('Ya existe un usuario con ese nombre.')
        return usuario

    def clean_pin(self):
        pin = self.cleaned_data['pin']
        if Repartidor.objects.filter(pin=pin).exists():
            raise ValidationError('Ese PIN ya está asignado a otro repartidor.')
        return pin


class ComercioForm(forms.ModelForm):
    activo = forms.TypedChoiceField(
        choices=[
            ('', 'Seleccioná un estado'),
            ('true', 'Activo'),
            ('false', 'Inactivo'),
        ],
        coerce=lambda valor: valor == 'true',
        empty_value=None,
        label='Activo',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Comercio
        fields = ('nombre', 'direccion', 'contacto', 'activo')
        labels = {
            'nombre': 'Nombre',
            'direccion': 'Dirección',
            'contacto': 'Contacto',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
        }
