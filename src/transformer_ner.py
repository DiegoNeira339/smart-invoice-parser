import re

def extraer_entidades_transformer(texto):
    factura_num = re.search(r'FACTURA:\s*([^\n]+)', texto)
    fecha = re.search(r'Fecha:\s*([^\n]+)', texto)
    empresa = re.search(r'Empresa:\s*([^\n]+?)(?=\s*RUT:|$)', texto)
    rut_empresa = re.search(r'Empresa:.*?RUT:\s*([^\n]+)', texto)
    dir_empresa = re.search(r'Dirección:\s*([^\n]+)', texto)

    cliente_match = re.search(r'Datos del Cliente:\s*\nNombre:\s*([^\n]+)\nRUT:\s*([^\n]+)\nDirección:\s*([^\n]+)', texto)

    total_neto = re.search(r'Total Neto:\s*([^\n]+)', texto)
    iva = re.search(r'IVA:\s*([^\n]+)', texto)
    total_final = re.search(r'Total Final:\s*([^\n]+)', texto)

    # Extraer todas las filas de la tabla de detalle
    items_block = re.search(r'Subtotal\n(.*?)\nTotal Neto:', texto, re.DOTALL)
    items_lines = [l.strip() for l in items_block.group(1).strip().split('\n') if l.strip()] if items_block else []

    items = []
    i = 0
    while i < len(items_lines):
        if i + 3 < len(items_lines) and items_lines[i+1].isdigit() and '$' in items_lines[i+2]:
            items.append({
                'producto': items_lines[i],
                'cantidad': items_lines[i+1],
                'precio_unitario': items_lines[i+2],
                'subtotal_item': items_lines[i+3]
            })
            i += 4
        else:
            i += 1

    # Ítem principal para el resumen plano
    primer_item = items[0] if items else {'producto': '', 'cantidad': '1', 'precio_unitario': '', 'subtotal_item': ''}

    return {
        'factura_num': factura_num.group(1).strip() if factura_num else '',
        'fecha': fecha.group(1).strip() if fecha else '',
        'empresa': empresa.group(1).strip() if empresa else '',
        'rut_empresa': rut_empresa.group(1).strip() if rut_empresa else '',
        'dir_empresa': dir_empresa.group(1).strip() if dir_empresa else '',
        'cliente': cliente_match.group(1).strip() if cliente_match else '',
        'rut_cliente': cliente_match.group(2).strip() if cliente_match else '',
        'dir_cliente': cliente_match.group(3).strip() if cliente_match else '',
        'producto': primer_item['producto'],
        'cantidad': primer_item['cantidad'],
        'precio_unitario': primer_item['precio_unitario'],
        'subtotal_item': primer_item['subtotal_item'],
        'items': items,  # Lista completa de ítems para SQLite
        'total_neto': total_neto.group(1).strip() if total_neto else '',
        'iva': iva.group(1).strip() if iva else '',
        'total_final': total_final.group(1).strip() if total_final else ''
    }