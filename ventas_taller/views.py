<<<<<<< HEAD
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from .models import Venta

def ficha_venta_pdf(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)
    html_string = render_to_string('ventas_taller/ficha_venta.html', {'venta': venta})
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="venta_{venta.id}.pdf"'
    return response
=======
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from .models import Venta

def ficha_venta_pdf(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)
    html_string = render_to_string('ventas_taller/ficha_venta.html', {'venta': venta})
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="venta_{venta.id}.pdf"'
    return response
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
