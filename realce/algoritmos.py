import cv2
import numpy as np

def aplicar_ecualizacion_global(imagen_gris):
    """
    Aplica la ecualización de histograma tradicional a una imagen.
    
    Esta técnica calcula la función de distribución acumulativa (CDF) del 
    histograma global y mapea las intensidades originales para aplanar 
    la distribución, maximizando el contraste global a costa de posibles
    saturaciones.
    
    Args:
        imagen_gris (np.ndarray): Matriz bidimensional de entrada en escala de grises.
        
    Returns:
        np.ndarray: Matriz bidimensional correspondiente a la imagen ecualizada.
    """
    if len(imagen_gris.shape) != 2:
        raise ValueError("La imagen debe estar en escala de grises.")
        
    return cv2.equalizeHist(imagen_gris)


def aplicar_clahe(imagen_gris, limite_recorte=2.0, tamano_cuadricula=(8, 8)):
    """
    Aplica el algoritmo CLAHE (Contrast Limited Adaptive Histogram Equalization).
    
    Opera sobre regiones locales (tiles) limitando la amplificación del 
    contraste para evitar la saturación de ruido, uniendo los bloques 
    mediante interpolación bilineal.
    
    Args:
        imagen_gris (np.ndarray): Matriz bidimensional de entrada en escala de grises.
        limite_recorte (float, optional): Umbral máximo para el contraste. Controla el 
            límite de recorte del histograma. Por defecto es 2.0.
        tamano_cuadricula (tuple, optional): Tupla indicando las dimensiones de la matriz 
            de bloques (filas, columnas). Por defecto es (8, 8).
            
    Returns:
        np.ndarray: Matriz bidimensional procesada con ecualización adaptativa.
    """
    if len(imagen_gris.shape) != 2:
        raise ValueError("La imagen debe estar en escala de grises.")
        
    procesador_clahe = cv2.createCLAHE(clipLimit=limite_recorte, tileGridSize=tamano_cuadricula)
    return procesador_clahe.apply(imagen_gris)


