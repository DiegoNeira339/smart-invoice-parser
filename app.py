import os
import re
import tempfile
import random
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from src.pdf_parser import extraer_texto_pdf
from src.transformer_ner import extraer_entidades_transformer
from src.normalizer import validar_rut, normalizar_fecha, normalizar_monto
from src.database import inicializar_bd, guardar_factura

app = Flask(__name__)
CORS(app)

# Inicializar Base de Datos SQLite al arrancar
inicializar_bd()

# Listas de datos dinámicos para boletas en tiempo real
EMPRESAS = [
    ("EnerJom SpA", "76.123.456-0", "Av. Pajaritos 3000, Maipú"),
    ("TechNova Chile S.A.", "76.543.210-5", "Av. Providencia 1020, Providencia"),
    ("DataCorp Consultores", "80.123.900-6", "San Martín 240, Valparaíso"),
    ("InnoTech Solutions", "77.654.321-1", "Alonso de Córdova 5000, Las Condes"),
]

CLIENTES = [
    ("ClienteCorp S.A.", "96.888.777-7", "Av. Apoquindo 4500, Las Condes"),
    ("Servicios El Norte", "22.444.555-6", "Calle 3 #45, Antofagasta"),
    ("Comercial Los Andes", "21.345.678-0", "Av. Los Héroes 100, Santiago"),
]

PRODUCTOS = [
    ("Monitoreo IoT EnerJom", 150000),
    ("Pinza Inductiva SEC", 50000),
    ("Licencia Software Anual", 120000),
    ("Servicio Mantenimiento", 80000),
    ("Consultoría Técnica (hrs)", 45000),
]

FECHAS = ["14/11/2026", "10/11/2026", "05/11/2026", "01/11/2026"]

def obtener_siguiente_numero(directorio="data/pdfs"):
    os.makedirs(directorio, exist_ok=True)
    archivos = os.listdir(directorio)
    numeros = []
    for f in archivos:
        match = re.match(r"doc_(\d+)\.pdf", f)
        if match:
            numeros.append(int(match.group(1)))
    return max(numeros) + 1 if numeros else 31

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "ok", "message": "Backend Flask EP3 en ejecución"}), 200

