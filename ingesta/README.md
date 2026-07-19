# Ingesta y Preparación de Datos

Este directorio contiene los scripts responsables de la obtención y el acondicionamiento del dataset RELLISUR. La ejecución de este pipeline automatiza la descarga segura y la extracción de una muestra estadística representativa, garantizando la reproducibilidad del experimento.

## ⚙️ Mecánica de los Scripts

### 1. `descargar_dataset.py`
Este script establece una conexión directa con el repositorio de Zenodo. Descarga el archivo masivo `RELLISUR.zip` (8.9 GB) utilizando una estrategia de *streaming* por bloques. Esto optimiza el uso de la memoria RAM y proporciona una barra de progreso visual en la terminal.

### 2. `extraer_dataset.py`
Este script evita la descompresión total del archivo en el disco. Lee directamente la tabla de contenidos del archivo ZIP en memoria y aplica una semilla matemática (`seed=42`) para garantizar un proceso determinista. 

Sus características principales de extracción son:
*   **Límite Estadístico:** Identifica y extrae automáticamente el máximo de pares únicos disponibles en el dataset original (**850 imágenes**).
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

Puedes realizar la extracción conservando el archivo original en el disco:

```bash
python ingesta/extraer_dataset.py

```

O, de manera alternativa, puedes ejecutar la extracción instruyendo al script que elimine automáticamente el archivo `.zip` al finalizar para liberar espacio:

```bash
python ingesta/extraer_dataset.py --eliminar-zip

```

## 📂 Artefactos Generados

Tras la ejecución exitosa de ambos scripts, se creará automáticamente una carpeta `dataset/` en la raíz del proyecto. Esta carpeta está excluida del control de versiones (`.gitignore`) y presentará la siguiente topología:

```text
dataset/
├── RELLISUR.zip               # Archivo comprimido original (ausente si se usó --eliminar-zip)
└── img/                       # Subconjunto extraído para la evaluación
    ├── original/              # 850 imágenes de referencia (NLHR/X1, re-indexadas)
    └── oscurecida/            # 850 imágenes subexpuestas (LLLR, 1 variante determinista por par)

```