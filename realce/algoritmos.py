import cv2
import numpy as np

def aplicar_ecualizacion_global(imagen_gris):
    """Aplica la ecualización de histograma tradicional a una imagen.
    
    Esta técnica calcula la función de distribución acumulativa (CDF) del 
    histograma de la imagen y mapea las intensidades originales para aplanar 
    la distribución, maximizando el contraste global.
    
    Args:
        imagen_gris: Imagen bidimensional de entrada en escala de grises (8 bits).
        
    Returns:
        Nueva matriz con el histograma global ecualizado.
    """
    if len(imagen_gris.shape) != 2:
        raise ValueError("La imagen de entrada debe estar en escala de grises (2 dimensiones).")
        
    return cv2.equalizeHist(imagen_gris)


def aplicar_clahe(imagen_gris, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Aplica el algoritmo CLAHE (Contrast Limited Adaptive Histogram Equalization).
    
    A diferencia de la ecualización global, CLAHE opera sobre cuadrículas locales 
    (tiles) de la imagen. Limita la amplificación del contraste (clip limit) para 
    evitar la saturación del ruido en regiones homogéneas y utiliza interpolación 
    bilineal para eliminar los bordes artificiales entre los bloques.
    
    Args:
        imagen_gris: Imagen bidimensional de entrada en escala de grises.
        clip_limit: Umbral de recorte para el contraste. Valores típicos 
            oscilan entre 2.0 (sutil) y 4.0 (agresivo).
        tile_grid_size: Dimensiones de la matriz de bloques (filas, columnas).
            
    Returns:
        Nueva matriz procesada con ecualización adaptativa.
    """
    if len(imagen_gris.shape) != 2:
        raise ValueError("La imagen de entrada debe estar en escala de grises (2 dimensiones).")
        
    # Instanciamos el objeto CLAHE de OpenCV con los parámetros solicitados
    clahe_processor = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    
    return clahe_processor.apply(imagen_gris)