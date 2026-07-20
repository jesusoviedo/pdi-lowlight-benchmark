# Evaluación y Métricas Cuantitativas

Este directorio aísla la lógica matemática y estadística del proyecto. Contiene las funciones vectorizadas necesarias para calcular el rendimiento y la calidad de los algoritmos de mejora de imagen (Ecualización Global, CLAHE, BHE2PL) sobre el dataset RELLISUR.

**⚠️ Nota Arquitectónica Importante:**  
Los archivos contenidos en esta carpeta **no son scripts ejecutables independientes**. Están diseñados para actuar estrictamente como módulos utilitarios. Su objetivo es ser importados y reutilizados por el orquestador central de evaluación.

## 🗂️ Contenido del Módulo

Las métricas se han dividido lógicamente en dos categorías según su requerimiento de datos:

### 1. `referenciadas.py`
Contiene métricas que requieren estrictamente una comparación matemática entre la imagen procesada y una Verdad Terreno (*Ground Truth*).
*   **PSNR (Peak Signal-to-Noise Ratio):** mide la relación señal-ruido. Valores más altos indican menor distorsión espacial frente a la referencia.
*   **AMBE (Absolute Mean Brightness Error):** cuantifica el desplazamiento del brillo medio. Valores más cercanos a cero indican una preservación óptima de la luminosidad original.
*   **SSIM (Structural Similarity Index Measure):** métrica avanzada introducida por *Wang et al. (2004)* que modela la percepción visual humana. Penaliza la pérdida de estructura, alteraciones de contraste y desviaciones de luminancia. Se ha implementado para garantizar una evaluación estructural robusta que complementa al PSNR.

### 2. `no_referenciadas.py`
Contiene métricas espaciales que evalúan características intrínsecas de la imagen procesada de forma independiente, sin necesidad de compararla contra una referencia externa.
*   **Entropía de Shannon:** cuantifica la cantidad de información empírica, detalles y texturas recuperadas en la imagen.
*   **Contraste Global:** evaluado matemáticamente a través de la desviación estándar de las intensidades de los píxeles.

## 🛠️ Patrón de Diseño y Uso Recomendado

Todas las funciones de este directorio están diseñadas para retornar **diccionarios** en lugar de valores numéricos simples (ej. `{"PSNR": 24.5}`). 

Este patrón arquitectónico permite consolidar la evaluación de una imagen en el script central utilizando el desempaquetado de diccionarios (`**`) en una sola línea. Esto facilita la construcción del JSON final y su posterior tabulación con Pandas:

```python
# Ejemplo de importación y uso en el script central
from metricas.referenciadas import calcular_psnr, calcular_ambe, calcular_ssim
from metricas.no_referenciadas import calcular_entropia, calcular_contraste

# Agrupación dinámica de resultados (Ejecución vectorizada)
resultados_imagen = {
    "Metodo": "CLAHE_2.0_8x8",
    **calcular_psnr(referencia, imagen_procesada),
    **calcular_ambe(referencia, imagen_procesada),
    **calcular_ssim(referencia, imagen_procesada),
    **calcular_entropia(imagen_procesada),
    **calcular_contraste(imagen_procesada)
}
```