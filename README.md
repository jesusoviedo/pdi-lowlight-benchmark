# Evaluación de Algoritmos para la Mejora de Imágenes Subexpuestas

Este repositorio contiene el código fuente y la metodología para evaluar y comparar técnicas de mejora de imágenes en condiciones de baja luminosidad. El proyecto utiliza una muestra representativa del dataset [RELLISUR](https://vap.aau.dk/rellisur/) para contrastar algoritmos clásicos como la Ecualización de Histograma tradicional y CLAHE mediante métricas cuantitativas de error espacial y estructural (PSNR, AMBE, Contraste y Entropía).

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
│   ├── extraer_dataset.py   # Script de extracción parametrizable y re-indexación
│   └── README.md            # Documentación e instrucciones específicas de ingesta
├── realce/                  # Módulo de procesamiento espacial (Ecualización, CLAHE)
│   ├── algoritmos.py        # Implementaciones de ecualización global y CLAHE
│   ├── __init__.py          # Inicializador del paquete
│   └── README.md            # Documentación técnica específica del realce
├── metricas/                # Módulo de evaluación matemática (utilitarios)
│   ├── __init__.py          # Inicializador del paquete
│   ├── referenciadas.py     # Métricas con Ground Truth (PSNR, AMBE)
│   ├── no_referenciadas.py  # Métricas espaciales (Entropía, Contraste)
│   └── README.md            # Documentación técnica específica del módulo
└── dataset/                 # Directorio generado dinámicamente (excluido en .gitignore)

```

## 🚀 Flujo de Ejecución

Para replicar el experimento de principio a fin, el proyecto está diseñado en fases modulares que deben ejecutarse en un orden lógico estricto. Todas las ejecuciones deben realizarse con el entorno Conda activado.

**Fase 1: Obtención y Preparación de Datos (`ingesta/`)**
Dirígete a la carpeta `ingesta/` y consulta las instrucciones detalladas en su archivo `README.md` interno. Allí se documentan los pasos exactos para descargar el dataset original de Zenodo y extraer la muestra estadística representativa (hasta 850 pares únicos) sin colapsar la memoria del sistema.

**Fase 2: Procesamiento y Realce Espacial (`realce/`)**
Los algoritmos de mejora en el dominio espacial (ecualización global y CLAHE) se encuentran implementados de forma modular en el paquete `realce/`. Estos métodos operan sobre imágenes en escala de grises para reasignar los niveles de intensidad y optimizar la visibilidad de los detalles. Consulta la documentación interna de la carpeta para verificar los parámetros de configuración.

**Fase 3: Evaluación Cuantitativa (`metricas/`)**
El módulo `metricas/` agrupa las funciones matemáticas referenciadas (`referenciadas.py`) y no referenciadas (`no_referenciadas.py`) necesarias para calcular el desempeño de cada técnica sobre las imágenes procesadas en comparación con el *Ground Truth*.

## 👥 Autores y Colaboradores

Este proyecto fue desarrollado como parte de la evaluación en Procesamiento Digital de Imágenes.

* **Jesús Oviedo Riquelme** - [[GitHub](https://github.com/jesusoviedo)/[LinkedIn](https://www.linkedin.com/in/jesusoviedoriquelme/)]
* **[Sofía Rivas Gaona]** - [Tu GitHub/LinkedIn]
* **[Liz Torres Cáceres]** - [Tu GitHub/LinkedIn]
* **[Gabriela Velázquez Sánchez]** - [Tu GitHub/LinkedIn]
* **[Miguel Angel Vera]** - [Tu GitHub/LinkedIn]
* **[Ernesto Yampey Cristaldo]** - [Tu GitHub/LinkedIn]

## 📄 Licencia

Este repositorio está sujeto a dos esquemas de licenciamiento distintos:

* **Código Fuente:** Los scripts de Python desarrollados para este proyecto se distribuyen bajo la [Licencia MIT](https://www.google.com/search?q=LICENSE). Eres libre de utilizarlos, modificarlos y distribuirlos.
* **Base de Datos (RELLISUR):** Las imágenes empleadas en los experimentos pertenecen a los autores de RELLISUR (*Aakerberg et al., 2021*) y se distribuyen bajo la licencia **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
