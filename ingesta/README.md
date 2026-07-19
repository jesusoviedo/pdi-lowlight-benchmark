# Ingesta y Preparación de Datos

Este directorio contiene los scripts responsables de la obtención y el acondicionamiento del dataset RELLISUR. La ejecución de este pipeline automatiza la descarga segura y la extracción de una muestra estadística representativa, garantizando la reproducibilidad del experimento.

## ⚙️ Mecánica de los Scripts

### 1. `descargar_dataset.py`
Este script establece una conexión directa con el repositorio de Zenodo. Descarga el archivo masivo `RELLISUR.zip` (8.9 GB) utilizando una estrategia de *streaming* por bloques. Esto optimiza el uso de la memoria RAM y proporciona una barra de progreso visual en la terminal.

### 2. `extraer_dataset.py`
Este script evita la descompresión total del archivo en el disco. Lee directamente la tabla de contenidos del archivo ZIP en memoria, aplica una semilla aleatoria (`seed=42`) para seleccionar 1062 pares de imágenes de forma determinista y los extrae estructuradamente.

## 🚀 Ejecución del Pipeline

Asegúrate de ejecutar estos comandos desde la **raíz del proyecto** con tu entorno virtual activado.

**Paso 1: Descargar los datos brutos**
```bash
python ingesta/descargar_dataset.py
```

**Paso 2: Extraer la muestra de evaluación**

```bash
python ingesta/extraer_dataset.py

```

## 📂 Artefactos Generados

Tras la ejecución exitosa de ambos scripts, se creará automáticamente una carpeta `dataset/` en la raíz del proyecto. Esta carpeta está excluida del control de versiones (`.gitignore`) y presentará la siguiente topología:

```text
dataset/
├── RELLISUR.zip               # Archivo comprimido original
└── img/                       # Subconjunto extraído para la evaluación
    ├── original/              # 1062 imágenes de referencia (NLHR/X1)
    └── oscurecida/            # 1062 imágenes subexpuestas (LLLR) correspondientes
```