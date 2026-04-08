# =================================================================
# CUADRO DE MANDO INTEGRAL: REPUTACIÓN Y CUSTOMER INTELLIGENCE
# PROYECTO: RYANAIR BUSINESS INSIGHTS 2026
# =================================================================

import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.express as px
import pandas as pd
import os

# 1. CARGA Y PREPARACIÓN DE DATOS
# =================================================================
try:
    df = pd.read_csv('../data/processed/ryanair_limpios_temas.csv')
    df['Date Published'] = pd.to_datetime(df['Date Published'])
except Exception:
    # Carga de seguridad si el archivo de temas no existe
    df = pd.read_csv('../data/processed/ryanair_limpios.csv')

# 2. CONFIGURACIÓN DE ESTILOS Y CONSTANTES
# =================================================================
COLORES = {
    'positive': '#27AE60', # Verde
    'neutral':  '#F1C40F', # Amarillo
    'negative': '#C0392B', # Rojo
    'accent':   '#073590', # Azul Ryanair
    'bg':       '#F4F7F9'
}

ESTILO_CARD = {
    'backgroundColor': 'white',
    'padding': '35px',
    'borderRadius': '15px',
    'boxShadow': '0 10px 30px rgba(0,0,0,0.05)',
    'marginBottom': '30px',
    'border': '1px solid #E5E8E8'
}

# 3. CONTENIDO TEXTUAL FORMAL
# =================================================================
INTRO_METODOLOGIA = """
El presente sistema de Business Intelligence emplea un pipeline avanzado de **Procesamiento de Lenguaje Natural (NLP)** para decodificar la percepción pública de Ryanair. A diferencia de las métricas tradicionales, este análisis utiliza 
**Análisis de Sentimiento Basado en Aspectos (ABSA)**, permitiendo separar la opinión general de los atributos 
específicos del servicio. La visualización topológica permite observar no solo *qué* se dice, sino *cómo* se 
relacionan los conceptos en la mente del consumidor.
"""

EXPLICACION_GRAFOS = """
### Interpretación de la Red Radial de Atributos
La visualización de grafos emplea una topología **Hub-and-Spoke**. Cada pilar operativo actúa como un nodo central 
(Hub) que atrae o repele términos descriptivos según su co-ocurrencia estadística.

* **Aristas Verdes (Positivas):** Representan una fuerte correlación entre el atributo y una alta satisfacción. Son los activos competitivos de la marca.
* **Aristas Rojas (Negativas):** Identifican "Puntos de Dolor" críticos donde el servicio genera fricción y sentimientos de rechazo.
* **Aristas Amarillas (Neutrales):** Indican aspectos meramente descriptivos o transaccionales que no generan una carga emocional determinante, pero son estructurales en la reseña.
"""

# 4. INICIALIZACIÓN DE LA APP
# =================================================================
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Ryanair Intelligence Dashboard"

