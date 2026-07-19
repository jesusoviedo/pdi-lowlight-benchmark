def extraer_pares_dataset(ruta_zip, directorio_salida, cantidad_muestras, semilla_aleatoria, eliminar_zip=False):
    """Extrae un muestreo aleatorio reproducible de pares de imágenes del dataset.

    Agrupa todas las variantes de subexposición (LLLR) para cada imagen original (NLHR) 
    y selecciona una al azar de forma determinista (usando la semilla). Aplica una 
    re-indexación secuencial global (ej. 0001.png) para mantener paridad estricta.

    Args:
        ruta_zip: Objeto Path que apunta al archivo ZIP del dataset.
        directorio_salida: Objeto Path que indica la carpeta raíz donde se crearán las subcarpetas de imágenes.
        cantidad_muestras: Entero que define la cantidad máxima de pares a extraer.
        semilla_aleatoria: Entero utilizado para fijar el estado del generador de números aleatorios.
        eliminar_zip: Booleano, si es Verdadero, elimina el archivo comprimido tras finalizar la extracción.

    Returns:
        Booleano que indica si la operación de extracción finalizó con éxito (Verdadero) o falló (Falso).
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
        diccionario_lllr = {}

        # 1. Escaneo inicial: Agrupamos todas las variantes de oscuridad en listas
        for ruta in todos_los_archivos:
            if "LLLR" in ruta and not ruta.endswith('/'):
                particion = "Train" if "Train" in ruta else ("Val" if "Val" in ruta else ("Test" if "Test" in ruta else "Extra"))
                nombre_archivo = Path(ruta).stem        
                prefijo = nombre_archivo.split('-')[0]  
                
                clave_unica = f"{particion}_{prefijo}"  
                
                if clave_unica not in diccionario_lllr:
                    diccionario_lllr[clave_unica] = []
                
                # Guardamos todas las rutas de las variantes (ej. -1.5, -2.5, etc.)
                diccionario_lllr[clave_unica].append(ruta)
                
            elif "NLHR" in ruta and "X1" in ruta and not ruta.endswith('/'):
                rutas_originales_disponibles.append(ruta)

        rutas_originales_disponibles.sort()

        if not rutas_originales_disponibles:
            print("No se encontraron imágenes en la subruta especificada (NLHR/X1).")
            return False

        # Inicializamos la semilla matemática
        random.seed(semilla_aleatoria)
        
        cantidad_a_extraer = min(cantidad_muestras, len(rutas_originales_disponibles))
        print(f"[*] Procediendo a extraer {cantidad_a_extraer} pares únicos (1 variante aleatoria por par)...")
        seleccion_originales = random.sample(rutas_originales_disponibles, cantidad_a_extraer)

        pares_procesados = 0

        # 2. Extracción O(1) con selección aleatoria determinista
        for ruta_original in seleccion_originales:
            particion = "Train" if "Train" in ruta_original else ("Val" if "Val" in ruta_original else ("Test" if "Test" in ruta_original else "Extra"))
            prefijo_original = Path(ruta_original).stem 
            
            clave_unica = f"{particion}_{prefijo_original}" 
            lista_variantes = diccionario_lllr.get(clave_unica)
            
            if lista_variantes:
                # Elegimos 1 nivel de oscuridad al azar de la lista (reproducible por el random.seed)
                ruta_oscurecida_esperada = random.choice(lista_variantes)
                
                contenido_original = archivo_comprimido.read(ruta_original)
                contenido_oscurecido = archivo_comprimido.read(ruta_oscurecida_esperada)

                # Nomenclatura: Formato de 4 dígitos para fácil iteración (0001.png, 0002.png...)
                nuevo_nombre_archivo = f"{(pares_procesados + 1):04d}.png"
                
                ruta_destino_original = carpeta_original / nuevo_nombre_archivo
                ruta_destino_oscurecida = carpeta_oscurecida / nuevo_nombre_archivo

                with open(ruta_destino_original, 'wb') as archivo_salida_original:
                    archivo_salida_original.write(contenido_original)
                
                with open(ruta_destino_oscurecida, 'wb') as archivo_salida_oscurecida:
                    archivo_salida_oscurecida.write(contenido_oscurecido)
                
                pares_procesados += 1
            else:
                print(f"Advertencia: No se encontró variante LLLR para la clave {clave_unica}")

    print(f"Extracción finalizada exitosamente: {pares_procesados} pares guardados en {carpeta_img}.")
    
    if eliminar_zip:
        try:
            ruta_zip.unlink()
            print(f"Limpieza: Archivo {ruta_zip.name} eliminado del disco exitosamente.")
        except Exception as e:
            print(f"Advertencia: No se pudo eliminar el archivo {ruta_zip.name}. Detalle: {e}")

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrae una muestra estadística del dataset RELLISUR.")
    parser.add_argument(
        "--eliminar-zip", 
        action="store_true", 
        help="Incluye esta bandera para eliminar el archivo ZIP original tras la extracción."
    )
    # Nuevo argumento para definir la cantidad por consola
    parser.add_argument(
        "-n", "--cantidad", 
        type=int, 
        default=850, 
        help="Cantidad de pares a extraer. Máximo soportado: 850."
    )
    args = parser.parse_args()

    directorio_script = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    carpeta_dataset = directorio_script.parent / "dataset"
    ruta_archivo_zip = carpeta_dataset / "RELLISUR.zip"
    
    semilla_reproducibilidad = 42
    MAX_CANTIDAD_IMAGENES = 850

    # Lógica de validación del límite superior
    if args.cantidad > MAX_CANTIDAD_IMAGENES:
        print(f"[*] Aviso: Solicitaste {args.cantidad} pares, pero el dataset contiene un máximo de {MAX_CANTIDAD_IMAGENES} imágenes originales únicas.")
        print(f"[*] El script extraerá el límite máximo disponible ({MAX_CANTIDAD_IMAGENES}).")
        cantidad_imagenes_a_extraer = MAX_CANTIDAD_IMAGENES
    else:
        cantidad_imagenes_a_extraer = args.cantidad

    extraer_pares_dataset(
        ruta_zip=ruta_archivo_zip,
        directorio_salida=carpeta_dataset,
        cantidad_muestras=cantidad_imagenes_a_extraer,
        semilla_aleatoria=semilla_reproducibilidad,
        eliminar_zip=args.eliminar_zip
    )