import re
from datetime import datetime

def validar_rut(rut_str):
    if not rut_str:
        return None
    rut_limpio = re.sub(r'[^0-9kK]', '', str(rut_str)).upper()
    if len(rut_limpio) < 2:
        return None
    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]
    suma = 0
    multiplicador = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = suma % 11
    dv_calculado = 11 - resto
    dv_esperado = '0' if dv_calculado == 11 else ('K' if dv_calculado == 10 else str(dv_calculado))
    return f"{cuerpo}-{dv_ingresado}"

def normalizar_fecha(fecha_str):
    if not fecha_str:
        return None
    formatos = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"]
    fecha_limpia = str(fecha_str).strip()
    for fmt in formatos:
        try:
            return datetime.strptime(fecha_limpia, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return fecha_limpia

def normalizar_monto(monto_str):
    if not monto_str:
        return 0.0
    monto_limpio = re.sub(r'[^\d,-]', '', str(monto_str)).replace('.', '').replace(',', '.')
    try:
        return float(monto_limpio)
    except ValueError:
        return 0.0