def aplicar_bhe2pl(imagen_gris):
    """
    Aplica el algoritmo BHE2PL utilizando operaciones vectorizadas.

    Divide el histograma en base a la intensidad promedio y calcula cuatro 
    límites de meseta dinámicos para evitar la sobre-ecualización, preservando
    de forma rigurosa el brillo original de la imagen.

    Args:
        imagen_gris (np.ndarray): Matriz bidimensional de la imagen en escala de grises.

    Returns:
        np.ndarray: Matriz bidimensional de la imagen ecualizada.
    """
    if len(imagen_gris.shape) != 2:
        raise ValueError("La imagen debe estar en escala de grises.")

    filas, columnas = imagen_gris.shape
    total_pixeles = filas * columnas

    # Cálculo del histograma y la probabilidad de cada intensidad (Ecuaciones 1 y 2 del paper)
    histograma = cv2.calcHist([imagen_gris], [0], None, [256], [0, 256]).flatten()
    probabilidad = histograma / total_pixeles
    niveles = np.arange(256)

    # SP: Intensidad promedio esperada que divide el histograma en dos mitades (Ecuación 8)
    intensidad_promedio = int(np.sum(probabilidad * niveles))
    indices_usados = np.nonzero(histograma)[0]
    
    if len(indices_usados) == 0:
        return imagen_gris.copy()
        
    # lmin y lmax: Primera y última intensidad con frecuencia mayor a cero
    limite_minimo = int(indices_usados[0])
    limite_maximo = int(indices_usados[-1])

    # Validación de contraste: Si la imagen es plana, se retorna sin cambios
    if intensidad_promedio <= limite_minimo or intensidad_promedio >= limite_maximo:
        return imagen_gris.copy()

    # NL y NU: Sumatoria de píxeles en los sub-histogramas inferior y superior
    cantidad_inferior = np.sum(histograma[limite_minimo:intensidad_promedio + 1])
    cantidad_superior = np.sum(histograma[intensidad_promedio + 1:limite_maximo + 1])

    if cantidad_inferior == 0 or cantidad_superior == 0:
        return imagen_gris.copy()

    # SPL y SPU: Promedio aritmético ponderado de cada sub-histograma (Ecuaciones 19 y 20)
    promedio_inferior = np.sum(niveles[limite_minimo:intensidad_promedio + 1] * histograma[limite_minimo:intensidad_promedio + 1]) / cantidad_inferior
    promedio_superior = np.sum(niveles[intensidad_promedio + 1:limite_maximo + 1] * histograma[intensidad_promedio + 1:limite_maximo + 1]) / cantidad_superior

    # GRL1 y GRU1: Tasa o proporción del nivel de gris para cada mitad (Ecuaciones 15 a 18)
    proporcion_inf_1 = (intensidad_promedio - promedio_inferior) / (intensidad_promedio - limite_minimo) if (intensidad_promedio - limite_minimo) != 0 else 0
    proporcion_sup_1 = (limite_maximo - promedio_superior) / (limite_maximo - intensidad_promedio) if (limite_maximo - intensidad_promedio) != 0 else 0

    # DL y DU: Factores de ajuste dinámico de las proporciones (Ecuaciones 21 y 22)
    delta_inferior = (1 - proporcion_inf_1) / 2 if proporcion_inf_1 > 0.5 else proporcion_inf_1 / 2
    delta_superior = (1 - proporcion_sup_1) / 2 if proporcion_sup_1 > 0.5 else proporcion_sup_1 / 2

    # GRL2 y GRU2: Tasas de nivel de gris definitivas ajustadas por los factores DL y DU
    proporcion_inf_2 = proporcion_inf_1 + delta_inferior
    proporcion_sup_2 = proporcion_sup_1 + delta_superior

    # PkL y PkU: Picos de frecuencia máxima dentro de cada sub-histograma (Ecuación 10)
    pico_inferior = np.max(histograma[limite_minimo:intensidad_promedio + 1])
    pico_superior = np.max(histograma[intensidad_promedio + 1:limite_maximo + 1])

    # PLL1, PLL2, PLU1, PLU2: Los cuatro límites de meseta para el recorte (Ecuaciones 11 a 14)
    meseta_inf_1 = proporcion_inf_1 * pico_inferior
    meseta_inf_2 = proporcion_inf_2 * pico_inferior
    meseta_sup_1 = proporcion_sup_1 * pico_superior
    meseta_sup_2 = proporcion_sup_2 * pico_superior

    # Creación de una copia del histograma para aplicar las modificaciones morfológicas
    histograma_modificado = histograma.copy()

    # Recorte (clipping) del sub-histograma inferior usando la doble meseta (PLL1, PLL2)
    indices_inf = np.arange(limite_minimo, intensidad_promedio + 1)
    condicion_inf = histograma[indices_inf] <= meseta_inf_2
    histograma_modificado[indices_inf] = np.where(condicion_inf, meseta_inf_1, meseta_inf_2)

    # Recorte (clipping) del sub-histograma superior usando la doble meseta (PLU1, PLU2)
    indices_sup = np.arange(intensidad_promedio + 1, limite_maximo + 1)
    condicion_sup = histograma[indices_sup] <= meseta_sup_2
    histograma_modificado[indices_sup] = np.where(condicion_sup, meseta_sup_1, meseta_sup_2)

    # Inicialización de la Tabla de Búsqueda (Look-Up Table) para el mapeo final
    tabla_mapeo = np.arange(256, dtype=float)

    # Ecualización independiente del sub-histograma inferior: Cálculo de la CDF y mapeo
    suma_inf = np.sum(histograma_modificado[limite_minimo:intensidad_promedio + 1])
    if suma_inf > 0:
        prob_inf = histograma_modificado[limite_minimo:intensidad_promedio + 1] / suma_inf
        cdf_inf = np.cumsum(prob_inf)
        tabla_mapeo[limite_minimo:intensidad_promedio + 1] = limite_minimo + (intensidad_promedio - limite_minimo) * (cdf_inf - 0.5 * prob_inf)

    # Ecualización independiente del sub-histograma superior: Cálculo de la CDF y mapeo
    suma_sup = np.sum(histograma_modificado[intensidad_promedio + 1:limite_maximo + 1])
    if suma_sup > 0:
        prob_sup = histograma_modificado[intensidad_promedio + 1:limite_maximo + 1] / suma_sup
        cdf_sup = np.cumsum(prob_sup)
        tabla_mapeo[intensidad_promedio + 1:limite_maximo + 1] = (intensidad_promedio + 1) + (limite_maximo - (intensidad_promedio + 1)) * (cdf_sup - 0.5 * prob_sup)

    # Redondeo de los niveles ecualizados y saturación estricta al rango [0, 255] (uint8)
    tabla_mapeo = np.clip(np.round(tabla_mapeo), 0, 255).astype(np.uint8)
    
    # Mapeo ultrarrápido aplicando la LUT sobre la imagen original
    return cv2.LUT(imagen_gris, tabla_mapeo)