@app.route('/api/process-invoice', methods=['POST'])
def process_invoice():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo PDF"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)

    try:
        texto = extraer_texto_pdf(temp_path)
        entidades = extraer_entidades_transformer(texto)
        
        rut_empresa_valido = validar_rut(entidades.get('rut_empresa'))
        rut_cliente_valido = validar_rut(entidades.get('rut_cliente'))

        datos_factura = {
            'archivo_origen': file.filename,
            'factura_num': entidades.get('factura_num'),
            'fecha': normalizar_fecha(entidades.get('fecha')),
            'empresa_nombre': entidades.get('empresa'),
            'empresa_rut': rut_empresa_valido,
            'empresa_direccion': entidades.get('dir_empresa'),
            'cliente_nombre': entidades.get('cliente'),
            'cliente_rut': rut_cliente_valido,
            'cliente_direccion': entidades.get('dir_cliente'),
            'total_neto': normalizar_monto(entidades.get('total_neto')),
            'iva': normalizar_monto(entidades.get('iva')),
            'total_final': normalizar_monto(entidades.get('total_final'))
        }

        items_factura = []
        for it in entidades.get('items', []):
            items_factura.append({
                'producto': it.get('producto'),
                'cantidad': int(it.get('cantidad', 1) if str(it.get('cantidad')).isdigit() else 1),
                'precio_unitario': normalizar_monto(it.get('precio_unitario')),
                'subtotal_item': normalizar_monto(it.get('subtotal_item'))
            })

        guardar_factura(datos_factura, items_factura)

        return jsonify({
            "success": True,
            "filename": file.filename,
            "normalized_data": datos_factura,
            "items": items_factura,
            "validations": {
                "rut_empresa_valido": rut_empresa_valido is not None,
                "rut_cliente_valido": rut_cliente_valido is not None
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/api/generate-invoice', methods=['POST'])
def generate_invoice():
    try:
        siguiente_num = obtener_siguiente_numero()
        num_str = f"{siguiente_num:03d}"
        output_dir = os.path.join("data", "pdfs")
        output_path = os.path.join(output_dir, f"doc_{num_str}.pdf")

        empresa, rut_emp, dir_emp = random.choice(EMPRESAS)
        cliente, rut_cli, dir_cli = random.choice(CLIENTES)
        prod_nombre, precio_u = random.choice(PRODUCTOS)
        cantidad = random.randint(1, 4)
        fecha = random.choice(FECHAS)

        subtotal = cantidad * precio_u
        neto = subtotal
        iva = int(round(neto * 0.19))
        total_final = neto + iva

        # Generar PDF Vectorial en disco
        c = canvas.Canvas(output_path, pagesize=letter)
        _, height = letter
        text = c.beginText()
        text.setTextOrigin(50, height - 60)
        text.setFont("Helvetica", 10)

        lineas = [
            f"FACTURA: F-2026-{num_str}",
            f"Fecha: {fecha}",
            f"Empresa: {empresa} RUT: {rut_emp}",
            f"Dirección: {dir_emp}",
            "",
            "Datos del Cliente:",
            f"Nombre: {cliente}",
            f"RUT: {rut_cli}",
            f"Dirección: {dir_cli}",
            "",
            "Detalle de Productos / Servicios:",
            "Producto Cantidad Precio Subtotal",
            "Subtotal",
            f"{prod_nombre}",
            f"{cantidad}",
            f"${precio_u:,}".replace(",", "."),
            f"${subtotal:,}".replace(",", "."),
            f"Total Neto: ${neto:,}".replace(",", "."),
            f"IVA: ${iva:,}".replace(",", "."),
            f"Total Final: ${total_final:,}".replace(",", ".")
        ]

        for line in lineas:
            text.textLine(line)

        c.drawText(text)
        c.save()

        # Extraer entidades e insertar en BD
        texto = extraer_texto_pdf(output_path)
        entidades = extraer_entidades_transformer(texto)

        rut_empresa_valido = validar_rut(entidades.get('rut_empresa'))
        rut_cliente_valido = validar_rut(entidades.get('rut_cliente'))

        datos_factura = {
            'archivo_origen': f"doc_{num_str}.pdf",
            'factura_num': entidades.get('factura_num'),
            'fecha': normalizar_fecha(entidades.get('fecha')),
            'empresa_nombre': entidades.get('empresa'),
            'empresa_rut': rut_empresa_valido,
            'empresa_direccion': entidades.get('dir_empresa'),
            'cliente_nombre': entidades.get('cliente'),
            'cliente_rut': rut_cliente_valido,
            'cliente_direccion': entidades.get('dir_cliente'),
            'total_neto': normalizar_monto(entidades.get('total_neto')),
            'iva': normalizar_monto(entidades.get('iva')),
            'total_final': normalizar_monto(entidades.get('total_final'))
        }

        items_factura = []
        for it in entidades.get('items', []):
            items_factura.append({
                'producto': it.get('producto'),
                'cantidad': int(it.get('cantidad', 1) if str(it.get('cantidad')).isdigit() else 1),
                'precio_unitario': normalizar_monto(it.get('precio_unitario')),
                'subtotal_item': normalizar_monto(it.get('subtotal_item'))
            })

        guardar_factura(datos_factura, items_factura)

        return jsonify({
            "success": True,
            "filename": f"doc_{num_str}.pdf",
            "normalized_data": datos_factura,
            "items": items_factura,
            "validations": {
                "rut_empresa_valido": rut_empresa_valido is not None,
                "rut_cliente_valido": rut_cliente_valido is not None
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask en http://127.0.0.1:5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)