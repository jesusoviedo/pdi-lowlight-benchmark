import requests
from pathlib import Path
from tqdm import tqdm

def obtener_ruta_destino_desde_url(url, directorio_destino):
    """
    Extrae el nombre del archivo desde la URL provista y construye la ruta 
    completa y absoluta de almacenamiento.

    Args:
        url (str): Cadena de texto con la dirección web de descarga directa.
        directorio_destino (Path): Objeto Path que representa la carpeta de destino.

    Returns:
        Path: Objeto Path con la ruta completa hacia el archivo a descargar.
    """
    nombre_archivo = url.split('/')[-1].split('?')[0]

    return directorio_destino / nombre_archivo


def descargar_archivo_en_streaming(url, ruta_completa):
    """
    Realiza la petición HTTP en modo streaming y escribe el archivo en disco 
    por bloques para optimizar el uso de memoria RAM, mostrando una barra de progreso.

    Args:
        url (str): Cadena de texto con la dirección web de descarga directa.
        ruta_completa (Path): Objeto Path que apunta a la ubicación final del archivo.

    Returns:
        None
    """
    print(f"Iniciando conexión con: {url}")

    # Obtener el nombre del archivo desde la ruta completa para mostrarlo en la barra de progreso
    nombre_archivo = ruta_completa.name
    respuesta = requests.get(url, stream=True)
    respuesta.raise_for_status()

    # Obtener el tamaño total del archivo para configurar la barra de progreso
    tamano_total_bytes = int(respuesta.headers.get('content-length', 0))

    # Abrir el archivo en modo binario y escribir los datos por bloques, actualizando la barra de progreso
    with open(ruta_completa, 'wb') as archivo_salida, tqdm(
        desc=nombre_archivo,
        total=tamano_total_bytes,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as barra_progreso:
        for bloque_datos in respuesta.iter_content(chunk_size=1024 * 1024):
            if bloque_datos:
                tamano_escrito = archivo_salida.write(bloque_datos)
                barra_progreso.update(tamano_escrito)
                
    print(f"\nDescarga finalizada con éxito en: {ruta_completa}")


def descargar_archivo_zip(url, directorio_destino):
    """
    Coordina la verificación de directorios, la comprobación de existencia previa 
    del archivo y el proceso de descarga mediante streaming.

    Args:
        url (str): Cadena de texto con la dirección web de descarga directa.
        directorio_destino (Path): Objeto Path que representa la carpeta de destino.

    Returns:
        Path: Objeto Path con la ruta completa y absoluta hacia el archivo descargado.
    """
    # Crear el directorio de destino si no existe
    directorio_destino.mkdir(parents=True, exist_ok=True)
    ruta_completa = obtener_ruta_destino_desde_url(url, directorio_destino)
    
    if ruta_completa.exists():
        print(f"El archivo ya existe en el sistema: {ruta_completa}")
        return ruta_completa

    # Descargar el archivo en modo streaming
    descargar_archivo_en_streaming(url, ruta_completa)

    return ruta_completa


if __name__ == "__main__":
    URL_DESCARGA = "https://zenodo.org/records/5234969/files/RELLISUR.zip?download=1"
    CARPETA_DESTINO = "dataset"
    
    directorio_script = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    carpeta_dataset = directorio_script.parent / CARPETA_DESTINO

    # Descargar el archivo ZIP desde la URL especificada y guardarlo en la carpeta de destino
    descargar_archivo_zip(URL_DESCARGA, carpeta_dataset)