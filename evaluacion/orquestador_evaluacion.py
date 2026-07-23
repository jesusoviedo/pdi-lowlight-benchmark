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


def verificar_existencia_directorios(ruta_originales, ruta_oscurecidas):
    """Verifica de manera estricta que los directorios de entrada existan y sean válidos.

    Comprueba tanto la existencia en disco como que la ruta apunte efectivamente 
    a un directorio. Si ocurre un error, informa al usuario por pantalla y detiene
    la ejecución limpiamente en lugar de arrojar una excepción abrupta.

    Args:
        ruta_originales (Path): Objeto con la ruta al directorio de imágenes de referencia.
        ruta_oscurecidas (Path): Objeto con la ruta al directorio de imágenes a procesar.
    """
    if not ruta_originales.exists() or not ruta_originales.is_dir():
        print(f"Error crítico: El directorio de imágenes originales no existe o no es válido -> {ruta_originales}")
        sys.exit(1)
    
    if not ruta_oscurecidas.exists() or not ruta_oscurecidas.is_dir():
        print(f"Error crítico: El directorio de imágenes oscurecidas no existe o no es válido -> {ruta_oscurecidas}")
        sys.exit(1)
        
    print("Pre-chequeo exitoso: Los directorios de entrada están listos y accesibles.")


