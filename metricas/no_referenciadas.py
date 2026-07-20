import numpy as np
from skimage.measure import shannon_entropy

def calcular_entropia(imagen):
    """
    Calcula la entropía de Shannon de una imagen para medir la cantidad de información.
    
    Args:
        imagen (np.ndarray): Imagen en escala de grises a evaluar.
        
    Returns:
        dict: Diccionario con la clave 'Entropia' y su respectivo valor.
    """
    entropia = shannon_entropy(imagen)
    
    return {"Entropia": float(entropia)}


def calcular_contraste(imagen):
    """
    Calcula el contraste global de una imagen basado en su desviación estándar.
    
    Args:
        imagen (np.ndarray): Imagen en escala de grises a evaluar.
        
    Returns:
        dict: Diccionario con la clave 'Contraste' y su respectivo valor.
    """
    contraste = np.std(imagen)
    
    return {"Contraste": float(contraste)}