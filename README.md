# Analisis de Inteligencia de Cliente y Reputacion: Ryanair Business Insights 2026

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Dash](https://img.shields.io/badge/Dash-Plotly-informational?style=flat&logo=plotly)
![NLP](https://img.shields.io/badge/NLP-NLTK%20%7C%20VADER-success?style=flat)
![NetworkX](https://img.shields.io/badge/NetworkX-Redes_Semanticas-success?style=flat)
![Gephi](https://img.shields.io/badge/Gephi-0.10.1-orange?style=flat)

## Descripcion del Proyecto

Este repositorio contiene un proyecto integral de Business Intelligence y Ciencia de Datos enfocado en decodificar la "Voz del Cliente" de la aerolinea Ryanair. 

A traves de la extraccion y procesamiento de 2.249 reseñas verificadas (obtenidas de Skytrax), este estudio combina tecnicas de Procesamiento de Lenguaje Natural (NLP) y Mineria de Redes Semanticas para:
1. Comprender la polaridad emocional del consumidor aplicando Analisis de Sentimiento Basado en Aspectos (ABSA) con el modelo lexico VADER.
2. Segmentar la percepcion cualitativa en 6 pilares operativos clave (Puntualidad, Precio, Equipaje, Personal, Asientos y Experiencia General).
3. Construir grafos de co-ocurrencia de palabras para mapear cognitivamente como estructura el pasajero su experiencia y detectar que atributos generan mayor lealtad o friccion.

El entregable final es un Dashboard Interactivo construido con Plotly Dash que integra KPIs, mapas topologicos segmentados por pilar semantico y un Data Storytelling con conclusiones accionables para la compañia.

---

## Estructura del Repositorio

El proyecto sigue esta arquitectura de directorios:

    Proyecto_sentimiento_ryanair/
    │
    ├── app/
    │   ├── assets/                           # Recursos estaticos (exportados desde Gephi)
    │   │   ├── Asientos.png
    │   │   ├── Equipaje.png
    │   │   ├── Experiencia.png
    │   │   ├── Nodos.png
    │   │   ├── Personal.png
    │   │   ├── Precio.png
    │   │   └── Puntualidad.png
    │   └── dashboard.py                      # Codigo fuente principal de la aplicacion web
    │
    ├── data/
    │   ├── processed/                        # Tablas procesadas y archivos estructurales
    │   │   ├── red_radial_ryanair.gexf       # Archivo base para visualizar la red en Gephi
    │   │   └── ryanair_limpios_temas.csv
    │   └── raw/                              # Dataset original (Ignorado en GitHub por peso)
    │       └── ryanair_reviews.csv
    │
    ├── notebook/
    │   └── 1_EDA_y_Preprocesamiento.ipynb    # Pipeline de NLP, VADER, ABSA y grafos (NetworkX)
    │
    ├── venv/                                 # Entorno virtual (Ignorado en .gitignore)
    ├── .gitignore                            # Configuracion de archivos ignorados (venv, __pycache__, data/raw, etc.)
    ├── README.md                             # Documentacion del proyecto
    └── requirements.txt                      # Dependencias de Python

---

## Tecnologias Utilizadas

* **Lenguaje:** Python 3.x
* **Manipulacion de Datos:** pandas, numpy
* **Procesamiento de Lenguaje Natural (NLP):** nltk (Stopwords, VADER SentimentIntensityAnalyzer), re (Expresiones regulares)
* **Analisis de Redes:** networkx (Creacion de grafos y exportacion GEXF)
* **Visualizacion de Grafos:** Gephi 0.10.1 (Algoritmo ForceAtlas2, clusterizacion semantica)
* **Desarrollo Web / Dashboarding:** dash, plotly, matplotlib, seaborn

---

## Instalacion y Configuracion

Para replicar este entorno y ejecutar el dashboard en tu maquina local, sigue estos pasos:

1. Clonar el repositorio:
    ```bash
    git clone [https://github.com/TU_USUARIO/Proyecto_sentimiento_ryanair.git](https://github.com/TU_USUARIO/Proyecto_sentimiento_ryanair.git)
    cd Proyecto_sentimiento_ryanair
    ```

2. Crear y activar un entorno virtual (Recomendado):
* En Windows:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
* En macOS / Linux:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4. Descargar los recursos necesarios de NLTK (ejecutar en terminal de Python):
    ```python
    import nltk
    nltk.download('stopwords')
    nltk.download('vader_lexicon')
    nltk.download('punkt')
    ```

5. Nota sobre datos crudos: 
   Debido a las reglas del `.gitignore`, la carpeta `data/raw/` no se sube al repositorio. Deberas colocar el archivo `ryanair_reviews.csv` manualmente en esa ruta antes de ejecutar el notebook.

---

## Flujo de Ejecucion

### Fase 1: Preprocesamiento y Modelado Semantico (Jupyter)
1. Inicia Jupyter Notebook o abre Visual Studio Code.
2. Navega a `notebook/1_EDA_y_Preprocesamiento.ipynb`.
3. Ejecuta todas las celdas. Este proceso limpia el texto, clasifica el sentimiento, genera la matriz de co-ocurrencias y exporta los datos a la carpeta `data/processed/`.

*Nota sobre Gephi:* El archivo `red_radial_ryanair.gexf` generado se utilizo en el software Gephi para visualizar la red topologica, separando los clusteres mediante un diseño Hub-and-Spoke. Las imagenes resultantes se encuentran alojadas en `app/assets/`.

### Fase 2: Lanzamiento del Dashboard
1. Navega a la carpeta de la aplicacion:
    ```bash
    cd app
    ```
2. Ejecuta el servidor Dash:
    ```bash
    python dashboard.py
    ```
3. Accede a `http://127.0.0.1:8055/` en tu navegador web.

---

## Conclusiones Principales del Estudio

El analisis topologico y de sentimiento arrojo los siguientes hallazgos empiricos:

1. **Topologia de Clusteres Desconectados:** Los seis pilares semanticos operan como comunidades independientes. El cliente evalua la experiencia en compartimentos estancos; los fallos operativos (ej. maletas) no suelen propagarse semanticamente hacia otros pilares (ej. personal), permitiendo intervenciones quirurgicas.
2. **Modelo de Satisfaccion Bimodal (Polarizacion):** La red del pilar de "Experiencia" demuestra que no existe un usuario medio: el pasajero detesta el servicio (generando superlativos negativos) o se convierte en promotor. La arista verde mas gruesa del modelo corresponde a la palabra *"return"*, evidenciando que el pasajero satisfecho repite.
3. **El Factor Humano como Escudo Reputacional:** El pilar "Personal/Tripulacion" es la sub-red mas positiva del modelo. El nodo *"crew"* concentra la mayor densidad de conexiones favorables (*friendly*, *helpful*), amortiguando la insatisfaccion generada por fallos sistemicos de la compañia.
4. **Fricciones Estructurales (Price Decoupling y Tiempos):** 
    * En el pilar de **Precio**, el cliente valora positivamente la tarifa base (*value*), pero las aristas de rechazo mas fuertes apuntan a los procesos de pago (*pay*, *extra fees*).
    * En **Puntualidad**, la frustracion no nace del retraso *per se*, sino del nodo temporal de espera (*hours*, *waiting*) sin comunicacion proactiva.
5. **Efecto Contaminante de la Experiencia Digital (UX):** Un hallazgo transversal fue la aparicion del termino *"website"* con conexiones negativas dentro de la red del pilar de **Asientos**. El proceso de seleccion online contamina retroactivamente la percepcion fisica del producto en cabina.

---
**Proyecto Universitario - Modelos Predictivos III: Analisis de Opinion Publica y Sentimiento**