import os
import glob
import pypdf

def extraer_texto_pdf(ruta_pdf):
    reader = pypdf.PdfReader(ruta_pdf)
    texto = "\n".join([pagina.extract_text() for pagina in reader.pages if pagina.extract_text()])
    return texto.strip()

def cargar_todas_las_facturas(carpeta_base):
    facturas_texto = {}
    # Busca archivos .pdf en la carpeta y en cualquier subcarpeta
    patron = os.path.join(carpeta_base, '**', '*.pdf')
    archivos = sorted(glob.glob(patron, recursive=True))
    
    # Si no encontró en la carpeta base, busca en todo el proyecto
    if not archivos:
        archivos = sorted(glob.glob('**/*.pdf', recursive=True))
        # Filtrar posibles PDFs de la pauta o instrucciones
        archivos = [f for f in archivos if 'doc_' in os.path.basename(f)]

    for archivo in archivos:
        nombre_base = os.path.basename(archivo)
        facturas_texto[nombre_base] = extraer_texto_pdf(archivo)
        
    return facturas_texto