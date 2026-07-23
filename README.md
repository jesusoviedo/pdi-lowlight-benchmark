# Evaluación de Algoritmos para la Mejora de Imágenes Subexpuestas

Este repositorio contiene el código fuente y la metodología para evaluar y comparar técnicas de mejora de imágenes en condiciones de baja luminosidad. El proyecto utiliza una muestra determinista del dataset [RELLISUR](https://vap.aau.dk/rellisur/) para contrastar algoritmos clásicos (Ecualización de Histograma tradicional y CLAHE) y un algoritmo denominado **BHE2PL (Bi-Histogram Equalization with Two Plateau Limits)**. La comparación se realiza mediante métricas cuantitativas de error espacial, preservación de brillo y similitud estructural (PSNR, AMBE, Contraste, Entropía y SSIM).


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

El código está fuertemente modularizado para separar la obtención de datos, el procesamiento algorítmico, la evaluación matemática y la orquestación. La topología principal es la siguiente:

```text
├── environment.yml          # Dependencias y configuración del entorno Conda
├── README.md                # Documentación principal y punto de entrada del proyecto
├── LICENSE                  # Licencia de uso del código
├── ingesta/                 # Módulo para la obtención y preparación de datos
│   ├── descargar_dataset.py # Script de descarga segura por bloques (Streaming)
│   ├── extraer_dataset.py   # Script de extracción parametrizable y re-indexación determinista
│   └── README.md            # Documentación de parámetros de ingesta
├── realce/                  # Módulo de procesamiento en el dominio espacial
│   ├── algoritmos.py        # Implementaciones vectorizadas de Ecualización Global, CLAHE y BHE2PL
│   ├── __init__.py          # Inicializador del paquete
│   └── README.md            # Documentación teórica y DOI de los algoritmos
├── metricas/                # Módulo de evaluación matemática (utilitarios)
│   ├── referenciadas.py     # Métricas con Ground Truth (PSNR, AMBE, SSIM)
│   ├── no_referenciadas.py  # Métricas espaciales sin referencia (Entropía, Contraste)
│   ├── __init__.py          # Inicializador del paquete
│   └── README.md            # Documentación del patrón de diccionarios de evaluación
├── evaluacion/              # Módulo principal de ejecución
│   ├── orquestador_evaluacion.py # Motor que acopla los algoritmos con las métricas por lotes
│   └── README.md            # Instrucciones de I/O y parámetros de reproducibilidad
├── analisis/                # Módulo de evaluación estadística y cuantitativa
│   ├── analisis_estadistico_resultados.ipynb # Cuaderno de Jupyter con el análisis de datos
│   └── README.md            # Instrucciones de ejecución del análisis
├── dataset/                 # Directorio generado dinámicamente tras la ingesta (excluido en .gitignore)
└── experimento/             # Directorio generado dinámicamente por el orquestador (excluido en .gitignore)

```


## 🚀 Flujo de Ejecución

Para replicar el experimento de principio a fin, el proyecto está diseñado en tres pasos secuenciales. Todas las ejecuciones deben realizarse con el entorno Conda `tp_1` activado.

**Paso 1: Obtención y Preparación de Datos (`ingesta/`)**
Navegue a la carpeta `ingesta/`. Los scripts contenidos allí se encargan de descargar el dataset masivo desde Zenodo y de extraer una muestra estadística reproducible de 850 pares de imágenes. Consulte el documento `ingesta/README.md` para conocer los comandos exactos de ejecución.

**Paso 2: Ejecución del Experimento (`evaluacion/`)**
Navegue a la carpeta `evaluacion/` y ejecute el orquestador principal. Este componente importa los algoritmos del módulo `realce/` y las funciones matemáticas del módulo `metricas/`. El sistema procesa las imágenes por lotes, guarda los resultados visuales en la carpeta `experimento/img` y genera el registro de evaluación en `experimento/json/resultados_evaluacion.json`. Consulte el documento `evaluacion/README.md` para conocer los comandos exactos de ejecución.

**Paso 3: Análisis Estadístico y Evaluación (`analisis/`)**
Navegue a la carpeta `analisis/` e inicie la interfaz interactiva de Jupyter Lab. Este directorio contiene el cuaderno que procesa el archivo JSON generado en el paso anterior. El cuaderno ejecuta código que aplica operaciones matriciales con Pandas para calcular métricas relativas y generar las tablas de resultados. El análisis culmina con la ejecución de pruebas de inferencia estadística (Kruskal-Wallis) para validar matemáticamente el rendimiento de los algoritmos.


## 👥 Autores y Colaboradores

Este proyecto fue desarrollado como parte de la evaluación en Procesamiento Digital de Imágenes.

* **Jesús Oviedo Riquelme** - [[GitHub](https://www.google.com/search?q=https://github.com/jesusoviedo)/[LinkedIn](https://www.google.com/search?q=https://www.linkedin.com/in/jesusoviedoriquelme/)]
* **Sofía Rivas Gaona**
* **Liz Torres Cáceres**
* **Gabriela Velázquez Sánchez**
* **Miguel Angel Vera**
* **Ernesto Yampey Cristaldo**

## 📄 Licencia

Este repositorio está sujeto a dos esquemas de licenciamiento distintos:

* **Código Fuente:** Los scripts de Python desarrollados se distribuyen bajo la [Licencia MIT](https://www.google.com/search?q=./LICENSE).
* **Base de Datos (RELLISUR):** Las imágenes empleadas en los experimentos pertenecen a los autores de RELLISUR (*Aakerberg et al., 2021*) y se distribuyen bajo la licencia **Creative Commons Attribution 4.0 International (CC BY 4.0)**.