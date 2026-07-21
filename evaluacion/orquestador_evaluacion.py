import sys
import json
import time
from pathlib import Path
import cv2
import numpy as np

# Resolvemos la ruta absoluta del archivo actual y subimos un nivel hacia la raíz del proyecto
directorio_actual = Path(__file__).resolve().parent
directorio_raiz = directorio_actual.parent
# Agregamos la raíz al entorno de búsqueda de Python si no está presente
if str(directorio_raiz) not in sys.path:
    sys.path.insert(0, str(directorio_raiz))

# Importación de funciones de mejora de imagen y métricas
from realce.algoritmos import aplicar_ecualizacion_global, aplicar_clahe, aplicar_bhe2pl
from metricas.referenciadas import calcular_psnr, calcular_ambe, calcular_ssim
from metricas.no_referenciadas import calcular_contraste, calcular_entropia

def leer_imagen_robusto(ruta_imagen):
    """
    Lee una imagen desde el disco soportando caracteres especiales en la ruta.

    Utiliza numpy para leer los bytes en crudo y el decodificador de OpenCV
    para evitar los problemas nativos de cv2.imread con tildes en Windows.

    Args:
        ruta_imagen: Cadena de texto o un objeto Path indicando la ubicación del archivo.

    Returns:
        Matriz bidimensional correspondiente a la imagen en escala de grises.
        Genera una excepción si la imagen no se puede decodificar.
    """
    ruta_texto = str(ruta_imagen)
    arreglo_bytes = np.fromfile(ruta_texto, dtype=np.uint8)
    
    if arreglo_bytes.size == 0:
        raise FileNotFoundError(f"No se pudo leer el archivo en la ruta: {ruta_texto}")
        
    imagen_decodificada = cv2.imdecode(arreglo_bytes, cv2.IMREAD_GRAYSCALE)
    
    if imagen_decodificada is None:
        raise ValueError(f"El archivo existe pero no es una imagen válida: {ruta_texto}")
        
    return imagen_decodificada


def aplicar_y_medir_tiempo(funcion_mejora, imagen_gris):
    """
    Ejecuta un algoritmo de mejora de imagen y mide su tiempo de procesamiento.

    Utiliza un contador de rendimiento de alta resolución para garantizar mediciones
    rigurosas de eficiencia computacional.

    Args:
        funcion_mejora: Referencia a la función del algoritmo a ejecutar.
        imagen_gris: Matriz bidimensional de la imagen en escala de grises.

    Returns:
        Tupla que contiene la matriz procesada y un diccionario con el tiempo en milisegundos.
    """
    tiempo_inicio = time.perf_counter()
    imagen_resultante = funcion_mejora(imagen_gris)
    tiempo_fin = time.perf_counter()
    
    tiempo_milisegundos = (tiempo_fin - tiempo_inicio) * 1000.0
    return imagen_resultante, {"tiempo_ms": float(tiempo_milisegundos)}


