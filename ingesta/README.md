# Ingesta y Preparación de Datos

Este directorio contiene los scripts responsables de la obtención y el acondicionamiento del dataset RELLISUR. La ejecución de este pipeline automatiza la descarga segura y la extracción de una muestra estadística representativa, garantizando la reproducibilidad del experimento.

## ⚙️ Mecánica de los Scripts

### 1. `descargar_dataset.py`

Este script establece una conexión directa con el repositorio público de Zenodo. El código descarga el archivo masivo `RELLISUR.zip` (8.9 GB) utilizando una estrategia de *streaming* por bloques. Esta técnica optimiza el uso de la memoria RAM y proporciona una barra de progreso visual en la terminal.

El archivo comprimido original contiene una topología interna específica diseñada para tareas de mejora de iluminación y súper-resolución. El desglose físico interno del archivo es el siguiente:

* **Particiones Base:** el dataset divide los datos en tres directorios principales: `Train/`, `Val/` y `Test/`. Cada subdirectorio contiene las siguientes dos carpetas internamente:
    * **`LLLR/` (Low-Light Low-Resolution):** esta carpeta almacena las imágenes subexpuestas empíricas. El dataset contiene 5 niveles diferentes de oscuridad controlada por cada imagen de referencia original.
    * **`NLHR/` (Normal-Light High-Resolution):** esta carpeta resguarda las imágenes de referencia (Verdad Terreno) capturadas con iluminación normal. Este directorio se subdivide en tres escalas de resolución espacial: `X1`, `X2` y `X4`.

A nivel estadístico, el archivo bruto totaliza 850 imágenes de referencia únicas. La multiplicación por sus niveles de exposición arroja un volumen exacto de 4250 imágenes subexpuestas de entrada. Conocer esta estructura es vital, ya que los algoritmos de evaluación de este proyecto consumirán exclusivamente la escala `X1` para mantener la paridad dimensional.

### 2. `extraer_dataset.py`
Este script evita la descompresión total del archivo en el disco. Lee directamente la tabla de contenidos del archivo ZIP en memoria y aplica una semilla matemática (`seed=42`) para garantizar un proceso determinista. 

Sus características principales de extracción son:
*   **Extracción a Medida:** Permite al usuario definir la cantidad exacta de pares a extraer mediante el parámetro `-n` o `--cantidad` (por defecto extrae 850).
*   **Límite Estadístico Protegido:** Contiene una validación estructural. Si se solicita un número superior a la capacidad del dataset, el script lo detecta y extrae automáticamente el límite máximo disponible (**850 imágenes originales únicas**).
*   **Selección de Ruido:** Agrupa las 5 variantes de subexposición (LLLR) por cada imagen original y elige una al azar de manera reproducible.
*   **Re-indexación Global:** Renombra los archivos extraídos aplicando una numeración secuencial unificada (ej. `0001.png` a `0850.png`) para asegurar una paridad estructural perfecta entre las imágenes originales y sus contrapartes oscurecidas.
*   **Limpieza de Disco:** Incorpora un parámetro opcional (`--eliminar-zip`) diseñado para borrar el archivo masivo original tras una extracción exitosa, optimizando el almacenamiento local.

## 🚀 Ejecución del Pipeline

Asegúrate de ejecutar estos comandos desde la **raíz del proyecto** con tu entorno virtual activado.

**Paso 1: Descargar los datos brutos**
```bash
python ingesta/descargar_dataset.py
```

**Paso 2: Extraer la muestra de evaluación**

Puedes realizar la extracción del dataset completo (850 pares por defecto):

```bash
python ingesta/extraer_dataset.py
```

> **💡 Nota del Proyecto:** Esta ejecución por defecto (850 pares) es el comando exacto que se utilizó para generar la muestra oficial sobre la cual se calcularon las métricas.

Extraer una muestra reducida para pruebas rápidas (ej. 100 pares):

```bash
python ingesta/extraer_dataset.py -n 100

```

Ejecutar la extracción completa instruyendo al script que elimine automáticamente el archivo `.zip` al finalizar para liberar espacio:

```bash
python ingesta/extraer_dataset.py --eliminar-zip

```

*Nota: Puedes combinar ambos parámetros si lo deseas (ej. `python ingesta/extraer_dataset.py -n 50 --eliminar-zip`).*

## 📂 Artefactos Generados

Tras la ejecución exitosa de ambos scripts, se creará automáticamente una carpeta `dataset/` en la raíz del proyecto. Esta carpeta está excluida del control de versiones (`.gitignore`) y presentará la siguiente topología:

```text
dataset/
├── RELLISUR.zip               # Archivo comprimido original (ausente si se usó --eliminar-zip)
└── img/                       # Subconjunto extraído para la evaluación
    ├── original/              # N imágenes de referencia (NLHR/X1, re-indexadas, máx. 850)
    └── oscurecida/            # N imágenes subexpuestas (LLLR, 1 variante determinista por par)

```