# pdi-lowlight-benchmark

Este repositorio contiene el código fuente y la metodología para evaluar y comparar técnicas de mejora de imágenes en condiciones de baja luminosidad. El proyecto utiliza una muestra representativa del dataset RELLISUR para contrastar algoritmos clásicos como la Ecualización de Histograma tradicional y CLAHE mediante métricas cuantitativas (PSNR, AMBE).

## 🛠️ Configuración del Entorno (Conda)

Para garantizar la reproducibilidad estricta de los experimentos, la gestión de dependencias y versiones se realiza a través de Anaconda. 

Sigue estos pasos para inicializar el entorno de desarrollo:

1. Asegúrate de tener instalado [Anaconda](https://www.anaconda.com/) o Miniconda en tu sistema.
2. Clona este repositorio y navega a la carpeta raíz.
3. Crea el entorno virtual a partir del archivo de configuración:
```bash
   conda env create -f environment.yml
```
4. Activa el entorno de trabajo:
```bash
conda activate tp_1
```


## 📂 Estructura del Proyecto

El código está modularizado para separar la obtención de datos, el procesamiento algorítmico y la evaluación cuantitativa. La estructura principal del repositorio es la siguiente:

```text
├── environment.yml          # Dependencias y configuración del entorno Conda
├── README.md                # Documentación principal del proyecto
├── LICENSE                  # Licencia de uso del código
├── ingesta/                 # Carpeta para la obtención y preparación de datos
│   ├── descargar_dataset.py # Script de descarga segura por bloques (Streaming)
│   └── extraer_dataset.py   # Script de muestreo aleatorio reproducible con semilla
```

## 🚀 Flujo de Ejecución

Para replicar el experimento de principio a fin, los scripts deben ejecutarse en un orden lógico estricto. Todas las ejecuciones deben realizarse con el entorno Conda activado.

**Paso 1: Obtención de Datos**
Descarga el dataset original RELLISUR (8.9 GB). El script incluye una barra de progreso para monitorear la descarga.

```bash
python src/descargar_dataset.py

```

**Paso 2: Muestreo Representativo**
Extrae una muestra estadística de 1062 pares de imágenes directamente a memoria (sin descomprimir todo el ZIP en disco). Este script asegura el emparejamiento de las imágenes subexpuestas con sus referencias.

```bash
python src/extraer_dataset.py

```

**Paso 3: Procesamiento y Evaluación (Próximamente)**
Aplica los algoritmos de mejora sobre las imágenes extraídas y tabula las métricas de error.

```bash
# python src/evaluar_metricas.py

```

## 👥 Autores y Colaboradores

Este proyecto fue desarrollado como parte de la evaluación en Procesamiento Digital de Imágenes.

* **[Tu Nombre]** - *Desarrollo de Arquitectura y Scripts Base* - [Tu GitHub/LinkedIn]
* **[Nombre Integrante 2]** - *[Rol o Aporte]* - [Enlace]
* **[Nombre Integrante 3]** - *[Rol o Aporte]* - [Enlace]

## 📄 Licencia

Este repositorio está sujeto a dos esquemas de licenciamiento distintos:

* **Código Fuente:** Los scripts de Python (descarga, extracción y algoritmos) desarrollados para este proyecto se distribuyen bajo la [Licencia MIT](https://www.google.com/search?q=LICENSE). Eres libre de utilizarlos, modificarlos y distribuirlos.
* **Base de Datos (RELLISUR):** Las imágenes empleadas en los experimentos pertenecen a los autores de RELLISUR (*Aakerberg et al., 2021*) y se distribuyen bajo la licencia **Creative Commons Attribution 4.0 International (CC BY 4.0)**.