<<<<<<< HEAD
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Necesitaremos crear el formulario en el siguiente paso
# from .forms import CampanaForm 

@login_required
def crear_campana(request):
    # Por ahora, solo renderizamos una página de ejemplo.
    # La lógica del formulario vendrá después.
    if request.method == 'POST':
        messages.success(request, "Lógica para guardar no implementada aún.")
        return redirect('crear_campana_marketing')
    
=======
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Necesitaremos crear el formulario en el siguiente paso
# from .forms import CampanaForm 

@login_required
def crear_campana(request):
    # Por ahora, solo renderizamos una página de ejemplo.
    # La lógica del formulario vendrá después.
    if request.method == 'POST':
        messages.success(request, "Lógica para guardar no implementada aún.")
        return redirect('crear_campana_marketing')
    
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
    return render(request, 'marketing/crear_campana.html')