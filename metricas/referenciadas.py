import numpy as np
from skimage.metrics import structural_similarity

def calcular_ambe(imagen_a, imagen_b):
    """
    Calcula el Error Absoluto Medio de Brillo (AMBE) entre dos imágenes.
    
    Args:
        imagen_a (np.ndarray): La imagen original de referencia.
        imagen_b (np.ndarray): La imagen procesada.
        
    Returns:
        dict: Diccionario con la clave 'AMBE' y su respectivo valor numérico.
    """
    # Convertimos las imágenes a tipo float64 para evitar problemas de desbordamiento
    media_a = np.mean(imagen_a.astype(np.float64))
    media_b = np.mean(imagen_b.astype(np.float64))

    # Calculamos el Error Absoluto Medio de Brillo
    ambe = np.abs(media_a - media_b)
    
    return {"AMBE": float(ambe)}


def calcular_psnr(imagen_a, imagen_b, max_val=255.0):
    """
    Calcula la Relación Señal a Ruido Máxima (PSNR) entre dos imágenes.
    
    Args:
        imagen_a (np.ndarray): La imagen original de referencia.
        imagen_b (np.ndarray): La imagen procesada a evaluar.
        max_val (float, optional): El valor máximo posible de un píxel. Por defecto 255.0.
            
    Returns:
        dict: Diccionario con la clave 'PSNR' y su respectivo valor en dB.
    """
    # Convertimos las imágenes a tipo float64 para evitar problemas de desbordamiento
    imagen_a_float = imagen_a.astype(np.float64)
    imagen_b_float = imagen_b.astype(np.float64)

    # Calculamos el Error Cuadrático Medio (MSE)
    mse = np.mean((imagen_a_float - imagen_b_float) ** 2)

    # Evitamos la división por cero en caso de que las imágenes sean idénticas
    if mse == 0:
        return {"PSNR": float('inf')}

    # Calculamos el PSNR usando la fórmula estándar
    psnr = 20 * np.log10(max_val / np.sqrt(mse))
    
    return {"PSNR": float(psnr)}


def calcular_ssim(imagen_referencia, imagen_procesada, rango_datos=255):
    """
    Calcula el Índice de Similitud Estructural (SSIM) entre dos imágenes.
    
    Esta métrica evalúa la degradación estructural, de luminancia y contraste,
    penalizando las distorsiones visuales. Un valor cercano a 1 indica una 
    similitud perfecta con la Verdad Terreno.
    
    Args:
        imagen_referencia: La imagen original con iluminación normal (Verdad Terreno).
        imagen_procesada: La imagen resultante tras aplicar el algoritmo de mejora.
        rango_datos: El valor máximo posible del rango dinámico de los píxeles.
        
    Returns:
        dict: Diccionario con la clave 'SSIM' y su respectivo valor numérico.
    """
    # Convertimos los arreglos a flotantes para evitar desbordamientos en las operaciones internas
    referencia_float = imagen_referencia.astype(np.float64)
    procesada_float = imagen_procesada.astype(np.float64)
    
    # Calculamos el SSIM utilizando la función de skimage
    valor_ssim = structural_similarity(
        referencia_float,
        procesada_float,
        data_range=rango_datos
    )
    
    return {"SSIM": float(valor_ssim)}