# Realce de Imágenes en el Dominio Espacial

Este directorio contiene las implementaciones algorítmicas fundamentales para la mejora de contraste y la corrección de iluminación en imágenes subexpuestas. Los métodos implementados operan directamente sobre los niveles de intensidad de los píxeles en el dominio espacial para optimizar la visibilidad de los detalles ocultos.

## ⚙️ Fundamento Matemático y Mecánica de los Algoritmos

### 1. Ecualización de Histograma Tradicional (HE)
Esta técnica aplica una transformación global basada en la Función de Distribución Acumulativa ($CDF$) del histograma de la imagen de entrada.
* **Efecto visual:** reasigna los valores de los píxeles para expandir el rango dinámico disponible ($[0, 255]$), maximizando el contraste global de la escena.
* **Limitación:** al ser un enfoque estrictamente global, tiende a sobreamplificar el contraste en regiones dominantes y a saturar el ruido presente en áreas homogéneas oscuras.

### 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
CLAHE divide la imagen en pequeñas regiones locales o *tiles* (por defecto de $8 \times 8$ píxeles) para procesar el contraste de manera adaptativa.
* **Efecto visual:** calcula el histograma local y la transformación correspondiente para cada cuadrícula de forma independiente, resolviendo problemas de iluminación heterogénea.
* **Control de Ruido:** incorpora un umbral de recorte (*clip limit*). Si la frecuencia de un nivel de intensidad supera el límite establecido, los píxeles excedentes se redistribuyen uniformemente antes de calcular la $CDF$, previniendo la amplificación excesiva del ruido.
* **Suavizado:** utiliza interpolación bilineal en los límites de las cuadrículas para eliminar los artefactos de bloques y las transiciones artificiales perceptibles.

### 3. BHE2PL (Bi-Histogram Equalization with Two Plateau Limits)
Este algoritmo avanzado, introducido por [Aquino-Morinigo et al.](https://doi.org/10.1007/s11760-016-1032-0), divide el histograma original en dos sub-histogramas basándose en la intensidad promedio de la imagen, procesándolos de manera independiente.
* **Efecto visual:** previene la sobre-ecualización característica del método tradicional y preserva rigurosamente el brillo medio original de la captura.
* **Control Dinámico:** calcula automáticamente cuatro límites de meseta (plateau limits) basados en la probabilidad espacial, recortando los picos del histograma sin necesidad de que el usuario introduzca hiperparámetros manuales.

## 🛠️ Estructura del Módulo

*   **`__init__.py`**: archivo inicializador que define el directorio como un paquete modular de Python.
*   **`algoritmos.py`**: script que expone las funciones principales de procesamiento:
    *   `aplicar_ecualizacion_global(imagen_gris)`: ejecuta la ecualización tradicional optimizada.
    *   `aplicar_clahe(imagen_gris, limite_recorte, tamano_cuadricula)`: ejecuta la ecualización adaptativa con control de contraste local.
    *   `aplicar_bhe2pl(imagen_gris)`: ejecuta la ecualización de doble histograma mediante operaciones puramente vectorizadas.

## 🚀 Guía de Uso e Integración

Este módulo está diseñado para ser importado y reutilizado desde el orquestador central del proyecto. Asegúrese de ejecutar el entorno de **Anaconda** configurado previamente.

Ejemplo de importación y aplicación en el flujo principal:

```python
import cv2
from realce.algoritmos import aplicar_ecualizacion_global, aplicar_clahe, aplicar_bhe2pl

# Cargar imagen en escala de grises
imagen_subexpuesta = cv2.imread("dataset/img/oscurecida/0001.png", cv2.IMREAD_GRAYSCALE)

# Aplicar técnicas de realce espacial
imagen_global = aplicar_ecualizacion_global(imagen_subexpuesta)
imagen_clahe = aplicar_clahe(imagen_subexpuesta, limite_recorte=2.0, tamano_cuadricula=(8, 8))
imagen_bhe2pl = aplicar_bhe2pl(imagen_subexpuesta)
```