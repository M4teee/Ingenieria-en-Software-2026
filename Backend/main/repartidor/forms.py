from PIL import Image, UnidentifiedImageError
from django import forms
from django.core.exceptions import ValidationError


MAX_FOTOGRAFIA_BYTES = 10 * 1024 * 1024
FORMATOS_FOTOGRAFIA = {'JPEG', 'PNG', 'WEBP'}


class ActualizarEstadoForm(forms.Form):
    estado = forms.CharField()
    fotografia = forms.ImageField(required=False)

    def clean_fotografia(self):
        fotografia = self.cleaned_data.get('fotografia')
        if fotografia is None:
            return None

        if fotografia.size > MAX_FOTOGRAFIA_BYTES:
            raise ValidationError('La fotografía no puede superar los 10 MB.')

        try:
            fotografia.seek(0)
            with Image.open(fotografia) as imagen:
                if imagen.format not in FORMATOS_FOTOGRAFIA:
                    raise ValidationError('Usá una imagen JPEG, PNG o WebP válida.')
                imagen.verify()
        except ValidationError:
            raise
        except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as error:
            raise ValidationError('El archivo no es una imagen válida.') from error
        finally:
            fotografia.seek(0)

        return fotografia