app.layout = html.Div(style={'backgroundColor': COLORES['bg'], 'fontFamily': 'Segoe UI, Helvetica', 'padding': '0'}, children=[

    # --- HEADER CORPORATIVO ---
    html.Header(style={
        'background': f'linear-gradient(135deg, {COLORES["accent"]} 0%, #1E50A2 100%)',
        'padding': '60px 50px', 'color': 'white', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)'
    }, children=[
        html.H1("RYANAIR: CUSTOMER INTELLIGENCE DASHBOARD", style={'margin': '0', 'fontSize': '2.8em', 'fontWeight': '800'}),
        html.P("Auditoría de Reputación y Análisis de Redes de Opinión Pública", style={'fontSize': '1.3em', 'opacity': '0.8', 'marginTop': '10px'})
    ]),

    html.Div(style={'padding': '40px 60px'}, children=[

        # --- SECCIÓN 1: INDICADORES CLAVE (KPIs) ---
        html.Div(style={'display': 'flex', 'gap': '25px', 'marginBottom': '40px'}, children=[
            html.Div(style={**ESTILO_CARD, 'flex': '1', 'textAlign': 'center'}, children=[
                html.H3(f"{len(df):,}", style={'color': COLORES['accent'], 'fontSize': '2.5em', 'margin': '0'}),
                html.P("INTERACCIONES ANALIZADAS", style={'fontWeight': 'bold', 'color': '#7F8C8D'})
            ]),
            html.Div(style={**ESTILO_CARD, 'flex': '1', 'textAlign': 'center'}, children=[
                html.H3(f"{df['Overall Rating'].mean():.1f} / 10", style={'color': '#F39C12', 'fontSize': '2.5em', 'margin': '0'}),
                html.P("SATISFACCIÓN MEDIA", style={'fontWeight': 'bold', 'color': '#7F8C8D'})
            ]),
            html.Div(style={**ESTILO_CARD, 'flex': '1', 'textAlign': 'center'}, children=[
                html.H3(f"{(df['Sentiment_Label']=='negative').mean()*100:.1f}%", style={'color': COLORES['negative'], 'fontSize': '2.5em', 'margin': '0'}),
                html.P("ÍNDICE DE DETRACCIÓN", style={'fontWeight': 'bold', 'color': '#7F8C8D'})
            ]),
        ]),

        # --- SECCIÓN 2: METODOLOGÍA ---
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Contexto Metodológico", style={'color': COLORES['accent'], 'borderBottom': f'2px solid {COLORES["accent"]}', 'paddingBottom': '10px'}),
            dcc.Markdown(INTRO_METODOLOGIA, style={'lineHeight': '1.8', 'fontSize': '1.1em'})
        ]),

        # --- SECCIÓN 3: EXPLORACIÓN POR PILARES (INTERACTIVO) ---
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Análisis Forense de Pilares Operativos", style={'color': COLORES['accent']}),
            dcc.Markdown(EXPLICACION_GRAFOS),
            
            dcc.Tabs(id="tabs-pilares", value='tab-puntualidad', children=[
                dcc.Tab(label='PUNTUALIDAD', value='tab-puntualidad', selected_style={'backgroundColor': COLORES['accent'], 'color': 'white'}),
                dcc.Tab(label='PRECIO', value='tab-precio', selected_style={'backgroundColor': COLORES['accent'], 'color': 'white'}),
                dcc.Tab(label='EQUIPAJE', value='tab-equipaje', selected_style={'backgroundColor': COLORES['accent'], 'color': 'white'}),
                dcc.Tab(label='PERSONAL', value='tab-personal', selected_style={'backgroundColor': COLORES['accent'], 'color': 'white'}),
                dcc.Tab(label='ASIENTOS', value='tab-asientos', selected_style={'backgroundColor': COLORES['accent'], 'color': 'white'}),
                dcc.Tab(label='EXPERIENCIA', value='tab-experiencia', selected_style={'backgroundColor': COLORES['accent'], 'color': 'white'}),
            ]),
            html.Div(id='tabs-content-pilares', style={'padding': '40px 0'})
        ]),

        # --- SECCIÓN 4: MAPA GLOBAL DE NODOS ---
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Topología de Red Global", style={'color': COLORES['accent']}),
            html.P("Visión macroscópica de las interacciones semánticas en el dataset completo."),
            html.Img(src='/assets/Nodos.png', style={'width': '100%', 'borderRadius': '10px', 'marginTop': '20px'})
        ]),

        # --- SECCIÓN 5: AUDITORÍA DE DATOS ---
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Auditoría de Reseñas por Sentimiento", style={'color': COLORES['accent']}),
            dash_table.DataTable(
                data=df.head(100).to_dict('records'),
                columns=[
                    {"name": "Tema", "id": "Tema"},
                    {"name": "Sentimiento", "id": "Sentiment_Label"},
                    {"name": "Comentario Procesado", "id": "Text_Clean"}
                ],
                page_size=10,
                style_cell={'textAlign': 'left', 'padding': '15px', 'fontSize': '13px'},
                style_header={'backgroundColor': COLORES['accent'], 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'filter_query': '{Sentiment_Label} = "positive"'}, 'color': COLORES['positive']},
                    {'if': {'filter_query': '{Sentiment_Label} = "negative"'}, 'color': COLORES['negative']},
                ]
            )
        ])
    ]),

    html.Footer(style={'textAlign': 'center', 'padding': '40px', 'color': '#BDC3C7'}, children=[
        html.P("© 2026 Inteligencia de Mercado - Análisis de Opinión Pública y Modelos Predictivos III")
    ])
])