def obtener_configuraciones_experimentos():
    """Retorna la lista estructurada con las configuraciones de los experimentos.

    Define los algoritmos de mejora de imagen a evaluar en el pipeline (incluyendo CLAHE,
    Ecualización Global y un método adicional), referenciando la función algorítmica 
    y los hiperparámetros utilizados para garantizar la reproducibilidad del estudio.

    Returns:
        list: Colección de diccionarios que definen los experimentos algorítmicos.
    """
    configuraciones = [
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

    return configuraciones


def leer_imagen_robusto(ruta_imagen):
    """Lee una imagen desde el disco soportando caracteres especiales en la ruta.

    Utiliza NumPy para leer los bytes en crudo y el decodificador de OpenCV
    para evitar los problemas nativos de cv2.imread en sistemas Windows cuando 
    las rutas contienen tildes o caracteres especiales.

    Args:
        ruta_imagen (str o Path): Cadena de texto o un objeto Path indicando la ubicación del archivo.

    Returns:
        numpy.ndarray: Matriz bidimensional correspondiente a la imagen en escala de grises.

    Raises:
        FileNotFoundError: Si el archivo no se puede leer o no existe en la ruta especificada.
        ValueError: Si el archivo existe pero OpenCV no puede decodificarlo como imagen válida.
    """
    # Convertir la ruta a cadena de texto para compatibilidad con np.fromfile
    ruta_texto = str(ruta_imagen)
    arreglo_bytes = np.fromfile(ruta_texto, dtype=np.uint8)

    # Validación de lectura de archivo
    if arreglo_bytes.size == 0:
        raise FileNotFoundError(f"No se pudo leer el archivo en la ruta: {ruta_texto}")
        
    imagen_decodificada = cv2.imdecode(arreglo_bytes, cv2.IMREAD_GRAYSCALE)

    # Validación de decodificación de imagen
    if imagen_decodificada is None:
        raise ValueError(f"El archivo existe pero no es una imagen válida: {ruta_texto}")
        
    return imagen_decodificada


def aplicar_y_medir_tiempo(funcion_mejora, imagen_gris):
    """Ejecuta un algoritmo de mejora de imagen y mide su tiempo de procesamiento.

    Utiliza un contador de rendimiento de alta resolución (time.perf_counter) para
    garantizar mediciones rigurosas de eficiencia computacional.

    Args:
        funcion_mejora (callable): Referencia a la función del algoritmo a ejecutar.
        imagen_gris (numpy.ndarray): Matriz bidimensional de la imagen en escala de grises.

    Returns:
        tuple: Una tupla que contiene:
            - numpy.ndarray: La matriz de la imagen procesada.
            - dict: Diccionario con la clave 'tiempo_ms' indicando el tiempo de ejecución en milisegundos.
    """
    # Medición de tiempo de ejecución del algoritmo
    tiempo_inicio = time.perf_counter()
    imagen_resultante = funcion_mejora(imagen_gris)
    tiempo_fin = time.perf_counter()

    # Cálculo del tiempo transcurrido en milisegundos
    tiempo_milisegundos = (tiempo_fin - tiempo_inicio) * 1000.0

    return imagen_resultante, {"tiempo_ms": float(tiempo_milisegundos)}


def evaluar_metodos_en_imagen(
    ruta_imagen_oscura, 
    ruta_imagen_original, 
    imagen_oscura, 
    imagen_referencia, 
    contraste_original, 
    entropia_original, 
    psnr_oscurecida, 
    ambe_oscurecida, 
    ssim_oscurecida, 
    contraste_oscurecida, 
    entropia_oscurecida, 
    configuraciones_experimentos, 
    ruta_salida_img, 
    ruta_raiz_proyecto
):
    """Aplica las configuraciones experimentales a una imagen, calculando sus métricas.

    Procesa la imagen oscura con cada algoritmo (CLAHE, HE, etc.), calcula métricas clave
    (PSNR, AMBE, SSIM, contraste y entropía) alineadas con la evaluación sumativa,
    y estructura los resultados para su posterior exportación.

    Args:
        ruta_imagen_oscura (Path): Ruta del archivo de la imagen subexpuesta.
        ruta_imagen_original (Path): Ruta del archivo de la imagen de referencia.
        imagen_oscura (numpy.ndarray): Matriz de la imagen oscura en escala de grises.
        imagen_referencia (numpy.ndarray): Matriz de la imagen original en escala de grises.
        contraste_original (dict): Valor de contraste de la imagen original.
        entropia_original (dict): Valor de entropía de la imagen original.
        psnr_oscurecida (dict): Valor PSNR de la imagen oscura respecto a la original.
        ambe_oscurecida (dict): Valor AMBE de la imagen oscura respecto a la original.
        ssim_oscurecida (dict): Valor SSIM de la imagen oscura respecto a la original.
        contraste_oscurecida (dict): Valor de contraste de la imagen oscura.
        entropia_oscurecida (dict): Valor de entropía de la imagen oscura.
        configuraciones_experimentos (list): Lista de diccionarios con métodos y parámetros.
        ruta_salida_img (Path): Directorio destino para guardar las imágenes procesadas.
        ruta_raiz_proyecto (Path): Directorio base del proyecto para construir rutas relativas.

    Returns:
        list: Colección de diccionarios con los resultados detallados por cada método aplicado.
    """
    resultados_imagen = []
    nombre_base = ruta_imagen_oscura.stem

    for config in configuraciones_experimentos:
        metodo = config["id_metodo"]
        
        # Ejecución algorítmica y perfilado de tiempo
        imagen_procesada, metrica_tiempo_procesada = aplicar_y_medir_tiempo(config["funcion"], imagen_oscura)
        
        # Guardado en disco de la imagen resultante
        nombre_salida = f"{nombre_base}_{metodo}.png"
        ruta_guardado_img = ruta_salida_img / nombre_salida
        cv2.imwrite(str(ruta_guardado_img), imagen_procesada)
        
        # Cálculo de métricas de calidad de la imagen procesada
        psnr_procesada = calcular_psnr(imagen_referencia, imagen_procesada)
        ambe_procesada = calcular_ambe(imagen_referencia, imagen_procesada)
        ssim_procesada = calcular_ssim(imagen_referencia, imagen_procesada)
        contraste_procesada = calcular_contraste(imagen_procesada)
        entropia_procesada = calcular_entropia(imagen_procesada)

        # Construcción del bloque de resultados para el JSON
        resultados_imagen.append({
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
            },
            "tiempo_ms": metrica_tiempo_procesada["tiempo_ms"]
        })

    return resultados_imagen


