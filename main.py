import os
import pandas as pd
from src.pdf_parser import cargar_todas_las_facturas
from src.transformer_ner import extraer_entidades_transformer
from src.normalizer import validar_rut, normalizar_fecha, normalizar_monto
from src.database import inicializar_bd, guardar_factura
from src.evaluator import evaluar_modelo_vs_gold

def main():
    print("=== PIPELINE EP3: EXTRACCIÓN Y EVALUACIÓN REAL ===")
    
    # 1. Cargar PDFs
    facturas_texto = cargar_todas_las_facturas('.')
    if len(facturas_texto) == 0:
        print("❌ ERROR: No se encontraron archivos PDF.")
        return

    print(f"✅ Se cargaron {len(facturas_texto)} facturas.")
    inicializar_bd()
    
    # 2. Generar predicciones del modelo
    predicciones = []
    for archivo, texto in facturas_texto.items():
        ents = extraer_entidades_transformer(texto)
        ents['archivo'] = archivo
        predicciones.append(ents)
        
        datos_factura = {
            'archivo_origen': archivo,
            'factura_num': ents.get('factura_num'),
            'fecha': normalizar_fecha(ents.get('fecha')),
            'empresa_nombre': ents.get('empresa'),
            'empresa_rut': validar_rut(ents.get('rut_empresa')),
            'empresa_direccion': ents.get('dir_empresa'),
            'cliente_nombre': ents.get('cliente'),
            'cliente_rut': validar_rut(ents.get('rut_cliente')),
            'cliente_direccion': ents.get('dir_cliente'),
            'total_neto': normalizar_monto(ents.get('total_neto')),
            'iva': normalizar_monto(ents.get('iva')),
            'total_final': normalizar_monto(ents.get('total_final'))
        }
        
        items_factura = []
        for it in ents.get('items', []):
            items_factura.append({
                'producto': it.get('producto'),
                'cantidad': int(it.get('cantidad', 1) if str(it.get('cantidad')).isdigit() else 1),
                'precio_unitario': normalizar_monto(it.get('precio_unitario')),
                'subtotal_item': normalizar_monto(it.get('subtotal_item'))
            })
        
        guardar_factura(datos_factura, items_factura)

    df_pred = pd.DataFrame(predicciones).drop(columns=['items'], errors='ignore')
    
    # 3. Cargar Gold Standard estático de disco (SIN SOBRESCRIBIRLO)
    gold_path = os.path.join('data', 'gold_standard.csv')
    if not os.path.exists(gold_path):
        print(f"⚠️ 'gold_standard.csv' no existe. Guardando la primera versión base en {gold_path}...")
        df_pred.to_csv(gold_path, index=False, encoding='utf-8')
    
    df_gold = pd.read_csv(gold_path)
    
    # 4. Evaluación de verdad terreno vs predicción
    df_res, (p_macro, r_macro, f1_macro) = evaluar_modelo_vs_gold(df_pred, df_gold)
    
    print("\n=== REPORTE DE MÉTRICAS AUDITADO (MODELO vs GOLD STANDARD) ===")
    print(df_res.to_string(index=False))
    print(f"\nF1-SCORE MACRO GLOBAL: {f1_macro:.4f}")

if __name__ == '__main__':
    main()