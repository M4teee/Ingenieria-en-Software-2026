from django.shortcuts import redirect

from main.clienteFinal.views import form as formulario_cliente


def _es_repartidor(user):
    return (
        user.is_authenticated
        and hasattr(user, 'repartidor')
        and user.repartidor.user.is_active
    )


def rootHandler(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('operario:inicio')

    if _es_repartidor(request.user):
        return redirect('repartidor')

    return formulario_cliente(request)
