import numpy as np

def calcular_ambe(imagen_a, imagen_b):
    """
    Calcula el Error Absoluto Medio de Brillo (AMBE) entre dos imágenes.
    
    Args:
        imagen_a (np.ndarray): La imagen original de referencia.
        imagen_b (np.ndarray): La imagen procesada.
        
    Returns:
        dict: Diccionario con la clave 'AMBE' y su respectivo valor numérico.
    """
    media_a = np.mean(imagen_a.astype(np.float64))
    media_b = np.mean(imagen_b.astype(np.float64))
    
    return {"AMBE": float(np.abs(media_a - media_b))}

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
    imagen_a_float = imagen_a.astype(np.float64)
    imagen_b_float = imagen_b.astype(np.float64)
    
    mse = np.mean((imagen_a_float - imagen_b_float) ** 2)
    
    if mse == 0:
        return {"PSNR": float('inf')}
    
    psnr = 20 * np.log10(max_val / np.sqrt(mse))
    
    return {"PSNR": float(psnr)}