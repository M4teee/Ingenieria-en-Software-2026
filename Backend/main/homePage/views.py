from django.shortcuts import redirect

def rootHandler(request):
    if not request.user.is_authenticated:
        return redirect('clienteFinal')

    if request.user.is_superuser:
        return redirect('admin:index')

    if request.user.is_staff:
        return redirect('operario:cargar_pedido')

    return redirect('repartidor')
