import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

def evaluar_modelo_vs_gold(df_predicciones, df_gold):
    entidades = [
        'factura_num', 'fecha', 'empresa', 'rut_empresa', 'dir_empresa',
        'cliente', 'rut_cliente', 'dir_cliente', 'producto', 'cantidad',
        'precio_unitario', 'subtotal_item', 'total_neto', 'iva', 'total_final'
    ]
    resultados_por_entidad = []
    y_true_all = []
    y_pred_all = []

    for entidad in entidades:
        y_t = df_gold[entidad].astype(str).str.strip().str.upper().tolist()
        y_p = df_predicciones[entidad].astype(str).str.strip().str.upper().tolist()

        aciertos = sum(1 for t, p in zip(y_t, y_p) if t == p)
        total = len(y_t)

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_t, y_p, average='micro', zero_division=0
        )

        resultados_por_entidad.append({
            'Entidad': entidad,
            'Precision': round(precision, 4),
            'Recall': round(recall, 4),
            'F1-Score': round(f1, 4),
            'Accuracy Campo': f"{aciertos}/{total} ({round(aciertos/total*100, 1)}%)"
        })

        y_true_all.extend(y_t)
        y_pred_all.extend(y_p)

    df_res = pd.DataFrame(resultados_por_entidad)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true_all, y_pred_all, average='macro', zero_division=0
    )

    return df_res, (p_macro, r_macro, f1_macro)