# Análisis Estadístico y Evaluación de Métricas

Este directorio contiene el cuaderno de computación interactiva (Jupyter Notebook) destinado al análisis cuantitativo y cualitativo de los algoritmos de mejora de imagen. El flujo de trabajo procesa los resultados extraídos por el orquestador del experimento y genera las tablas estadísticas necesarias para el artículo académico.

## Contenido del Directorio

* `analisis_estadistico_resultados.ipynb`: Cuaderno principal con el análisis de los datos.
* `README.md`: Documento actual con instrucciones de configuración y uso.

## Metodología de Análisis

El cuaderno implementa operaciones vectorizadas mediante la biblioteca Pandas para evaluar el rendimiento de las técnicas (CLAHE, HE_Global y BHE2PL). El análisis procesa las siguientes métricas de calidad de imagen:
* Error Absoluto Medio de Brillo (AMBE).
* Relación Señal a Ruido Máxima (PSNR).
* Índice de Similitud Estructural (SSIM).
* Contraste (Desviación estándar de intensidades).
* Entropía (Riqueza de información visual).

El flujo de ejecución genera cuatro tablas analíticas fundamentales:
1. **Estadística Descriptiva (Medias):** evalúa el rendimiento central de cada algoritmo.
2. **Estadística Descriptiva (Desviación Estándar):** analiza la estabilidad de cada técnica.
3. **Mejoras Relativas (Deltas):** cuantifica el impacto de la mejora frente a la imagen subexpuesta original.
4. **Tasas de Recuperación:** nide la retención de la información visual frente a la escena original.

## Requisitos Previos

Para ejecutar este módulo de análisis estadístico, es estrictamente necesario cumplir con las siguientes dependencias del proyecto:

1. Haber completado la **Fase 4 (Ejecución del Experimento)** utilizando el orquestador del directorio `evaluacion/`. Este paso genera el archivo `resultados_evaluacion.json` requerido por el cuaderno.
2. Tener activado el entorno virtual global del proyecto (`tp_1`).

## Instrucciones de Ejecución

1. Inicie la interfaz de computación interactiva desde su terminal:
```bash
jupyter lab
```
2. Navegue hasta el directorio `evaluacion/` y abra el archivo `analisis_estadistico_resultados.ipynb`.
3. Ejecute las celdas de forma secuencial (Shift + Enter). Este proceso cargará los datos, calculará las métricas y generará las tablas estadísticas debatidas en el artículo.