def ejecutar_pipeline_evaluacion(ruta_originales, ruta_oscurecidas, ruta_salida_img, ruta_archivo_json, ruta_raiz_proyecto):
    """
    Orquesta la ejecución de los experimentos de mejora de imagen sobre el dataset.

    Recorre el directorio de imágenes oscurecidas, aplica las configuraciones de 
    algoritmos definidas, calcula las métricas contrastando con la imagen original 
    (Verdad Terreno), guarda las imágenes resultantes y compila un registro JSON 
    estructurado con rutas relativas para su posterior análisis estadístico.

    Args:
        ruta_originales: Objeto Path al directorio con las imágenes de referencia.
        ruta_oscurecidas: Objeto Path al directorio con las imágenes a procesar.
        ruta_salida_img: Objeto Path al directorio donde se guardarán las imágenes.
        ruta_archivo_json: Objeto Path completo del archivo JSON de salida.
        ruta_raiz_proyecto: Objeto Path que apunta a la raíz del proyecto para 
            calcular las rutas relativas.
    """
    # Crear estructura de directorios de salida dinámicamente
    ruta_salida_img.mkdir(parents=True, exist_ok=True)
    # Crea la carpeta padre del archivo JSON dinámicamente si no existe
    ruta_archivo_json.parent.mkdir(parents=True, exist_ok=True)

    # Definición modular de los experimentos
    configuraciones_experimentos = [
        {
            "id_metodo": "HE_Global",
            "funcion": aplicar_ecualizacion_global,
            "parametros": {}
        },
        {
            "id_metodo": "CLAHE_2_8",
            "funcion": lambda img: aplicar_clahe(img, limite_recorte=2.0, tamano_cuadricula=(8, 8)),
            "parametros": {"limite_contraste": 2.0, "tamano_cuadricula": [8, 8]}
        },
                {
            "id_metodo": "CLAHE_2_4",
            "funcion": lambda img: aplicar_clahe(img, limite_recorte=2.0, tamano_cuadricula=(4, 4)),
            "parametros": {"limite_contraste": 2.0, "tamano_cuadricula": [4, 4]}
        },
                {
            "id_metodo": "CLAHE_4_8",
            "funcion": lambda img: aplicar_clahe(img, limite_recorte=4.0, tamano_cuadricula=(8, 8)),
            "parametros": {"limite_contraste": 4.0, "tamano_cuadricula": [8, 8]}
        },
        {
            "id_metodo": "BHE2PL",
            "funcion": aplicar_bhe2pl,
            "parametros": {}
        }
    ]

    registro_resultados = []

    print("Iniciando procesamiento por lotes del dataset...")
    
    # Iteración sobre los archivos (I/O).
    for ruta_imagen_oscura in ruta_oscurecidas.glob("*.png"):
        nombre_archivo = ruta_imagen_oscura.name
        ruta_imagen_original = ruta_originales / nombre_archivo
        
        if not ruta_imagen_original.exists():
            print(f"Advertencia: Verdad Terreno no encontrada para {nombre_archivo}")
            continue

        # Carga en memoria mediante función robusta para soportar tildes en rutas de Windows
        imagen_oscura = leer_imagen_robusto(ruta_imagen_oscura)
        imagen_referencia = leer_imagen_robusto(ruta_imagen_original)

        # Calcular métricas originales una sola vez por imagen
        contraste_original = calcular_contraste(imagen_referencia)
        entropia_original = calcular_entropia(imagen_referencia)

        # Calcular métricas de la imagen oscura una sola vez por imagen
        psnr_oscurecida = calcular_psnr(imagen_referencia, imagen_oscura)
        ambe_oscurecida = calcular_ambe(imagen_referencia, imagen_oscura)
        ssim_oscurecida = calcular_ssim(imagen_referencia, imagen_oscura)
        contraste_oscurecida = calcular_contraste(imagen_oscura)
        entropia_oscurecida = calcular_entropia(imagen_oscura)

        for config in configuraciones_experimentos:
            metodo = config["id_metodo"]
            
            # Ejecución algorítmica y perfilado de tiempo
            imagen_procesada, metrica_tiempo_procesada = aplicar_y_medir_tiempo(config["funcion"], imagen_oscura)
            
            # Guardado en disco de la imagen resultante
            nombre_base = ruta_imagen_oscura.stem
            nombre_salida = f"{nombre_base}_{metodo}.png"
            ruta_guardado_img = ruta_salida_img / nombre_salida
            cv2.imwrite(str(ruta_guardado_img), imagen_procesada)
            
            # Cálculo de métricas de calidad (referenciadas y no referenciadas)
            psnr_procesada = calcular_psnr(imagen_referencia, imagen_procesada)
            ambe_procesada = calcular_ambe(imagen_referencia, imagen_procesada)
            ssim_procesada = calcular_ssim(imagen_referencia, imagen_procesada)
            contraste_procesada = calcular_contraste(imagen_procesada)
            entropia_procesada = calcular_entropia(imagen_procesada)

            # Construcción del bloque JSON
            registro_resultados.append({
                "id_imagen": nombre_salida,
                "metodo": metodo,
                "parametros": config["parametros"],
                "rutas": {
                    "original": str(ruta_imagen_original.relative_to(ruta_raiz_proyecto).as_posix()),
                    "oscurecida": str(ruta_imagen_oscura.relative_to(ruta_raiz_proyecto).as_posix()),
                    "procesada": str(ruta_guardado_img.relative_to(ruta_raiz_proyecto).as_posix())
                },
                "metricas_imagen_procesada": {
                    **psnr_procesada,
                    **ambe_procesada,
                    **ssim_procesada,
                    **contraste_procesada,
                    **entropia_procesada,
                    **metrica_tiempo_procesada
                },
                "metricas_imagen_oscurecida": {
                    **psnr_oscurecida,
                    **ambe_oscurecida,
                    **ssim_oscurecida,
                    **contraste_oscurecida,
                    **entropia_oscurecida
                },
                "metricas_imagen_original": {
                    **contraste_original,
                    **entropia_original,
                }
            })
            
            print(f"Procesado: {nombre_archivo} | Método: {metodo} | Tiempo: {metrica_tiempo_procesada['tiempo_ms']:.2f} ms")

    # Volcado estructurado de los resultados al disco
    with open(ruta_archivo_json, "w", encoding="utf-8") as archivo_json:
        json.dump(registro_resultados, archivo_json, indent=2, ensure_ascii=False)
        
    print(f"\nEvaluación finalizada. Resultados exportados en: {ruta_archivo_json}")


if __name__ == "__main__":
    # DEFINICIÓN DE CONSTANTES ESTRUCTURALES Y NOMBRES
    NOMBRE_CARPETA_DATASET = "dataset"
    NOMBRE_CARPETA_EXPERIMENTOS = "experimento"
    
    NOMBRE_CARPETA_IMG = "img"
    NOMBRE_CARPETA_ORIGINAL = "original"
    NOMBRE_CARPETA_OSCURECIDA = "oscurecida"
    NOMBRE_CARPETA_JSON = "json"
    
    NOMBRE_ARCHIVO_JSON = "resultados_evaluacion.json"

    # Configuración de rutas base dinámicas
    directorio_actual = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    directorio_raiz_proyecto = directorio_actual.parent
    
    directorio_base_dataset = directorio_raiz_proyecto / NOMBRE_CARPETA_DATASET
    directorio_base_experimentos = directorio_raiz_proyecto / NOMBRE_CARPETA_EXPERIMENTOS
    
    # Composición de rutas de entrada (Lectura)
    ruta_entrada_originales = directorio_base_dataset / NOMBRE_CARPETA_IMG / NOMBRE_CARPETA_ORIGINAL
    ruta_entrada_oscurecidas = directorio_base_dataset / NOMBRE_CARPETA_IMG / NOMBRE_CARPETA_OSCURECIDA
    
    # Composición de rutas de salida (Escritura)
    ruta_salida_imagenes = directorio_base_experimentos / NOMBRE_CARPETA_IMG
    ruta_salida_archivo_json = directorio_base_experimentos / NOMBRE_CARPETA_JSON / NOMBRE_ARCHIVO_JSON
    
    # Inyección de dependencias a la función principal, incluyendo la raíz del proyecto
    ejecutar_pipeline_evaluacion(
        ruta_entrada_originales, 
        ruta_entrada_oscurecidas, 
        ruta_salida_imagenes, 
        ruta_salida_archivo_json,
        directorio_raiz_proyecto
    )