def ejecutar_pipeline_evaluacion(
    ruta_originales, 
    ruta_oscurecidas, 
    ruta_salida_img, 
    ruta_archivo_json, 
    ruta_raiz_proyecto
):
    """Orquesta la ejecución completa de los experimentos de mejora sobre el dataset.

    Coordina la inicialización de directorios, delegación del procesamiento por lotes,
    cálculo de métricas requeridas (AMBE, PSNR, Contraste, Entropía) y persistencia
    incremental de los resultados en un archivo JSON.

    Args:
        ruta_originales (Path): Directorio que contiene las imágenes de referencia (Verdad Terreno).
        ruta_oscurecidas (Path): Directorio que contiene las imágenes subexpuestas a procesar.
        ruta_salida_img (Path): Directorio de destino para las imágenes resultantes.
        ruta_archivo_json (Path): Ruta completa donde se exportará el registro JSON.
        ruta_raiz_proyecto (Path): Ruta absoluta al directorio raíz del repositorio.
    """
    # Crear estructura de directorios de salida dinámicamente
    ruta_salida_img.mkdir(parents=True, exist_ok=True)

    # Crea la carpeta padre del archivo JSON dinámicamente si no existe
    ruta_archivo_json.parent.mkdir(parents=True, exist_ok=True)

    # Obtener la lista de configuraciones de experimentos a evaluar
    configuraciones_experimentos = obtener_configuraciones_experimentos()

    # Contar el total de imágenes y métodos para calcular el progreso
    total_imagenes = sum(1 for _ in ruta_oscurecidas.glob("*.png"))
    total_metodos = len(configuraciones_experimentos)

    # Inicialización de variables de progreso
    total_pasos = total_imagenes * total_metodos
    paso_actual = 0

    registro_resultados = []

    print("Iniciando procesamiento por lotes del dataset...")
    
    # Iteración sobre los archivos (I/O).
    for ruta_imagen_oscura in ruta_oscurecidas.glob("*.png"):
        nombre_archivo = ruta_imagen_oscura.name
        ruta_imagen_original = ruta_originales / nombre_archivo
        
        if not ruta_imagen_original.exists():
            print(f"Advertencia: Verdad Terreno no encontrada para {nombre_archivo}")
            continue

        # Lectura robusta de imágenes desde disco
        imagen_oscura = leer_imagen_robusto(ruta_imagen_oscura)
        imagen_referencia = leer_imagen_robusto(ruta_imagen_original)

        # Calcular métricas de la imagen original una sola vez por imagen
        contraste_original = calcular_contraste(imagen_referencia)
        entropia_original = calcular_entropia(imagen_referencia)

        # Calcular métricas de la imagen oscura una sola vez por imagen
        psnr_oscurecida = calcular_psnr(imagen_referencia, imagen_oscura)
        ambe_oscurecida = calcular_ambe(imagen_referencia, imagen_oscura)
        ssim_oscurecida = calcular_ssim(imagen_referencia, imagen_oscura)
        contraste_oscurecida = calcular_contraste(imagen_oscura)
        entropia_oscurecida = calcular_entropia(imagen_oscura)

        # Evaluar todos los métodos de mejora sobre la imagen oscura y obtener resultados
        resultados_parciales = evaluar_metodos_en_imagen(
            ruta_imagen_oscura,
            ruta_imagen_original,
            imagen_oscura,
            imagen_referencia,
            contraste_original,
            entropia_original,
            psnr_oscurecida,
            ambe_oscurecida,
            ssim_oscurecida,
            contraste_oscurecida,
            entropia_oscurecida,
            configuraciones_experimentos,
            ruta_salida_img,
            ruta_raiz_proyecto
        )

        # Acumulación de resultados y actualización de progreso
        registro_resultados.extend(resultados_parciales)

        paso_actual += len(resultados_parciales)
        porcentaje_avance = (paso_actual / total_pasos) * 100
        
        print(f"Progreso: {porcentaje_avance:5.1f}% | Memoria procesada: {nombre_archivo}")

    print("\nProcesamiento finalizado. Guardando resultados en disco...")
    
    # Exportación de resultados a archivo JSON con codificación UTF-8 y formato legible
    with open(ruta_archivo_json, "w", encoding="utf-8") as archivo_json:
        json.dump(registro_resultados, archivo_json, indent=2, ensure_ascii=False)
            
    print(f"Exportación exitosa en: {ruta_archivo_json}")


if __name__ == "__main__":
    # Definición de nombres de carpetas y archivos
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
    
    # Composición de rutas de entrada (lectura)
    ruta_entrada_originales = directorio_base_dataset / NOMBRE_CARPETA_IMG / NOMBRE_CARPETA_ORIGINAL
    ruta_entrada_oscurecidas = directorio_base_dataset / NOMBRE_CARPETA_IMG / NOMBRE_CARPETA_OSCURECIDA

    verificar_existencia_directorios(ruta_entrada_originales, ruta_entrada_oscurecidas)
    
    # Composición de rutas de salida (escritura)
    ruta_salida_imagenes = directorio_base_experimentos / NOMBRE_CARPETA_IMG
    ruta_salida_archivo_json = directorio_base_experimentos / NOMBRE_CARPETA_JSON / NOMBRE_ARCHIVO_JSON
    
    # Ejecución del pipeline de evaluación con todas las configuraciones y métricas
    ejecutar_pipeline_evaluacion(
        ruta_entrada_originales, 
        ruta_entrada_oscurecidas, 
        ruta_salida_imagenes, 
        ruta_salida_archivo_json,
        directorio_raiz_proyecto
    )