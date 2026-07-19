import requests
from pathlib import Path
from tqdm import tqdm

def descargar_archivo_zip(url, directorio_destino):
    """Descarga un archivo desde una URL mostrando una barra de progreso visual.
    
    Verifica si el directorio de destino existe; si no, lo crea. Luego extrae el
    nombre del archivo de la URL y realiza la descarga en modo streaming (por bloques)
    para optimizar el uso de memoria RAM.

    Args:
        url: Cadena de texto con la dirección web de descarga directa.
        directorio_destino: Objeto Path que representa la carpeta donde se 
            almacenará el archivo descargado.

    Returns:
        Objeto Path con la ruta completa y absoluta hacia el archivo descargado.
    """
    directorio_destino.mkdir(parents=True, exist_ok=True)
    
    nombre_archivo = url.split('/')[-1].split('?')[0]
    ruta_completa = directorio_destino / nombre_archivo
    
    if ruta_completa.exists():
        print(f"El archivo ya existe en el sistema: {ruta_completa}")
        return ruta_completa
        
    print(f"Iniciando conexión con: {url}")
    
    # Iniciar la petición HTTP en modo streaming
    respuesta = requests.get(url, stream=True)
    respuesta.raise_for_status()  # Lanza una excepción si hay un error HTTP (ej. 404, 500)
    
    # Extraer el tamaño total del archivo desde las cabeceras HTTP
    tamano_total_bytes = int(respuesta.headers.get('content-length', 0))
    
    # Configurar el bloque de escritura con la barra de progreso de tqdm
    with open(ruta_completa, 'wb') as archivo_salida, tqdm(
        desc=nombre_archivo,
        total=tamano_total_bytes,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as barra_progreso:
        # Descargar y escribir en disco en bloques de 1 MB
        for bloque_datos in respuesta.iter_content(chunk_size=1024 * 1024):
            if bloque_datos:
                tamano_escrito = archivo_salida.write(bloque_datos)
                barra_progreso.update(tamano_escrito)
                
    print(f"\nDescarga finalizada con éxito en: {ruta_completa}")
    return ruta_completa

if __name__ == "__main__":
    url_descarga = "https://zenodo.org/records/5234969/files/RELLISUR.zip?download=1"
    
    # Obtener el directorio donde se encuentra este script (ingesta/)
    directorio_script = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    
    # Subir un nivel hacia la raíz del proyecto y apuntar a la carpeta dataset
    carpeta_dataset = directorio_script.parent / "dataset"
    
    descargar_archivo_zip(url_descarga, carpeta_dataset)