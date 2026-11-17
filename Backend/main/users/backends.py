from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


class CachedModelBackend(ModelBackend):
    """
    Backend de autenticación que cachea la consulta de get_user en memoria local
    para evitar una consulta SQL redundante en cada petición HTTP.
    Se invalida automáticamente cuando el usuario es modificado o eliminado.
    """
    def get_user(self, user_id):
        cache_key = f"auth_user_{user_id}"
        user = cache.get(cache_key)
        if user is None:
            try:
                user = get_user_model()._default_manager.get(pk=user_id)
                cache.set(cache_key, user, timeout=300)
            except get_user_model().DoesNotExist:
                return None
        return user


@receiver(post_save)
def _invalidar_cache_usuario(sender, instance, **kwargs):
    if sender == get_user_model():
        cache.delete(f"auth_user_{instance.pk}")


@receiver(post_delete)
def _invalidar_cache_usuario_delete(sender, instance, **kwargs):
    if sender == get_user_model():
        cache.delete(f"auth_user_{instance.pk}")
