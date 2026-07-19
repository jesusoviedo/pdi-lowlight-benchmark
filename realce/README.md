# Realce de Imágenes en el Dominio Espacial

Este directorio contiene las implementaciones algorítmicas fundamentales para la mejora de contraste y la corrección de iluminación en imágenes subexpuestas. Los métodos implementados operan directamente sobre los niveles de intensidad de los píxeles en el dominio espacial para optimizar la visibilidad de los detalles ocultos.

## ⚙️ Fundamento Matemático y Mecánica de los Algoritmos

### 1. Ecualización de Histograma Tradicional
Esta técnica aplica una transformación global basada en la Función de Distribución Acumulativa ($CDF$) del histograma de la imagen de entrada.
* **Efecto visual:** Reasigna los valores de los píxeles para expandir el rango dinámico disponible ($[0, 255]$), maximizando el contraste global de la escena.
* **Limitación:** Al ser un enfoque estrictamente global, tiende a sobreamplificar el contraste en regiones dominantes y a saturar el ruido presente en áreas homogéneas oscuras.

### 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
CLAHE divide la imagen en pequeñas regiones locales o *tiles* (por defecto de $8 \times 8$ píxeles) para procesar el contraste de manera adaptativa.
* **Efecto visual:** Calcula el histograma local y la transformación correspondiente para cada cuadrícula de forma independiente, resolviendo problemas de iluminación heterogénea.
* **Control de Ruido:** Incorpora un umbral de recorte (*clip limit*). Si la frecuencia de un nivel de intensidad supera el límite establecido, los píxeles excedentes se redistribuyen uniformemente antes de calcular la $CDF$, previniendo la amplificación excesiva del ruido.
* **Suavizado:** Utiliza interpolación bilineal en los límites de las cuadrículas para eliminar los artefactos de bloques y las transiciones artificiales perceptibles.

## 🛠️ Estructura del Módulo

*   **`__init__.py`**: Archivo inicializador que define el directorio como un paquete modular de Python.
*   **`algoritmos.py`**: Script que expone las funciones principales de procesamiento:
    *   `aplicar_ecualizacion_global(imagen_gris)`: Ejecuta la ecualización tradicional optimizada mediante operaciones nativas de OpenCV.
    *   `aplicar_clahe(imagen_gris, clip_limit, tile_grid_size)`: Ejecuta la ecualización adaptativa con control de contraste local y parámetros configurables.

## 🚀 Guía de Uso e Integración

Este módulo está diseñado para ser importado y reutilizado desde el script central de procesamiento del proyecto. Asegúrate de contar con el entorno de **Anaconda** configurado y activo con las dependencias necesarias.

Ejemplo de importación y aplicación en el flujo principal:

```python
import cv2
from realce.algoritmos import aplicar_ecualizacion_global, aplicar_clahe

# Cargar imagen en escala de grises
imagen_subexpuesta = cv2.imread("dataset/img/oscurecida/0001.png", cv2.IMREAD_GRAYSCALE)

# Aplicar técnicas de realce espacial
imagen_global = aplicar_ecualizacion_global(imagen_subexpuesta)
imagen_clahe = aplicar_clahe(imagen_subexpuesta, clip_limit=2.0, tile_grid_size=(8, 8))
```