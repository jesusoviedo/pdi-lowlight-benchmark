# Módulo de Orquestación y Evaluación

Este directorio contiene el script `orquestador_evaluacion.py`, el cual actúa como el motor principal de la **Fase 2 (Procesamiento)** y **Fase 3 (Evaluación)** descritas en la documentación general del proyecto. 

Su función es acoplar dinámicamente los algoritmos de realce con las métricas de evaluación matemática, ejecutando los experimentos por lotes sobre el dataset RELLISUR.

## Requisitos Previos

1. Haber completado la **Fase 1** (descarga y extracción del dataset) utilizando los scripts de la carpeta `ingesta/`.
2. Tener activado el entorno virtual del proyecto.

## Instrucciones de Ejecución

Para iniciar el procesamiento masivo, asegúrese de estar posicionado dentro de este directorio (`evaluacion/`) y ejecute el orquestador:
```bash
python orquestador_evaluacion.py
```

## Flujo de Datos (I/O)

El orquestador funciona con rutas dinámicas relativas, asumiendo la siguiente estructura jerárquica:

* **Entrada (Lectura):** accede a `../dataset/img/` para leer las imágenes oscurecidas y sus respectivas verdades terreno (Ground Truth).
* **Salida (Escritura):** genera automáticamente un directorio `../experimento/` en la raíz del proyecto. Aquí se exportan las imágenes procesadas y el registro final de métricas (`json/resultados_evaluacion.json`), dejando los datos listos para el análisis estadístico en Jupyter.

## Parámetros de Reproducibilidad

Para garantizar una evaluación justa y determinista de las técnicas de mejora de imagen, los hiperparámetros están codificados en el bloque principal del script:

* **CLAHE (Contrast Limited Adaptive Histogram Equalization):**
    * `clip_limit`: 2.0
    * `tile_grid_size`: (8, 8)
* **Ecualización de Histograma (HE) Global:** ejecución matemática estándar basada en la función de distribución acumulativa (CDF) de toda la imagen, sin parámetros de segmentación espacial.
* **BHE2PL (Bi-Histogram Equalization with Two Plateau Limits):** ejecución algorítmica automatizada que utiliza la intensidad media espacial como punto de corte para el cálculo de mesetas, sin requerir hiperparámetros manuales de segmentación.
