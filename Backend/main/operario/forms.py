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

MENSAJE_COMERCIO_DUPLICADO = 'Ya existe un comercio registrado con ese nombre'

MARGEN_FECHA_ENTREGA = timedelta(minutes=10)

MENSAJE_VEHICULO_INCOMPATIBLE = (
    'El repartidor seleccionado no posee el vehículo requerido por el pedido.'
)


def _repartidores_disponibles():
    ocupados = Pedido.objects.filter(
        estado__in=('asignado', 'retirado', 'en_viaje'),
        repartidor__isnull=False,
    ).values('repartidor_id')
    return (
        Repartidor.objects.select_related('user')
        .filter(disponible=True, user__is_active=True)
        .exclude(user_id__in=ocupados)
    )


class RepartidorSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vehiculos = {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs,
        )
        vehiculo = self.vehiculos.get(str(value))
        if vehiculo:
            option['attrs']['data-vehiculo'] = vehiculo
        return option


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
    datos_destinatario = forms.CharField(
        label='Datos del destinatario',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    )
    tamano_paquete = forms.CharField(
        label='Tamaño del paquete',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    )
    vehiculo_requerido = forms.ChoiceField(
        choices=Repartidor.VEHICULOS,
        label='Vehículo requerido',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    repartidor = forms.ModelChoiceField(
        queryset=Repartidor.objects.none(),
        label='Repartidor',
        required=False,
        empty_label='Automático',
        widget=RepartidorSelect(attrs={'class': 'form-select'}),
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
        disponibles = _repartidores_disponibles().order_by('user__username')
        self.fields['repartidor'].queryset = disponibles
        self.fields['repartidor'].widget.vehiculos = {
            str(perfil.pk): perfil.vehiculo for perfil in disponibles
        }

    def clean_fecha_hora_estimada_entrega(self):
        fecha_hora = self.cleaned_data['fecha_hora_estimada_entrega']
        if fecha_hora < timezone.now() - MARGEN_FECHA_ENTREGA:
            raise ValidationError(
                'La fecha y hora estimadas de entrega no pueden ser anteriores al momento actual.'
            )
        return fecha_hora

    def clean_repartidor(self):
        perfil = self.cleaned_data.get('repartidor')
        if perfil is None:
            return None
        vehiculo = self.cleaned_data.get('vehiculo_requerido')
        if perfil.vehiculo != vehiculo:
            raise ValidationError(MENSAJE_VEHICULO_INCOMPATIBLE)
        return perfil

class AsignarPedidoForm(forms.Form):
    repartidor = forms.ModelChoiceField(
        queryset=Repartidor.objects.none(),
        label='Repartidor disponible',
        required=False,
        empty_label='Automático',
        widget=RepartidorSelect(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        pedido = kwargs.pop('pedido', None)
        super().__init__(*args, **kwargs)
        queryset = _repartidores_disponibles()
        if pedido is not None:
            vehiculo = pedido.vehiculo_requerido
            if vehiculo in dict(Repartidor.VEHICULOS):
                queryset = queryset.filter(vehiculo=vehiculo)
        self.fields['repartidor'].queryset = queryset.order_by('user__username')


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
    dni = forms.CharField(
        max_length=8,
        min_length=8,
        label='DNI',
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='El DNI debe contener 8 dígitos numéricos.',
        )],
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'inputmode': 'numeric', 'autocomplete': 'off'},
        ),
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

    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if Repartidor.objects.filter(dni=dni).exists():
            raise ValidationError('El DNI ingresado ya se encuentra registrado en el sistema.')
        return dni
    
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
            'contacto': 'Teléfono de contacto', # Actualizado según la HU
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'nombre': {'unique': MENSAJE_COMERCIO_DUPLICADO},
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        duplicados = Comercio.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise ValidationError(MENSAJE_COMERCIO_DUPLICADO, code='unique')
        return nombre