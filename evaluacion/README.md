# Módulo de Orquestación y Evaluación

Este directorio contiene el script `orquestador_evaluacion.py`. Este script actúa como el motor principal de la **Fase 2 (Procesamiento)** y **Fase 3 (Evaluación)** descritas en la documentación general del proyecto. 

Su función es acoplar dinámicamente los algoritmos de realce con las métricas de evaluación matemática (AMBE, PSNR, Contraste, Entropía y SSIM). El script ejecuta los experimentos por lotes sobre el dataset seleccionado.

## Requisitos Previos

1. Haber completado la **Paso 1** (descarga y extracción del dataset) utilizando los scripts de la carpeta `ingesta/`.
2. Tener activado el entorno virtual del proyecto.

## Instrucciones de Ejecución

El script utiliza resolución de rutas relativas dinámicas. Asegúrese de activar su entorno virtual y de ubicarse en la **raíz del proyecto**. Ejecute el orquestador con el siguiente comando:
`python evaluacion/orquestador_evaluacion.py`

## Flujo de Datos (I/O)

El orquestador funciona con un sistema de rutas relativas ancladas a la raíz del proyecto. Esto garantiza la portabilidad absoluta del código:

* **Entrada (Lectura):** accede a `dataset/img/` para leer las imágenes oscurecidas y sus respectivas verdades terreno (Ground Truth).
* **Salida (Escritura):** genera automáticamente el directorio jerárquico `experimento/` en la raíz. Las imágenes procesadas se exportan a la subcarpeta `experimento/img/`. El registro final de métricas se almacena en `experimento/json/resultados_evaluacion.json`.
* **Estructura Semántica de Datos:** el archivo JSON aísla estructuralmente las métricas en tres grupos fundamentales: imagen oscurecida, imagen original e imagen procesada. Esta separación permite la ingesta nativa y el cálculo vectorizado de ganancias en Pandas. 

A continuación, se presenta un extracto representativo del archivo generado:

```json
[
  {
    "id_imagen": "0001_CLAHE_2_8.png",
    "metodo": "CLAHE_2_8",
    "parametros": {
      "limite_contraste": 2.0,
      "tamano_cuadricula": [8, 8]
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
    "metricas_imagen_oscurecida": {
      "PSNR": 8.0123,
      "AMBE": 95.4321,
      "SSIM": 0.3124,
      "Contraste": 25.1023,
      "Entropia": 5.1452
    },
    "metricas_imagen_original": {
      "Contraste": 40.1234,
      "Entropia": 6.8912
    }
  }
]

```

## Parámetros de Reproducibilidad y Configuraciones del Experimento

El script codifica los hiperparámetros de manera estricta. Esto garantiza una evaluación determinista y asegura la reproducibilidad de los experimentos. El orquestador ejecuta un total de cinco configuraciones algorítmicas por imagen.

Para evaluar el impacto de la distribución espacial de píxeles, el experimento implementa tres variaciones específicas del algoritmo CLAHE. La alteración de sus parámetros modifica la mitigación de ruido y la saturación del contraste local.

Las configuraciones establecidas son las siguientes:

* **CLAHE_2_8 (Configuración Conservadora):**
  * `limite_contraste`: 2.0
  * `tamano_cuadricula`: [8, 8]
  * El objetivo es aplicar un estiramiento de contraste local moderado. El límite de recorte bajo previene la amplificación del ruido de alta frecuencia en regiones homogéneas.
* **CLAHE_2_4 (Alta Frecuencia Local):**
  * `limite_contraste`: 2.0
  * `tamano_cuadricula`: [4, 4]
  * El objetivo es capturar detalles finos muy localizados. La reducción de la cuadrícula concentra el cálculo de la Función de Distribución Acumulada (CDF) en vecindarios espaciales más pequeños.
* **CLAHE_4_8 (Configuración Agresiva):**
  * `limite_contraste`: 4.0
  * `tamano_cuadricula`: [8, 8]
  * El objetivo es identificar el punto de degradación del error de brillo. El aumento del límite de recorte satura los histogramas locales y afecta negativamente la métrica AMBE.
* **HE_Global (Ecualización de Histograma):** ejecuta la ecualización clásica basada en la CDF global de la imagen. Este algoritmo carece de parámetros espaciales.
* **BHE2PL:** ejecuta un algoritmo de mejora de contraste automatizado. El método utiliza la media de intensidad para separar el histograma en dos mesetas sin requerir hiperparámetros manuales.

