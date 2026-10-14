from django.shortcuts import redirect

def rootHandler(request):
    if not request.user.is_authenticated:
        return redirect('clienteFinal')

    if request.user.is_superuser:
        return redirect('admin:index')

    return redirect('repartidor')