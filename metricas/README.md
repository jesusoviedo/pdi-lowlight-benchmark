# Evaluación y Métricas Cuantitativas

Este directorio aísla la lógica matemática y estadística del proyecto. Contiene las funciones necesarias para calcular el rendimiento y la calidad de los algoritmos de mejora de imagen (Ecualización, CLAHE, etc.) sobre el dataset RELLISUR.

**⚠️ Nota Arquitectónica Importante:**  
Los archivos contenidos en esta carpeta **no son scripts ejecutables independientes**. Están diseñados para actuar estrictamente como módulos utilitarios. Su objetivo es ser importados y reutilizados por el script central de evaluación.

## 🗂️ Contenido del Módulo

Las métricas se han dividido lógicamente en dos categorías según su requerimiento de datos, apoyadas por un inicializador de paquete:

*   **`__init__.py`**: Archivo de configuración que declara este directorio como un paquete oficial de Python, asegurando que las importaciones relativas funcionen correctamente en todo el proyecto.

### 1. `referenciadas.py`
Contiene métricas que requieren estrictamente una comparación matemática entre la imagen procesada y una imagen original perfecta (*Ground Truth*).
*   **PSNR (Peak Signal-to-Noise Ratio):** mide la relación señal-ruido. Valores más altos indican menor distorsión de los píxeles frente a la referencia.
*   **AMBE (Absolute Mean Brightness Error):** mide el desplazamiento del brillo medio. Valores más cercanos a cero indican una mejor preservación de la luminosidad original.
*   **SSIM (Structural Similarity Index Measure):** métrica avanzada que modela la percepción humana. Penaliza la pérdida de estructura espacial, alteraciones de contraste y desviaciones de luminancia. (Implementada para satisfacer el criterio de "Inclusión de nuevas métricas de evaluación" para puntaje extra).

### 2. `no_referenciadas.py`
Contiene métricas espaciales que evalúan características intrínsecas de una única imagen, sin necesidad de compararla contra una referencia externa.
*   **Entropía de Shannon:** cuantifica la cantidad de información (detalles y texturas) presentes en la imagen.
*   **Contraste Global:** medido a través de la desviación estándar de las intensidades de los píxeles.

## 🛠️ Patrón de Diseño y Uso Recomendado

Todas las funciones de este directorio están diseñadas para retornar **diccionarios** en lugar de valores numéricos simples (ej. `{"PSNR": 24.5}`). 

Este patrón permite consolidar la evaluación de una imagen en el script central utilizando el desempaquetado de diccionarios (`**`) en una sola línea, facilitando la tabulación, el análisis estadístico y la exportación de resultados:

```python
# Ejemplo de importación y uso en el script central
from metricas.referenciadas import calcular_psnr, calcular_ambe, calcular_ssim
from metricas.no_referenciadas import calcular_entropia, calcular_contraste

# Agrupación dinámica de resultados (Ejecución vectorizada)
resultados_clahe = {
    "Metodo": "CLAHE (Clip: 2, Grid: 8x8)",
    **calcular_psnr(referencia, imagen_procesada),
    **calcular_ambe(referencia, imagen_procesada),
    **calcular_ssim(referencia, imagen_procesada),
    **calcular_entropia(imagen_procesada),
    **calcular_contraste(imagen_procesada)
}
```