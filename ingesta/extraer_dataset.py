import zipfile
import random
import argparse
from pathlib import Path
from tqdm import tqdm

def procesar_argumentos_linea_comandos():
    """
    Parsea y valida los argumentos pasados por la línea de comandos.

    Configura el analizador de argumentos para recibir las opciones de ejecución
    relacionadas con la extracción de pares del dataset RELLISUR.

    Returns:
        argparse.Namespace: Objeto con los argumentos parseados y validados.
    """
    analizador = argparse.ArgumentParser(
        description="Extrae una muestra estadística del dataset RELLISUR."
    )

    analizador.add_argument(
        "--eliminar-zip", 
        action="store_true", 
        help="Elimina el archivo ZIP original tras la extracción."
    )

    analizador.add_argument(
        "-n", "--cantidad", 
        type=int, 
        default=850, 
        help="Cantidad de pares a extraer. Máximo soportado: 850."
    )

    return analizador.parse_args()


def validar_cantidad_muestras(cantidad_solicitada, maxima_cantidad):
    """
    Valida que la cantidad de muestras solicitada no exceda el límite máximo 
    permitido por el dataset.

    Si la cantidad solicitada supera el umbral máximo soportado, ajusta el valor 
    al límite superior y emite un aviso por consola. De lo contrario, respeta 
    la cantidad especificada.

    Args:
        cantidad_solicitada (int): Entero que representa la cantidad de pares pedidos.
        maxima_cantidad (int): Entero que representa el límite superior soportado.

    Returns:
        int: Entero con la cantidad final de muestras a extraer.
    """
    if cantidad_solicitada > maxima_cantidad:
        print(f"Aviso: Se solicitaron {cantidad_solicitada} pares, pero el máximo disponible es {maxima_cantidad}.")
        return maxima_cantidad
    
    return cantidad_solicitada


def escanear_y_agrupar_archivos_zip(todos_los_archivos):
    """
    Escanea la lista de rutas dentro del archivo comprimido para agrupar las 
    variantes de subexposición (LLLR) y recopilar las imágenes originales (NLHR).

    Args:
        todos_los_archivos (list): Lista de cadenas que representan las rutas internas del archivo ZIP.

    Returns:
        tuple: Una tupla compuesta por:
            - diccionario_lllr (dict): Diccionario que relaciona claves únicas con sus listas de rutas LLLR.
            - rutas_originales_disponibles (list): Lista ordenada con las rutas de las imágenes originales válidas.
    """
    rutas_originales_disponibles = []
    diccionario_lllr = {}

    for ruta in todos_los_archivos:
        if "LLLR" in ruta and not ruta.endswith('/'):
            particion = "Train" if "Train" in ruta else ("Val" if "Val" in ruta else ("Test" if "Test" in ruta else "Extra"))
            nombre_archivo = Path(ruta).stem        
            prefijo = nombre_archivo.split('-')[0]  
            
            clave_unica = f"{particion}_{prefijo}"  
            
            if clave_unica not in diccionario_lllr:
                diccionario_lllr[clave_unica] = []
            
            diccionario_lllr[clave_unica].append(ruta)
            
        elif "NLHR" in ruta and "X1" in ruta and not ruta.endswith('/'):
            rutas_originales_disponibles.append(ruta)

    rutas_originales_disponibles.sort()

    return diccionario_lllr, rutas_originales_disponibles


def extraer_y_guardar_pares_imagenes(
    seleccion_originales, 
    diccionario_lllr, 
    archivo_comprimido, 
    carpeta_original, 
    carpeta_oscurecida
):
    """
    Extrae, re-indexa y guarda en disco los pares de imágenes seleccionadas 
    mostrando una barra de progreso interactiva.

    Args:
        seleccion_originales (list): Lista de rutas de las imágenes originales seleccionadas.
        diccionario_lllr (dict): Diccionario con las rutas de las variantes oscurecidas agrupadas.
        archivo_comprimido (zipfile.ZipFile): Objeto abierto del archivo ZIP del dataset.
        carpeta_original (Path): Directorio de destino para las imágenes originales.
        carpeta_oscurecida (Path): Directorio de destino para las imágenes oscurecidas.

    Returns:
        int: Cantidad total de pares procesados y guardados exitosamente.
    """
    pares_procesados = 0

    for ruta_original in tqdm(seleccion_originales, desc="Extrayendo imágenes", unit="par"):
        particion = "Train" if "Train" in ruta_original else ("Val" if "Val" in ruta_original else ("Test" if "Test" in ruta_original else "Extra"))
        prefijo_original = Path(ruta_original).stem 
        
        clave_unica = f"{particion}_{prefijo_original}" 
        lista_variantes = diccionario_lllr.get(clave_unica)
        
        if lista_variantes:
            ruta_oscurecida_esperada = random.choice(lista_variantes)
            
            contenido_original = archivo_comprimido.read(ruta_original)
            contenido_oscurecido = archivo_comprimido.read(ruta_oscurecida_esperada)

            nuevo_nombre_archivo = f"{(pares_procesados + 1):04d}.png"
            
            ruta_destino_original = carpeta_original / nuevo_nombre_archivo
            ruta_destino_oscurecida = carpeta_oscurecida / nuevo_nombre_archivo

            with open(ruta_destino_original, 'wb') as archivo_salida_original:
                archivo_salida_original.write(contenido_original)
            
            with open(ruta_destino_oscurecida, 'wb') as archivo_salida_oscurecida:
                archivo_salida_oscurecida.write(contenido_oscurecido)
            
            pares_procesados += 1

    return pares_procesados


def eliminar_archivo_zip(ruta_zip, eliminar_zip):
    """
    Elimina de forma segura el archivo comprimido del disco si se ha 
    solicitado explícitamente mediante los parámetros de ejecución.

    Args:
        ruta_zip (Path): Objeto Path que apunta al archivo ZIP del dataset.
        eliminar_zip (bool): Booleano que indica si se debe proceder con la eliminación.

    Returns:
        bool: Retorna siempre verdadero para mantener la continuidad del flujo lógico.
    """
    if eliminar_zip:
        try:
            ruta_zip.unlink()
            print(f"Limpieza: Archivo {ruta_zip.name} eliminado del disco exitosamente.")
        except Exception as error_limpieza:
            print(f"Advertencia: No se pudo eliminar el archivo {ruta_zip.name}. Detalle: {error_limpieza}")

    return True


def extraer_pares_dataset(
    ruta_zip, 
    directorio_salida, 
    cantidad_muestras, 
    semilla_aleatoria, 
    nombre_carpeta_img, 
    nombre_carpeta_orig, 
    nombre_carpeta_osc, 
    eliminar_zip=False
):
    """
    Extrae un muestreo aleatorio reproducible de pares de imágenes del dataset 
    mostrando una barra de progreso interactiva.

    Agrupa todas las variantes de subexposición (LLLR) para cada imagen original (NLHR) 
    y selecciona una al azar de forma determinista (usando la semilla). Aplica una 
    re-indexación secuencial global (ej. 0001.png) para mantener paridad estricta.

    Args:
        ruta_zip (Path): Objeto Path que apunta al archivo ZIP del dataset.
        directorio_salida (Path): Objeto Path que indica la carpeta raíz donde se crearán 
            las subcarpetas de imágenes.
        cantidad_muestras (int): Entero que define la cantidad máxima de pares a extraer.
        semilla_aleatoria (int): Entero utilizado para fijar el estado del generador de 
            números aleatorios.
        nombre_carpeta_img (str): Nombre de la carpeta contenedora de imágenes.
        nombre_carpeta_orig (str): Nombre de la subcarpeta para imágenes originales.
        nombre_carpeta_osc (str): Nombre de la subcarpeta para imágenes oscurecidas.
        eliminar_zip (bool, optional): Booleano que si es verdadero, elimina el archivo comprimido tras 
            finalizar la extracción. Por defecto es falso.

    Returns:
        bool: Booleano que indica verdadero si la operación finalizó con éxito, 
        falso si ocurrió un error crítico.
    """
    if not ruta_zip.exists():
        print(f"Error crítico: El archivo comprimido no existe en {ruta_zip}")
        return False

    # Crear la estructura de carpetas de salida
    carpeta_img = directorio_salida / nombre_carpeta_img
    carpeta_original = carpeta_img / nombre_carpeta_orig
    carpeta_oscurecida = carpeta_img / nombre_carpeta_osc

    # Crear las carpetas si no existen
    carpeta_original.mkdir(parents=True, exist_ok=True)
    carpeta_oscurecida.mkdir(parents=True, exist_ok=True)

    print(f"Abriendo el archivo {ruta_zip.name} para escaneo en memoria...")
    
    with zipfile.ZipFile(ruta_zip, 'r') as archivo_comprimido:
        # Escaneo y agrupamiento de rutas internas
        todos_los_archivos = archivo_comprimido.namelist()
        diccionario_lllr, rutas_originales_disponibles = escanear_y_agrupar_archivos_zip(todos_los_archivos)

        # Validación de disponibilidad de imágenes originales
        if not rutas_originales_disponibles:
            print("No se encontraron imágenes en la subruta especificada (NLHR/X1).")
            return False

        # Configuración de la semilla para reproducibilidad y selección aleatoria
        random.seed(semilla_aleatoria)
        cantidad_a_extraer = min(cantidad_muestras, len(rutas_originales_disponibles))
        print(f"Procediendo a extraer {cantidad_a_extraer} pares únicos...")
        seleccion_originales = random.sample(rutas_originales_disponibles, cantidad_a_extraer)

        # Extracción y guardado de pares de imágenes con barra de progreso
        pares_procesados = extraer_y_guardar_pares_imagenes(
            seleccion_originales,
            diccionario_lllr,
            archivo_comprimido,
            carpeta_original,
            carpeta_oscurecida
        )

    print(f"\nExtracción finalizada exitosamente: {pares_procesados} pares guardados.")
    
    # Eliminación opcional del archivo ZIP original si se solicitó
    eliminar_archivo_zip(ruta_zip, eliminar_zip)

    return True


if __name__ == "__main__":
    NOMBRE_ARCHIVO_DATASET_ZIP = "RELLISUR.zip"
    NOMBRE_CARPETA_DATASET_RAIZ = "dataset"
    NOMBRE_CARPETA_CONTENEDOR_IMAGENES = "img"
    NOMBRE_CARPETA_ORIGINALES = "original"
    NOMBRE_CARPETA_OSCURECIDAS = "oscurecida"

    argumentos = procesar_argumentos_linea_comandos()

    directorio_script = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    carpeta_dataset = directorio_script.parent / NOMBRE_CARPETA_DATASET_RAIZ
    ruta_archivo_zip = carpeta_dataset / NOMBRE_ARCHIVO_DATASET_ZIP
    
    semilla_reproducibilidad = 42
    maxima_cantidad_imagenes = 850

    cantidad_imagenes_a_extraer = validar_cantidad_muestras(
        argumentos.cantidad, 
        maxima_cantidad_imagenes
    )

    extraer_pares_dataset(
        ruta_zip=ruta_archivo_zip,
        directorio_salida=carpeta_dataset,
        cantidad_muestras=cantidad_imagenes_a_extraer,
        semilla_aleatoria=semilla_reproducibilidad,
        nombre_carpeta_img=NOMBRE_CARPETA_CONTENEDOR_IMAGENES,
        nombre_carpeta_orig=NOMBRE_CARPETA_ORIGINALES,
        nombre_carpeta_osc=NOMBRE_CARPETA_OSCURECIDAS,
        eliminar_zip=argumentos.eliminar_zip
    )