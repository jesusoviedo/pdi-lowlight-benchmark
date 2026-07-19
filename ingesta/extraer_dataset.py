import zipfile
import random
import argparse
from pathlib import Path

def extraer_pares_dataset(ruta_zip, directorio_salida, cantidad_muestras, semilla_aleatoria, eliminar_zip=False):
    """Extrae un muestreo aleatorio reproducible de pares de imágenes del dataset.

    Explora el archivo comprimido buscando las imágenes originales en la subcarpeta
    NLHR/X1 y sus contrapartes en la carpeta LLLR. Asegura la reproducibilidad 
    matemática ordenando explícitamente la lista de archivos antes de inicializar 
    el generador pseudoaleatorio. Las imágenes se guardan en subcarpetas separadas.

    Args:
        ruta_zip: Objeto Path que apunta al archivo ZIP descargado.
        directorio_salida: Objeto Path de la carpeta principal donde se creará 
            la carpeta 'img'.
        cantidad_muestras: Número entero de pares de imágenes a extraer.
        semilla_aleatoria: Número entero para inicializar el muestreo determinista.
        eliminar_zip: Booleano que indica si se debe borrar el archivo ZIP original 
            del disco tras finalizar la extracción exitosamente.

    Returns:
        Booleano indicando si la operación de extracción finalizó con éxito.
    """
    if not ruta_zip.exists():
        print(f"Error crítico: El archivo comprimido no existe en {ruta_zip}")
        return False

    carpeta_img = directorio_salida / "img"
    carpeta_original = carpeta_img / "original"
    carpeta_oscurecida = carpeta_img / "oscurecida"

    carpeta_original.mkdir(parents=True, exist_ok=True)
    carpeta_oscurecida.mkdir(parents=True, exist_ok=True)

    print(f"Abriendo el archivo {ruta_zip.name} para extracción en memoria...")
    
    with zipfile.ZipFile(ruta_zip, 'r') as archivo_comprimido:
        todos_los_archivos = archivo_comprimido.namelist()

        rutas_originales_disponibles = []
        for ruta in todos_los_archivos:
            # Filtramos solo los archivos de la subcarpeta X1 (evitando directorios puros)
            if "NLHR" in ruta and "X1" in ruta and not ruta.endswith('/'):
                rutas_originales_disponibles.append(ruta)

        # Ordenación explícita para garantizar la reproducibilidad 
        # sin importar el sistema operativo o cómo el gestor desempaquetó la tabla.
        rutas_originales_disponibles.sort()

        if not rutas_originales_disponibles:
            print("No se encontraron imágenes en la subruta especificada (NLHR/X1).")
            return False

        # Inicializamos el generador con la semilla
        random.seed(semilla_aleatoria)
        
        cantidad_a_extraer = min(cantidad_muestras, len(rutas_originales_disponibles))
        seleccion_originales = random.sample(rutas_originales_disponibles, cantidad_a_extraer)

        pares_procesados = 0

        for ruta_original in seleccion_originales:
            nombre_imagen = Path(ruta_original).name
            
            # Buscar el par correspondiente en LLLR
            ruta_oscurecida_esperada = None
            for ruta in todos_los_archivos:
                if "LLLR" in ruta and Path(ruta).name == nombre_imagen:
                    ruta_oscurecida_esperada = ruta
                    break
            
            if ruta_oscurecida_esperada:
                # Lectura directa a memoria (optimiza I/O al no extraer carpetas innecesarias)
                contenido_original = archivo_comprimido.read(ruta_original)
                contenido_oscurecido = archivo_comprimido.read(ruta_oscurecida_esperada)

                ruta_destino_original = carpeta_original / nombre_imagen
                ruta_destino_oscurecida = carpeta_oscurecida / nombre_imagen

                with open(ruta_destino_original, 'wb') as archivo_salida_original:
                    archivo_salida_original.write(contenido_original)
                
                with open(ruta_destino_oscurecida, 'wb') as archivo_salida_oscurecida:
                    archivo_salida_oscurecida.write(contenido_oscurecido)
                
                pares_procesados += 1
            else:
                print(f"Advertencia: No se encontró la imagen LLLR para el par {nombre_imagen}")

    print(f"Extracción finalizada exitosamente: {pares_procesados} pares guardados en {carpeta_img}.")
    
    # Fuera del context manager `with`, procedemos a eliminar si se solicitó
    if eliminar_zip:
        try:
            ruta_zip.unlink()
            print(f"Limpieza: Archivo {ruta_zip.name} eliminado del disco exitosamente.")
        except Exception as e:
            print(f"Advertencia: No se pudo eliminar el archivo {ruta_zip.name}. Detalle: {e}")

    return True

if __name__ == "__main__":
    # Configuración de los argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Extrae una muestra estadística del dataset RELLISUR.")
    parser.add_argument(
        "--eliminar-zip", 
        action="store_true", 
        help="Incluye esta bandera para eliminar el archivo ZIP original tras la extracción."
    )
    args = parser.parse_args()

    # Obtener el directorio donde se encuentra este script (ingesta/)
    directorio_script = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    
    # Subir un nivel hacia la raíz del proyecto y apuntar a la carpeta dataset
    carpeta_dataset = directorio_script.parent / "dataset"
    ruta_archivo_zip = carpeta_dataset / "RELLISUR.zip"
    
    # Parámetros para la reproducibilidad de los experimentos
    semilla_reproducibilidad = 42
    cantidad_imagenes_a_extraer = 1062

    extraer_pares_dataset(
        ruta_zip=ruta_archivo_zip,
        directorio_salida=carpeta_dataset,
        cantidad_muestras=cantidad_imagenes_a_extraer,
        semilla_aleatoria=semilla_reproducibilidad,
        eliminar_zip=args.eliminar_zip
    )