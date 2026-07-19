import urllib.request
from pathlib import Path

def descargar_archivo_zip(url, directorio_destino):
    """Descarga un archivo desde una URL y lo guarda en el directorio especificado.
    
    Verifica si el directorio de destino existe; si no, lo crea. Luego extrae el
    nombre del archivo de la URL y realiza la descarga si el archivo no se
    encuentra previamente en la ruta.

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
        
    print(f"Iniciando descarga desde: {url}")
    print("Por favor, espere. Esto puede tardar dependiendo del tamaño del archivo...")
    
    urllib.request.urlretrieve(url, ruta_completa)
    
    print(f"Descarga finalizada con éxito en: {ruta_completa}")
    return ruta_completa

if __name__ == "__main__":
    url_descarga = "https://zenodo.org/records/5234969/files/RELLISUR.zip?download=1"
    
    directorio_actual = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    carpeta_dataset = directorio_actual / "dataset"
    
    descargar_archivo_zip(url_descarga, carpeta_dataset)