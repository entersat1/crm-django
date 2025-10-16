# servicios/forms.py - VERSIÓN SIN CICLO DE IMPORTACIÓN
from django import forms
from .models import OrdenTaller
from django_select2.forms import ModelSelect2Widget

# Importar solo lo esencial - NO importar equipos aquí
from clientes.models import Cliente
from django.contrib.auth.models import User

class ClienteWidget(ModelSelect2Widget):
    search_fields = [
        "nombre__icontains",
        "apellido__icontains",
        "email__icontains",
    ]

# Widget para Equipo - usar string reference
class EquipoWidget(ModelSelect2Widget):
    def __init__(self, *args, **kwargs):
        # Configurar search_fields dinámicamente
        kwargs['search_fields'] = [
            "modelo__icontains", 
            "marca__icontains",
            "numero_serie__icontains",
        ]
        super().__init__(*args, **kwargs)

class TecnicoWidget(ModelSelect2Widget):
    search_fields = [
        "username__icontains",
        "first_name__icontains",
        "last_name__icontains",
    ]

class OrdenTallerForm(forms.ModelForm):
    class Meta:
        model = OrdenTaller
        fields = [
            'cliente', 'equipo', 'tecnico_asignado', 'estado', 'prioridad',
            'accesorios_recibidos', 'problema', 'diagnostico', 'observaciones',
            'costo_mano_obra', 'costo_repuestos', 'presupuesto', 'fecha_entrega_prometida'
        ]

        widgets = {
            "cliente": ClienteWidget(attrs={'data-minimum-input-length': 2}),
            "equipo": EquipoWidget(attrs={'data-minimum-input-length': 2}),
            "tecnico_asignado": TecnicoWidget(attrs={'data-minimum-input-length': 2}),

            'accesorios_recibidos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Cargador, cable, funda, etc.'
            }),
            'problema': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa el problema...'
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Diagnostico tecnico...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'costo_mano_obra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'costo_repuestos': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'presupuesto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'fecha_entrega_prometida': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }