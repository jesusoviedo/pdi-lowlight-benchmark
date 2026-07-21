# Módulo de Orquestación y Evaluación

Este directorio contiene el script `orquestador_evaluacion.py`, el cual actúa como el motor principal de la **Fase 2 (Procesamiento)** y **Fase 3 (Evaluación)** descritas en la documentación general del proyecto. 

Su función es acoplar dinámicamente los algoritmos de realce con las métricas de evaluación matemática, ejecutando los experimentos por lotes sobre el dataset RELLISUR.

## Requisitos Previos

1. Haber completado la **Fase 1** (descarga y extracción del dataset) utilizando los scripts de la carpeta `ingesta/`.
2. Tener activado el entorno virtual del proyecto.

## Instrucciones de Ejecución

Para garantizar la resolución correcta de las rutas relativas dinámicas, asegúrese de tener su entorno virtual activado y estar posicionado en la **raíz del proyecto** (directorio principal). Desde allí, ejecute el orquestador:
```bash
python evaluacion/orquestador_evaluacion.py
```

## Flujo de Datos (I/O)

El orquestador funciona con un sistema de rutas relativas ancladas a la raíz del proyecto, garantizando la portabilidad absoluta del código:

* **Entrada (Lectura):** accede a `dataset/img/` para leer las imágenes oscurecidas y sus respectivas verdades terreno (Ground Truth).
* **Salida (Escritura):** genera automáticamente el directorio jerárquico `experimento/` en la raíz. Las imágenes procesadas se exportan a la subcarpeta `experimento/img/`, mientras que el registro final de métricas se almacena en `experimento/json/resultados_evaluacion.json`.
* **Estructura Semántica y Salida de Datos:** el JSON resultante aísla estructuralmente las métricas. Esta separación semántica es fundamental, ya que permite la ingesta nativa y el aplanamiento vectorizado de los datos en Pandas mediante la función `pd.json_normalize()`. 

A continuación, se presenta un extracto representativo de la estructura del archivo generado:

```json
[
  {
    "id_imagen": "0001_CLAHE_2_8.png",
    "metodo": "CLAHE_2_8",
    "parametros": {
      "clip_limit": 2.0,
      "tile_grid_size": [8, 8]
    },
    "rutas": {
      "original": "dataset/img/original/0001.png",
      "oscurecida": "dataset/img/oscurecida/0001.png",
      "procesada": "experimento/img/0001_CLAHE_2_8.png"
    },
    "metricas_imagen_procesada": {
      "PSNR": 14.2341,
      "AMBE": 45.1235,
      "SSIM": 0.8124,
      "Contraste": 56.1023,
      "Entropia": 7.1452,
      "tiempo_ms": 1.25
    },
    "metricas_imagen_original": {
      "Contraste": 40.1234,
      "Entropia": 6.8912
    }
  }
]
```

## Parámetros de Reproducibilidad

Para garantizar una evaluación determinista y el rigor científico de los resultados, los hiperparámetros se encuentran estrictamente codificados en el bloque principal del script:

* **CLAHE (Contrast Limited Adaptive Histogram Equalization):**
	* `clip_limit`: 2.0
	* `tile_grid_size`: (8, 8)
* **Ecualización de Histograma (HE) Global:** Ejecución matemática estándar basada en la función de distribución acumulativa (CDF) de toda la imagen, sin parámetros de segmentación espacial.
* **BHE2PL (Bi-Histogram Equalization with Two Plateau Limits):** Ejecución algorítmica automatizada que utiliza la intensidad media espacial como punto de corte para el cálculo de las dos mesetas, garantizando la preservación del brillo sin requerir hiperparámetros manuales de ajuste.