# 5. CALLBACK PARA INTERACTIVIDAD DE PESTAÑAS
# =================================================================
@app.callback(Output('tabs-content-pilares', 'children'),
              Input('tabs-pilares', 'value'))
def render_content(tab):
    content = {
        'tab-puntualidad': {
            'img': 'Puntualidad.png',
            'title': 'Pilar: Puntualidad y Gestión del Tiempo',
            'desc': """
            **Análisis de Aristas:**
            * **Negativo (Rojo):** Los términos **"hours"**, **"delayed"** y **"waiting"** dominan la red. Esto indica que la frustración del cliente no nace solo del retraso, sino del tiempo de inactividad percibido en la terminal.
            * **Positivo (Verde):** Las conexiones con **"ontime"** validan la promesa básica de la aerolínea cuando los procesos logísticos son exitosos.
            """
        },
        'tab-precio': {
            'img': 'Precio.png',
            'title': 'Pilar: Economía y Transparencia de Costes',
            'desc': """
            **Análisis de Aristas:**
            * **Positivo (Verde):** El término **"value"** y **"price"** son los nodos con mayor conexión verde. El cliente percibe el beneficio económico como el eje central de su lealtad.
            * **Negativo (Rojo):** La fricción se concentra en **"extra"**, **"fees"** y **"refund"**. La red detecta un sentimiento de castigo financiero por servicios secundarios o dificultades en reembolsos.
            """
        },
        'tab-equipaje': {
            'img': 'Equipaje.png',
            'title': 'Pilar: Logística de Equipajes y Embarque',
            'desc': """
            **Análisis de Aristas:**
            * **Negativo (Rojo):** Las aristas rojas hacia **"fees"** y **"checkin"** revelan que el problema es procedimental y monetario, más que una pérdida física de maletas.
            * **Positivo (Verde):** La rapidez en el **"boarding"** se identifica como una ventaja competitiva.
            """
        },
        'tab-personal': {
            'img': 'Personal.png',
            'title': 'Pilar: Factor Humano y Atención al Cliente',
            'desc': """
            **Análisis de Aristas:**
            * **Positivo (Verde):** Aristas vibrantes hacia **"friendly"** y **"professional"**. El capital humano de Ryanair es capaz de generar experiencias memorables a pesar del modelo bajo coste.
            * **Negativo (Rojo):** El nodo **"ignored"** es crítico. El sentimiento negativo se dispara cuando el pasajero percibe falta de asistencia ante problemas operativos.
            """
        },
        'tab-asientos': {
            'img': 'Asientos.png',
            'title': 'Pilar: Confort de Cabina y Ergonomía',
            'desc': """
            **Análisis de Aristas:**
            * **Positivo (Verde):** Sorprendente fortaleza en **"legroom"** y **"space"**. Los datos sugieren que la renovación de la flota está rompiendo el estigma de incomodidad absoluta.
            * **Negativo (Rojo):** Quejas puntuales sobre la imposibilidad de **"recline"** (reclinación) y la dureza de los asientos en trayectos largos.
            """
        },
        'tab-experiencia': {
            'img': 'Experiencia.png',
            'title': 'Pilar: Valoración Holística del Viaje',
            'desc': """
            **Análisis de Aristas:**
            * **Positivo (Verde):** El nodo **"recommend"** actúa como el KPI final de éxito.
            * **Negativo (Rojo):** Las conexiones con **"worst"** y **"bad"** suelen ser el resultado de fallos combinados en Puntualidad y Equipaje.
            """
        }
    }

    data = content[tab]
    return html.Div(style={'display': 'flex', 'gap': '40px', 'alignItems': 'top'}, children=[
        html.Div(style={'flex': '1'}, children=[
            html.H3(data['title'], style={'color': COLORES['accent']}),
            dcc.Markdown(data['desc'], style={'lineHeight': '1.8'})
        ]),
        html.Div(style={'flex': '1', 'textAlign': 'right'}, children=[
            html.Img(src=f'/assets/{data["img"]}', style={'width': '100%', 'borderRadius': '12px', 'boxShadow': '0 8px 20px rgba(0,0,0,0.1)'})
        ])
    ])

# 6. EJECUCIÓN
# =================================================================
if __name__ == '__main__':
    app.run(debug=True, port=8055)