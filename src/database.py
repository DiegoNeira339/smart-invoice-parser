import sqlite3

def inicializar_bd(ruta_db="data/facturas.db"):
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        archivo_origen TEXT UNIQUE,
        factura_num TEXT,
        fecha TEXT,
        empresa_nombre TEXT,
        empresa_rut TEXT,
        empresa_direccion TEXT,
        cliente_nombre TEXT,
        cliente_rut TEXT,
        cliente_direccion TEXT,
        total_neto REAL,
        iva REAL,
        total_final REAL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_facturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        factura_id INTEGER,
        producto TEXT,
        cantidad INTEGER,
        precio_unitario REAL,
        subtotal_item REAL,
        FOREIGN KEY (factura_id) REFERENCES facturas (id)
    )
    """)
    conn.commit()
    conn.close()

def guardar_factura(datos_factura, items_factura, ruta_db="data/facturas.db"):
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO facturas (
        archivo_origen, factura_num, fecha, empresa_nombre, empresa_rut, empresa_direccion,
        cliente_nombre, cliente_rut, cliente_direccion, total_neto, iva, total_final
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datos_factura.get('archivo_origen'),
        datos_factura.get('factura_num'),
        datos_factura.get('fecha'),
        datos_factura.get('empresa_nombre'),
        datos_factura.get('empresa_rut'),
        datos_factura.get('empresa_direccion'),
        datos_factura.get('cliente_nombre'),
        datos_factura.get('cliente_rut'),
        datos_factura.get('cliente_direccion'),
        datos_factura.get('total_neto', 0.0),
        datos_factura.get('iva', 0.0),
        datos_factura.get('total_final', 0.0)
    ))
    factura_id = cursor.lastrowid

    for item in items_factura:
        cursor.execute("""
        INSERT INTO detalle_facturas (factura_id, producto, cantidad, precio_unitario, subtotal_item)
        VALUES (?, ?, ?, ?, ?)
        """, (
            factura_id,
            item.get('producto'),
            item.get('cantidad', 1),
            item.get('precio_unitario', 0.0),
            item.get('subtotal_item', 0.0)
        ))
    conn.commit()
    conn.close()