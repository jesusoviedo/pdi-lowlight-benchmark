import json
import time
from pathlib import Path
import cv2
import numpy as np

# Importación de funciones de mejora de imagen y métricas
from realce.algoritmos import aplicar_ecualizacion_global, aplicar_clahe, aplicar_bhe2pl
from metricas.referenciadas import calcular_psnr, calcular_ambe, calcular_ssim
from metricas.no_referenciadas import calcular_contraste, calcular_entropia

def aplicar_y_medir_tiempo(funcion_mejora, imagen_gris):
    """
    Ejecuta un algoritmo de mejora de imagen y mide su tiempo de procesamiento.

    Utiliza un contador de rendimiento de alta resolución para garantizar mediciones
    rigurosas de eficiencia computacional.

    Args:
        funcion_mejora: Referencia a la función del algoritmo a ejecutar.
        imagen_gris: Matriz bidimensional de la imagen en escala de grises.

    Returns:
        Tupla que contiene la matriz procesada y el tiempo de ejecución en milisegundos.
    """
    tiempo_inicio = time.perf_counter()
    imagen_resultante = funcion_mejora(imagen_gris)
    tiempo_fin = time.perf_counter()
    
    tiempo_milisegundos = (tiempo_fin - tiempo_inicio) * 1000.0
    return imagen_resultante, float(tiempo_milisegundos)


def ejecutar_pipeline_evaluacion(ruta_originales, ruta_oscurecidas, ruta_salida_img, ruta_archivo_json):
    """
    Orquesta la ejecución de los experimentos de mejora de imagen sobre el dataset.

    Recorre el directorio de imágenes oscurecidas, aplica las configuraciones de 
    algoritmos definidas, calcula las métricas contrastando con la imagen original 
    (Verdad Terreno), guarda las imágenes resultantes y compila un registro JSON 
    estructurado para su posterior análisis estadístico.

    Args:
        ruta_originales: Objeto Path al directorio con las imágenes de referencia.
        ruta_oscurecidas: Objeto Path al directorio con las imágenes a procesar.
        ruta_salida_img: Objeto Path al directorio donde se guardarán las imágenes.
        ruta_archivo_json: Objeto Path completo del archivo JSON de salida.
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
            "id_metodo": "CLAHE_2.0_8x8",
            "funcion": lambda img: aplicar_clahe(img, limite_recorte=2.0, tamano_cuadricula=(8, 8)),
            "parametros": {"clip_limit": 2.0, "tile_grid_size": [8, 8]}
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

        # Carga en memoria mediante rutinas optimizadas de OpenCV
        imagen_oscura = cv2.imread(str(ruta_imagen_oscura), cv2.IMREAD_GRAYSCALE)
        imagen_referencia = cv2.imread(str(ruta_imagen_original), cv2.IMREAD_GRAYSCALE)

        for config in configuraciones_experimentos:
            metodo = config["id_metodo"]
            
            # Ejecución algorítmica y perfilado de tiempo
            imagen_procesada, tiempo_ms = aplicar_y_medir_tiempo(config["funcion"], imagen_oscura)
            
            # Guardado en disco de la imagen resultante
            nombre_salida = f"{metodo}_{nombre_archivo}"
            ruta_guardado_img = ruta_salida_img / nombre_salida
            cv2.imwrite(str(ruta_guardado_img), imagen_procesada)
            
            # Cálculo de métricas de calidad (referenciadas y no referenciadas)
            valor_psnr = calcular_psnr(imagen_referencia, imagen_procesada)
            valor_ambe = calcular_ambe(imagen_referencia, imagen_procesada)
            valor_ssim = calcular_ssim(imagen_referencia, imagen_procesada)
            valor_contraste = calcular_contraste(imagen_procesada)
            valor_entropia = calcular_entropia(imagen_procesada)

            # Construcción del bloque JSON por iteración
            registro_resultados.append({
                "id_imagen": nombre_archivo,
                "metodo": metodo,
                "parametros": config["parametros"],
                "rutas": {
                    "original": str(ruta_imagen_original.as_posix()),
                    "oscurecida": str(ruta_imagen_oscura.as_posix()),
                    "procesada": str(ruta_guardado_img.as_posix())
                },
                "metricas": {
                    "PSNR": valor_psnr,
                    "AMBE": valor_ambe,
                    "Contraste": valor_contraste,
                    "Entropia": valor_entropia,
                    "SSIM": valor_ssim,
                    "tiempo_ms": round(tiempo_ms, 4)
                }
            })
            
            print(f"Procesado: {nombre_archivo} | Método: {metodo} | Tiempo: {tiempo_ms:.2f} ms")

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
    directorio_base_dataset = directorio_actual.parent / NOMBRE_CARPETA_DATASET
    directorio_base_experimentos = directorio_actual.parent / NOMBRE_CARPETA_EXPERIMENTOS
    
    # Composición de rutas de entrada (Lectura)
    ruta_entrada_originales = directorio_base_dataset / NOMBRE_CARPETA_IMG / NOMBRE_CARPETA_ORIGINAL
    ruta_entrada_oscurecidas = directorio_base_dataset / NOMBRE_CARPETA_IMG / NOMBRE_CARPETA_OSCURECIDA
    
    # Composición de rutas de salida (Escritura)
    ruta_salida_imagenes = directorio_base_experimentos / NOMBRE_CARPETA_IMG
    ruta_salida_archivo_json = directorio_base_experimentos / NOMBRE_CARPETA_JSON / NOMBRE_ARCHIVO_JSON
    
    # Inyección de dependencias (rutas completas) a la función principal
    ejecutar_pipeline_evaluacion(
        ruta_entrada_originales, 
        ruta_entrada_oscurecidas, 
        ruta_salida_imagenes, 
        ruta_salida_archivo_json
    )