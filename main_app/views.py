from django.shortcuts import render, redirect
from django.contrib import messages
from.forms import Contactanos

#Vistas de usuario.
def home(request):
    return render(request, 'index.html')

def servicios(request):
    return render(request, 'servicios.html')

def contacto(request):
    if request.method == 'POST':
        form = Contactanos(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.')
            return redirect('contacto')
    else:
        form = Contactanos()
    
    return render(request, 'contactanos.html', {'form': form})

def login(request):
    return render(request, 'login.html')