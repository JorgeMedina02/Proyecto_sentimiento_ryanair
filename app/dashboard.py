# =================================================================
# CUADRO DE MANDO INTEGRAL: REPUTACIÓN Y CUSTOMER INTELLIGENCE
# PROYECTO: RYANAIR BUSINESS INSIGHTS 2026
# =================================================================

import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.graph_objects as go
import pandas as pd
import os

# 1. CARGA Y PREPARACIÓN DE DATOS
# =================================================================
try:
    df = pd.read_csv('../data/processed/ryanair_limpios_temas.csv')
    df['Date Published'] = pd.to_datetime(df['Date Published'])
except Exception:
    df = pd.read_csv('../data/processed/ryanair_limpios.csv')

# 2. CONFIGURACIÓN DE ESTILOS
# =================================================================
COLORES = {
    'positive': '#27AE60',
    'neutral':  '#F1C40F',
    'negative': '#C0392B',
    'accent':   '#073590',
    'accent2':  '#1E50A2',
    'bg':       '#F0F2F5',
    'card':     '#FFFFFF',
    'text':     '#1A1A2E',
    'muted':    '#5D6D7E',
    'warn':     '#E67E22',
}

ESTILO_CARD = {
    'backgroundColor': COLORES['card'],
    'padding': '40px',
    'borderRadius': '16px',
    'boxShadow': '0 4px 24px rgba(7,53,144,0.07)',
    'marginBottom': '32px',
    'border': '1px solid #DDE3EC'
}

ESTILO_KPI = {
    **ESTILO_CARD,
    'flex': '1',
    'textAlign': 'center',
    'padding': '32px 20px',
    'borderTop': f'4px solid {COLORES["accent"]}',
}

# 3. MÉTRICAS GLOBALES
# =================================================================
total_resenas   = len(df)
rating_medio    = df['Overall Rating'].mean()
tasa_detraccion = (df['Sentiment_Label'] == 'negative').mean() * 100
tasa_promocion  = (df['Sentiment_Label'] == 'positive').mean() * 100

# Sentimiento por tema
if 'Tema' in df.columns:
    sent_por_tema = (
        df.groupby('Tema')['Sentiment_Score']
        .agg(['mean', 'count'])
        .rename(columns={'mean': 'Sentimiento_Medio', 'count': 'Volumen'})
        .reset_index()
    )
    sent_pos_neg = (
        df.groupby(['Tema', 'Sentiment_Label'])
        .size().unstack(fill_value=0).reset_index()
    )
else:
    sent_por_tema = pd.DataFrame()
    sent_pos_neg  = pd.DataFrame()

# 4. CONTENIDO TEXTUAL
# =================================================================
INTRO_METODOLOGIA = """
Este sistema de **Business Intelligence** emplea un pipeline de **Procesamiento de Lenguaje Natural (NLP)** 
para decodificar la percepción pública de Ryanair a partir de 2.249 reseñas verificadas de pasajeros.

A diferencia de los análisis de puntuación tradicionales, este proyecto implementa **Análisis de Sentimiento 
Basado en Aspectos (ABSA)**: cada reseña se descompone en los pilares operativos que menciona, asignando 
una carga emocional específica a cada uno. El modelo de análisis de sentimiento es **VADER** 
(*Valence Aware Dictionary and sEntiment Reasoner*), calibrado para lenguaje coloquial y opiniones de consumidor.

La etapa final construye una **Red Semántica de Co-ocurrencias** con Gephi: un grafo donde cada nodo es un 
concepto del vocabulario del cliente y cada arista refleja que ambos términos aparecieron en la misma reseña. 
El color de la arista representa el **sentimiento medio ponderado** de todas las reseñas donde esa 
co-ocurrencia se produjo. El resultado es un mapa cognitivo de cómo el consumidor estructura mentalmente 
su experiencia de vuelo.
"""

LEYENDA_GRAFOS = """
### Clave de lectura

| Color de arista | Significado | Implicación |
|---|---|---|
| 🟢 **Verde** | Sentimiento positivo (score ≥ +0.05) | Activo competitivo — reforzar y comunicar |
| 🔴 **Rojo** | Sentimiento negativo (score ≤ −0.05) | Punto de dolor — intervención prioritaria |
| 🟡 **Amarillo** | Neutro (−0.05 a +0.05) | Atributo descriptivo sin carga emocional |

El **grosor** de la arista indica la frecuencia de co-ocurrencia: arista gruesa = mayor robustez estadística.
"""

# 5. DATOS DE PILARES
# =================================================================
PILARES = {
    'tab-puntualidad': {
        'img': 'Puntualidad.png',
        'title': '⏱ Pilar I: Puntualidad y Gestión del Tiempo',
        'kpi_color': COLORES['negative'],
        'badge': 'ALERTA CRÍTICA',
        'badge_color': COLORES['negative'],
        'analisis': """
### Diagnóstico de la Red

La red de Puntualidad es la más **desequilibrada negativamente** de todo el modelo. El nodo central 
está rodeado de forma abrumadora por aristas rojas, convirtiendo este pilar en el **principal driver 
de insatisfacción** de la aerolínea.

**Señales negativas dominantes:**
- **"hours" y "hour"** — aristas rojas más gruesas: la queja no es solo el retraso en sí, sino la 
  **duración percibida de la espera**, que genera frustración exponencial.
- **"cancelled"**, **"delayed"** y **"late"** — clúster semántico de incumplimiento operativo más 
  citado en todo el dataset.
- **"stuck"** y **"waiting"** — componente de **impotencia y abandono**: no solo hay retraso, 
  sino ausencia de información o soluciones alternativas.
- **"later"** — promesas de nueva salida que tampoco se cumplen, agravando la crisis de confianza.

**Señales positivas residuales:**
- **"time"** — arista verde gruesa: cuando los procesos funcionan, el pasajero valora 
  explícitamente la eficiencia temporal.
- **"ontime"** y **"schedule"** — en verde pero con aristas finas: la puntualidad satisfactoria 
  se menciona con menor frecuencia que su ausencia.

**Conclusión:** Cada retraso no gestionado activamente destruye más valor reputacional 
del que crea un vuelo puntual.
""",
    },
    'tab-precio': {
        'img': 'Precio.png',
        'title': '💰 Pilar II: Economía y Transparencia de Costes',
        'kpi_color': COLORES['warn'],
        'badge': 'RIESGO MODERADO-ALTO',
        'badge_color': COLORES['warn'],
        'analisis': """
### Diagnóstico de la Red

La red de Precio revela una **paradoja estructural** del modelo *low-cost*: el pasajero reconoce 
el valor del precio base, pero experimenta una fricción económica intensa en los servicios adicionales.

**Señales negativas dominantes:**
- **"pay"** — arista roja más gruesa de la red: el acto de pagar genera el mayor rechazo, 
  apuntando a cobros inesperados de último momento.
- **"extra"** y **"fees"** — el pasajero percibe una estrategia de precio señuelo con costes ocultos.
- **"charged"**, **"charge"**, **"refund"** y **"expensive"** — campo semántico de 
  **disputas económicas post-compra** y dificultades para obtener reembolsos.

**Señales positivas:**
- **"value"** — en verde: cuando el pasajero evalúa la relación calidad-precio globalmente, 
  una parte significativa la encuentra positiva.
- **"price"** y **"priority"** — en verde tenue: el precio base y la tarifa prioritaria 
  se perciben como razonables.

**Señales neutras:** **"fare"**, **"cheap"** y **"paying"** en amarillo: términos descriptivos 
sin carga emocional específica.

**Conclusión:** El cliente llega atraído por el precio anunciado, pero la experiencia real del 
pago acumula fricciones que dañan la percepción global — fenómeno de *price decoupling*.
""",
    },
    'tab-equipaje': {
        'img': 'Equipaje.png',
        'title': '🧳 Pilar III: Logística de Equipajes y Embarque',
        'kpi_color': COLORES['negative'],
        'badge': 'ALERTA ALTA',
        'badge_color': COLORES['negative'],
        'analisis': """
### Diagnóstico de la Red

La red de Equipaje es la **segunda más negativa** del modelo. El hallazgo más relevante es la 
disociación entre el proceso de embarque (positivo) y todo lo relativo al equipaje (negativo).

**Señales negativas dominantes:**
- **"carry"** — arista roja más intensa: señala directamente la política que obliga a pagar 
  por maletas de mano o confiscarlas en puerta de embarque.
- **"checkin"** y **"checking"** — el proceso de facturación, online y en mostrador, 
  genera alta conflictividad.
- **"gate"**, **"desk"**, **"overhead"** — la experiencia física en el aeropuerto relacionada 
  con el equipaje es mayoritariamente negativa.
- **"bag"**, **"bags"**, **"suitcase"**, **"checked"** — prácticamente todo el vocabulario 
  de maletas facturadas aparece con aristas rojas, sin término positivo en este sub-grupo.

**Señales positivas:**
- **"boarding"** — arista verde más gruesa: el proceso de embarque, una vez el equipaje está 
  resuelto, se valora muy positivamente.
- **"luggage"** — también en verde, en contextos sin incidencias.

**Conclusión:** El problema no es la pérdida de maletas sino las **políticas y tasas**. 
Simplificar la política de equipaje de cabina tendría el mayor impacto en este pilar.
""",
    },
    'tab-personal': {
        'img': 'Personal.png',
        'title': '👥 Pilar IV: Factor Humano y Atención al Cliente',
        'kpi_color': COLORES['positive'],
        'badge': 'FORTALEZA DIFERENCIAL',
        'badge_color': COLORES['positive'],
        'analisis': """
### Diagnóstico de la Red

La red de Personal es la **más positiva** de todo el modelo. El propio hub tiene un color más 
claro que el resto, reflejando que el sentimiento medio global de este pilar es el más favorable.

**Señales positivas dominantes:**
- **"crew"** — arista verde más gruesa del grafo: el tripulante de cabina como figura individual 
  recibe más valoraciones positivas que cualquier otro elemento del viaje.
- **"friendly"** y **"helpful"** — las cualidades relacionales más reconocidas.
- **"polite"**, **"attendant"** y **"professional"** — perfil de equipo percibido como cortés 
  y competente en el trato directo.

**Señales negativas:**
- **"service"** — arista roja gruesa, aparente contradicción: "service" se usa en contextos 
  de **fallo del sistema** (reclamaciones, incidencias) mientras "crew" se reserva para 
  la interacción humana en cabina. Son dominios distintos en la mente del pasajero.
- **"rude"** — en rojo pero arista fina: episodios minoritarios estadísticamente.
- **"ignored"** — tenue, en situaciones puntuales de crisis operativa.

**Señal neutra clave:**
- **"staff"** en amarillo: cuando el pasajero menciona al personal en abstracto no carga 
  emocionalmente el término, pero "crew" sí. La experiencia positiva es personal, no institucional.

**Conclusión:** El capital humano es el **mayor activo reputacional** de Ryanair y actúa 
como amortiguador de insatisfacciones generadas por otros pilares.
""",
    },
    'tab-asientos': {
        'img': 'Asientos.png',
        'title': '💺 Pilar V: Confort de Cabina y Ergonomía',
        'kpi_color': '#2E86C1',
        'badge': 'FORTALEZA EN CONSOLIDACIÓN',
        'badge_color': '#2E86C1',
        'analisis': """
### Diagnóstico de la Red

La red de Asientos es la **segunda más positiva** del modelo, con claro dominio de aristas verdes. 
La renovación de flota está produciendo un cambio real en la percepción del cliente.

**Señales positivas dominantes:**
- **"seats"** — arista verde más gruesa: satisfacción al evaluar la cabina en conjunto.
- **"legroom"** y **"space"** — en verde: el espacio para las piernas, históricamente la queja 
  más recurrente en *low-cost*, genera valoraciones positivas, evidenciando mejoras reales.
- **"aisle"**, **"row"** y **"comfortable"** — la posición del asiento se menciona positivamente 
  cuando el pasajero pudo reservar su preferencia.

**Señales negativas:**
- **"uncomfortable"** y **"recline"** — la imposibilidad de reclinar sigue siendo un dolor 
  en trayectos largos.
- **"website"** — arista roja en el grafo de asientos: las quejas sobre la web de selección 
  de asientos (proceso confuso, cobros inesperados) **contaminan retroactivamente** la 
  valoración del producto físico. Hallazgo transversal clave.

**Señales neutras:** **"sit"** y **"cabin"** en amarillo, puramente descriptivos.

**Conclusión:** El principal vector de mejora ya no es el confort físico sino la 
**experiencia digital de reserva**, un problema de UX que contamina la percepción del producto.
""",
    },
    'tab-experiencia': {
        'img': 'Experiencia.png',
        'title': '⭐ Pilar VI: Valoración Holística de la Experiencia',
        'kpi_color': '#8E44AD',
        'badge': 'POLARIZACIÓN EXTREMA',
        'badge_color': '#8E44AD',
        'analisis': """
### Diagnóstico de la Red

La red de Experiencia es el **nodo síntesis** del modelo: aquí el pasajero evalúa la totalidad 
del viaje. Exhibe la **polarización más extrema** de todos los pilares — no existe experiencia 
media; o el viaje funciona y el pasajero lo defiende activamente, o falla y la crítica es contundente.

**Señales positivas clave:**
- **"return"** — arista verde más gruesa de toda la red, y el hallazgo más estratégicamente 
  valioso del modelo completo. Representa la **intención de volver**: el pasajero satisfecho 
  no solo valora, regresa y fideliza.
- **"review"** y **"good"** — en verde: cuando la experiencia es positiva, el pasajero deja 
  reseñas proactivamente y usa "good" como resumen evaluativo.
- **"recommend"** — en verde: una parte relevante del corpus recomienda explícitamente la aerolínea.

**Señales negativas significativas:**
- **"worst"** — arista roja gruesa: los insatisfechos usan superlativos negativos, los fallos 
  acumulados (puntualidad + equipaje) generan reacción emocionalmente intensa.
- **"experience"** — en rojo: el sustantivo aparece más en contextos negativos 
  (*"my experience was terrible"*), siendo un indicador agregado de fracaso.
- **"excellent"** — en rojo: resultado contraintuitivo explicable por **ironía o sarcasmo** 
  (*"excellent job ruining my trip"*), fenómeno documentado que VADER detecta parcialmente.

**Señales neutras:** **"customer"** y **"customers"** en amarillo, reservando la carga 
emocional para los atributos del servicio.

**Conclusión:** Ryanair opera con un **modelo de satisfacción bimodal**. Reducir los fallos 
críticos no solo elimina detractores — convierte pasajeros neutrales en promotores activos.
""",
    },
}

# 6. DATOS MATRIZ FORTALEZAS / DEBILIDADES
# =================================================================
FORTALEZAS = [
    {
        'pilar': '👥 Personal / Tripulación',
        'activos': 'crew, friendly, helpful, polite, professional',
        'mecanismo': 'Mayor arista verde del modelo. Fideliza por interacción humana directa.',
        'accion': 'Ampliar formación en gestión de crisis para mantener la fortaleza bajo presión operativa.',
    },
    {
        'pilar': '💺 Asientos / Confort',
        'activos': 'legroom, space, comfortable — superando expectativas low-cost',
        'mecanismo': 'Renovación de flota rompe el estigma histórico de incomodidad.',
        'accion': 'Comunicar activamente la mejora de flota. Resolver UX web de selección de asiento.',
    },
    {
        'pilar': '⭐ Intención de retorno',
        'activos': '"return" — arista verde más gruesa del modelo completo',
        'mecanismo': 'Pasajeros satisfechos muestran lealtad real y repiten vuelo.',
        'accion': 'Programa de fidelización basado en precio preferente para clientes recurrentes.',
    },
    {
        'pilar': '🧳 Proceso de embarque',
        'activos': '"boarding" — arista verde gruesa en red de Equipaje',
        'mecanismo': 'La eficiencia de embarque es ventaja operativa diferencial clara.',
        'accion': 'Mantener y comunicar tiempos de embarque como KPI de marca en marketing.',
    },
]

DEBILIDADES = [
    {
        'pilar': '⏱ Puntualidad',
        'problema': 'hours, delayed, cancelled, late, stuck, waiting',
        'mecanismo': 'Red casi 100% roja. Retraso + ausencia de comunicación = frustración exponencial.',
        'accion': 'Sistema proactivo de notificación en tiempo real. Protocolo de compensación visible en app.',
        'impacto': 'CRÍTICO',
    },
    {
        'pilar': '🧳 Política de equipaje de cabina',
        'problema': 'carry (arista roja más gruesa), checkin, overhead, gate',
        'mecanismo': 'Política percibida como trampa económica. Confiscación en puerta = crisis de confianza.',
        'accion': 'Simplificar política. Comunicar claramente dimensiones permitidas antes del vuelo.',
        'impacto': 'CRÍTICO',
    },
    {
        'pilar': '💰 Cargos adicionales y reembolsos',
        'problema': 'pay (rojo grueso), extra, fees, refund, charged',
        'mecanismo': 'El acto de pagar genera más rechazo que el precio base. Reembolsos percibidos como imposibles.',
        'accion': 'Mostrar coste total desde el inicio del proceso de compra. Agilizar proceso de refunds.',
        'impacto': 'ALTO',
    },
    {
        'pilar': '💻 Experiencia digital (web / app)',
        'problema': '"website" aparece con arista roja en red de Asientos',
        'mecanismo': 'El proceso de reserva online contamina la valoración del producto físico.',
        'accion': 'Auditoría UX del flujo de selección de asientos y gestión de equipaje en web y app.',
        'impacto': 'ALTO',
    },
    {
        'pilar': '📞 Servicio al cliente en incidencias',
        'problema': '"service" — arista roja gruesa en red de Personal',
        'mecanismo': 'El equipo humano en vuelo es excelente, pero el sistema de reclamaciones falla.',
        'accion': 'Separar canales de atención en vuelo (✅) de gestión de disputas (❌). Mejorar este último.',
        'impacto': 'MODERADO',
    },
]


# 7. FIGURAS
# =================================================================
def build_sentiment_bar():
    if sent_pos_neg.empty:
        return go.Figure()

    tema_orden = ['Puntualidad/Retrasos', 'Precio/Valor', 'Equipaje/Embarque',
                  'Personal/Tripulacion', 'Asientos/Confort', 'General/Otros']
    etiquetas = {
        'Puntualidad/Retrasos': '⏱ Puntualidad',
        'Precio/Valor':         '💰 Precio',
        'Equipaje/Embarque':    '🧳 Equipaje',
        'Personal/Tripulacion': '👥 Personal',
        'Asientos/Confort':     '💺 Asientos',
        'General/Otros':        '⭐ Experiencia',
    }

    df_plot = sent_pos_neg.copy()
    df_plot['Tema'] = pd.Categorical(df_plot['Tema'], categories=tema_orden, ordered=True)
    df_plot = df_plot.sort_values('Tema')
    df_plot['Label'] = df_plot['Tema'].map(etiquetas)

    for col in ['negative', 'neutral', 'positive']:
        if col not in df_plot.columns:
            df_plot[col] = 0

    total = df_plot[['negative', 'neutral', 'positive']].sum(axis=1).replace(0, 1)
    df_plot['pct_pos'] = (df_plot['positive'] / total * 100).round(1)
    df_plot['pct_neu'] = (df_plot['neutral']  / total * 100).round(1)
    df_plot['pct_neg'] = (df_plot['negative'] / total * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Positivo', x=df_plot['Label'], y=df_plot['pct_pos'],
        marker_color=COLORES['positive'],
        text=df_plot['pct_pos'].astype(str) + '%',
        textposition='inside', textfont=dict(color='white', size=12),
    ))
    fig.add_trace(go.Bar(
        name='Neutro', x=df_plot['Label'], y=df_plot['pct_neu'],
        marker_color=COLORES['neutral'],
    ))
    fig.add_trace(go.Bar(
        name='Negativo', x=df_plot['Label'], y=df_plot['pct_neg'],
        marker_color=COLORES['negative'],
        text=df_plot['pct_neg'].astype(str) + '%',
        textposition='inside', textfont=dict(color='white', size=12),
    ))
    fig.update_layout(
        barmode='stack', height=380,
        margin=dict(t=20, b=20, l=10, r=10),
        paper_bgcolor='white', plot_bgcolor='white',
        legend=dict(orientation='h', y=-0.18, x=0.5, xanchor='center'),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(title='% de reseñas', ticksuffix='%'),
    )
    return fig


def build_radar():
    if sent_por_tema.empty:
        return go.Figure()

    tema_orden = ['Puntualidad/Retrasos', 'Precio/Valor', 'Equipaje/Embarque',
                  'Personal/Tripulacion', 'Asientos/Confort', 'General/Otros']
    etiquetas  = ['⏱ Puntualidad', '💰 Precio', '🧳 Equipaje',
                  '👥 Personal', '💺 Asientos', '⭐ Experiencia']

    df_r = sent_por_tema[sent_por_tema['Tema'].isin(tema_orden)].copy()
    df_r['Tema'] = pd.Categorical(df_r['Tema'], categories=tema_orden, ordered=True)
    df_r = df_r.sort_values('Tema')
    valores_norm = [(v + 1) / 2 * 10 for v in df_r['Sentimiento_Medio'].tolist()]

    fig = go.Figure(go.Scatterpolar(
        r=valores_norm + [valores_norm[0]],
        theta=etiquetas + [etiquetas[0]],
        fill='toself',
        fillcolor='rgba(7,53,144,0.12)',
        line=dict(color=COLORES['accent'], width=2),
        marker=dict(size=7, color=COLORES['accent']),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 10], tickvals=[2, 4, 6, 8],
                            tickfont=dict(size=10), gridcolor='#DDE3EC'),
            angularaxis=dict(tickfont=dict(size=13)),
        ),
        height=360, margin=dict(t=20, b=20, l=40, r=40),
        paper_bgcolor='white', showlegend=False,
    )
    return fig


# 8. APP LAYOUT
# =================================================================
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Ryanair Intelligence Dashboard"

app.layout = html.Div(style={
    'backgroundColor': COLORES['bg'],
    'fontFamily': '"IBM Plex Sans", "Segoe UI", Helvetica, sans-serif',
    'minHeight': '100vh',
}, children=[

    # ── HEADER ────────────────────────────────────────────────────
    html.Header(style={
        'background': f'linear-gradient(135deg, {COLORES["accent"]} 0%, {COLORES["accent2"]} 100%)',
        'padding': '56px 64px 48px', 'color': 'white',
        'position': 'relative', 'overflow': 'hidden',
    }, children=[
        html.Div(style={
            'position': 'absolute', 'top': '-40px', 'right': '-40px',
            'width': '300px', 'height': '300px', 'borderRadius': '50%',
            'background': 'rgba(255,255,255,0.04)', 'pointerEvents': 'none',
        }),
        html.Span("RYANAIR", style={
            'fontSize': '0.75em', 'letterSpacing': '0.35em', 'opacity': '0.7',
            'display': 'block', 'marginBottom': '8px', 'textTransform': 'uppercase', 'fontWeight': '500',
        }),
        html.H1("Customer Intelligence Dashboard", style={
            'margin': '0', 'fontSize': '2.6em', 'fontWeight': '700',
            'lineHeight': '1.15', 'maxWidth': '700px',
        }),
        html.P("Análisis de Redes Semánticas y Sentimiento · 2.249 reseñas verificadas · Pipeline NLP + VADER",
               style={'marginTop': '16px', 'opacity': '0.75', 'fontSize': '1.05em', 'maxWidth': '640px'}),
    ]),

    html.Div(style={'padding': '48px 64px'}, children=[

        # ── KPIs ──────────────────────────────────────────────────
        html.Div(style={'display': 'flex', 'gap': '24px', 'marginBottom': '40px'}, children=[
            html.Div(style=ESTILO_KPI, children=[
                html.Div(f"{total_resenas:,}", style={'color': COLORES['accent'], 'fontSize': '2.8em', 'fontWeight': '800', 'lineHeight': '1'}),
                html.P("RESEÑAS ANALIZADAS", style={'fontWeight': '600', 'color': COLORES['muted'], 'fontSize': '0.78em', 'letterSpacing': '0.1em', 'margin': '10px 0 0'}),
            ]),
            html.Div(style={**ESTILO_KPI, 'borderTopColor': '#F39C12'}, children=[
                html.Div(f"{rating_medio:.1f} / 10", style={'color': '#F39C12', 'fontSize': '2.8em', 'fontWeight': '800', 'lineHeight': '1'}),
                html.P("SATISFACCIÓN MEDIA", style={'fontWeight': '600', 'color': COLORES['muted'], 'fontSize': '0.78em', 'letterSpacing': '0.1em', 'margin': '10px 0 0'}),
            ]),
            html.Div(style={**ESTILO_KPI, 'borderTopColor': COLORES['negative']}, children=[
                html.Div(f"{tasa_detraccion:.1f}%", style={'color': COLORES['negative'], 'fontSize': '2.8em', 'fontWeight': '800', 'lineHeight': '1'}),
                html.P("ÍNDICE DE DETRACCIÓN", style={'fontWeight': '600', 'color': COLORES['muted'], 'fontSize': '0.78em', 'letterSpacing': '0.1em', 'margin': '10px 0 0'}),
            ]),
            html.Div(style={**ESTILO_KPI, 'borderTopColor': COLORES['positive']}, children=[
                html.Div(f"{tasa_promocion:.1f}%", style={'color': COLORES['positive'], 'fontSize': '2.8em', 'fontWeight': '800', 'lineHeight': '1'}),
                html.P("ÍNDICE DE PROMOCIÓN", style={'fontWeight': '600', 'color': COLORES['muted'], 'fontSize': '0.78em', 'letterSpacing': '0.1em', 'margin': '10px 0 0'}),
            ]),
        ]),

        # ── MAPA ESTRATÉGICO ──────────────────────────────────────
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Mapa Estratégico: Fortalezas y Debilidades", style={
                'color': COLORES['accent'], 'fontSize': '1.4em',
                'borderBottom': f'2px solid {COLORES["accent"]}',
                'paddingBottom': '12px', 'marginBottom': '24px',
            }),
            html.P("Síntesis ejecutiva derivada del análisis de redes semánticas. "
                   "Cada hallazgo está sustentado en las aristas y nodos observados en los grafos de Gephi.",
                   style={'color': COLORES['muted'], 'marginBottom': '28px', 'fontSize': '0.97em'}),

            html.Div(style={'display': 'flex', 'gap': '32px'}, children=[

                # FORTALEZAS
                html.Div(style={'flex': '1'}, children=[
                    html.Div(style={
                        'backgroundColor': '#EAFAF1',
                        'borderLeft': f'4px solid {COLORES["positive"]}',
                        'padding': '14px 18px', 'borderRadius': '8px', 'marginBottom': '20px',
                    }, children=[
                        html.H3("✅ FORTALEZAS IDENTIFICADAS", style={
                            'color': COLORES['positive'], 'margin': '0',
                            'fontSize': '0.95em', 'letterSpacing': '0.08em',
                        }),
                        html.P("Activos competitivos validados estadísticamente por el modelo NLP.",
                               style={'color': '#555', 'margin': '4px 0 0', 'fontSize': '0.85em'}),
                    ]),
                    *[html.Div(style={
                        'backgroundColor': 'white', 'border': '1px solid #D5F5E3',
                        'borderRadius': '10px', 'padding': '18px 20px', 'marginBottom': '14px',
                    }, children=[
                        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '8px'}, children=[
                            html.Strong(f['pilar'], style={'color': COLORES['text'], 'fontSize': '1em'}),
                            html.Span('FORTALEZA', style={
                                'backgroundColor': COLORES['positive'], 'color': 'white',
                                'fontSize': '0.68em', 'fontWeight': '700', 'letterSpacing': '0.08em',
                                'padding': '3px 10px', 'borderRadius': '20px',
                            }),
                        ]),
                        html.P(f'Señal en grafo: {f["activos"]}',
                               style={'color': COLORES['muted'], 'fontSize': '0.85em', 'margin': '0 0 6px', 'fontStyle': 'italic'}),
                        html.P(f['mecanismo'],
                               style={'color': '#444', 'fontSize': '0.9em', 'margin': '0 0 8px', 'lineHeight': '1.5'}),
                        html.Div(style={'backgroundColor': '#F0FAF4', 'borderRadius': '6px', 'padding': '8px 12px'}, children=[
                            html.P(f'→ {f["accion"]}',
                                   style={'color': COLORES['positive'], 'fontSize': '0.88em', 'margin': '0', 'fontWeight': '600'}),
                        ]),
                    ]) for f in FORTALEZAS],
                ]),

                # DEBILIDADES
                html.Div(style={'flex': '1'}, children=[
                    html.Div(style={
                        'backgroundColor': '#FDEDEC',
                        'borderLeft': f'4px solid {COLORES["negative"]}',
                        'padding': '14px 18px', 'borderRadius': '8px', 'marginBottom': '20px',
                    }, children=[
                        html.H3("⚠️ DEBILIDADES A MEJORAR", style={
                            'color': COLORES['negative'], 'margin': '0',
                            'fontSize': '0.95em', 'letterSpacing': '0.08em',
                        }),
                        html.P("Puntos de dolor detectados con mayor frecuencia e intensidad negativa.",
                               style={'color': '#555', 'margin': '4px 0 0', 'fontSize': '0.85em'}),
                    ]),
                    *[html.Div(style={
                        'backgroundColor': 'white',
                        'border': f'1px solid {"#FADBD8" if d["impacto"]=="CRÍTICO" else "#FAE5D3" if d["impacto"]=="ALTO" else "#F9F3DC"}',
                        'borderRadius': '10px', 'padding': '18px 20px', 'marginBottom': '14px',
                    }, children=[
                        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '8px'}, children=[
                            html.Strong(d['pilar'], style={'color': COLORES['text'], 'fontSize': '1em'}),
                            html.Span(d['impacto'], style={
                                'backgroundColor': COLORES['negative'] if d['impacto'] == 'CRÍTICO' else COLORES['warn'] if d['impacto'] == 'ALTO' else '#F1C40F',
                                'color': 'white',
                                'fontSize': '0.68em', 'fontWeight': '700', 'letterSpacing': '0.08em',
                                'padding': '3px 10px', 'borderRadius': '20px',
                            }),
                        ]),
                        html.P(f'Señal en grafo: {d["problema"]}',
                               style={'color': COLORES['muted'], 'fontSize': '0.85em', 'margin': '0 0 6px', 'fontStyle': 'italic'}),
                        html.P(d['mecanismo'],
                               style={'color': '#444', 'fontSize': '0.9em', 'margin': '0 0 8px', 'lineHeight': '1.5'}),
                        html.Div(style={
                            'backgroundColor': '#FEF0F0' if d['impacto'] == 'CRÍTICO' else '#FEF9F0',
                            'borderRadius': '6px', 'padding': '8px 12px',
                        }, children=[
                            html.P(f'→ {d["accion"]}', style={
                                'color': COLORES['negative'] if d['impacto'] == 'CRÍTICO' else COLORES['warn'],
                                'fontSize': '0.88em', 'margin': '0', 'fontWeight': '600',
                            }),
                        ]),
                    ]) for d in DEBILIDADES],
                ]),
            ]),
        ]),

        # ── VISUALIZACIONES CUANTITATIVAS ─────────────────────────
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Análisis Cuantitativo por Pilar", style={
                'color': COLORES['accent'], 'fontSize': '1.4em',
                'borderBottom': f'2px solid {COLORES["accent"]}',
                'paddingBottom': '12px', 'marginBottom': '24px',
            }),
            html.Div(style={'display': 'flex', 'gap': '40px', 'alignItems': 'flex-start'}, children=[
                html.Div(style={'flex': '1.4'}, children=[
                    html.H4("Distribución de sentimiento por pilar",
                            style={'color': COLORES['muted'], 'fontWeight': '600', 'marginBottom': '8px'}),
                    html.P("% de reseñas positivas, neutras y negativas dentro de cada categoría semántica.",
                           style={'color': COLORES['muted'], 'fontSize': '0.88em', 'marginBottom': '12px'}),
                    dcc.Graph(figure=build_sentiment_bar(), config={'displayModeBar': False}),
                ]),
                html.Div(style={'flex': '1', 'minWidth': '280px'}, children=[
                    html.H4("Radar de salud global por pilar",
                            style={'color': COLORES['muted'], 'fontWeight': '600', 'marginBottom': '8px'}),
                    html.P("Sentimiento medio normalizado (0–10). Valores > 5 indican balance positivo.",
                           style={'color': COLORES['muted'], 'fontSize': '0.88em', 'marginBottom': '12px'}),
                    dcc.Graph(figure=build_radar(), config={'displayModeBar': False}),
                ]),
            ]),
        ]),

        # ── ANÁLISIS DETALLADO POR PILARES ────────────────────────
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Diagnóstico Detallado por Pilar Semántico", style={
                'color': COLORES['accent'], 'fontSize': '1.4em',
                'borderBottom': f'2px solid {COLORES["accent"]}',
                'paddingBottom': '12px', 'marginBottom': '8px',
            }),
            html.P("Seleccione un pilar para acceder al análisis completo de su red semántica generada con Gephi.",
                   style={'color': COLORES['muted'], 'marginBottom': '28px', 'fontSize': '0.97em'}),
            dcc.Tabs(id="tabs-pilares", value='tab-puntualidad', children=[
                dcc.Tab(label='⏱ PUNTUALIDAD', value='tab-puntualidad',
                        style={'fontWeight': '600', 'padding': '12px 16px'},
                        selected_style={'backgroundColor': COLORES['accent'], 'color': 'white', 'fontWeight': '700', 'padding': '12px 16px', 'borderRadius': '6px 6px 0 0'}),
                dcc.Tab(label='💰 PRECIO', value='tab-precio',
                        style={'fontWeight': '600', 'padding': '12px 16px'},
                        selected_style={'backgroundColor': COLORES['accent'], 'color': 'white', 'fontWeight': '700', 'padding': '12px 16px', 'borderRadius': '6px 6px 0 0'}),
                dcc.Tab(label='🧳 EQUIPAJE', value='tab-equipaje',
                        style={'fontWeight': '600', 'padding': '12px 16px'},
                        selected_style={'backgroundColor': COLORES['accent'], 'color': 'white', 'fontWeight': '700', 'padding': '12px 16px', 'borderRadius': '6px 6px 0 0'}),
                dcc.Tab(label='👥 PERSONAL', value='tab-personal',
                        style={'fontWeight': '600', 'padding': '12px 16px'},
                        selected_style={'backgroundColor': COLORES['accent'], 'color': 'white', 'fontWeight': '700', 'padding': '12px 16px', 'borderRadius': '6px 6px 0 0'}),
                dcc.Tab(label='💺 ASIENTOS', value='tab-asientos',
                        style={'fontWeight': '600', 'padding': '12px 16px'},
                        selected_style={'backgroundColor': COLORES['accent'], 'color': 'white', 'fontWeight': '700', 'padding': '12px 16px', 'borderRadius': '6px 6px 0 0'}),
                dcc.Tab(label='⭐ EXPERIENCIA', value='tab-experiencia',
                        style={'fontWeight': '600', 'padding': '12px 16px'},
                        selected_style={'backgroundColor': COLORES['accent'], 'color': 'white', 'fontWeight': '700', 'padding': '12px 16px', 'borderRadius': '6px 6px 0 0'}),
            ]),
            html.Div(id='tabs-content-pilares', style={'paddingTop': '36px'}),
        ]),

        # ── TOPOLOGÍA GLOBAL ──────────────────────────────────────
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Topología Global de la Red Semántica", style={
                'color': COLORES['accent'], 'fontSize': '1.4em',
                'borderBottom': f'2px solid {COLORES["accent"]}',
                'paddingBottom': '12px', 'marginBottom': '20px',
            }),
            html.Div(style={'display': 'flex', 'gap': '48px', 'alignItems': 'flex-start'}, children=[
                html.Div(style={'flex': '1'}, children=[
                    dcc.Markdown("""
### Lectura de la arquitectura global

La vista topológica global revela que los **seis pilares semánticos se comportan como 
comunidades relativamente independientes**, con alta densidad de conexiones intra-clúster 
y baja conectividad entre clústeres.

Esta estructura **Hub-and-Spoke desconectada** tiene implicaciones directas:

- **La experiencia de vuelo no es un continuo para el pasajero**: evalúa cada pilar 
  como un dominio separado. Un vuelo puntual no «compensa» un problema con el equipaje.
- **Los fallos no se propagan semánticamente**: las quejas sobre precios rara vez 
  contaminan el lenguaje sobre el personal. Esto permite **intervenciones quirúrgicas** 
  por pilar con impacto localizado.
- **El clúster de mayor densidad visual** corresponde a Precio y Puntualidad, 
  confirmando que concentran el mayor volumen de menciones en el dataset.

La fragmentación es en sí misma un dato: en aerolíneas con mejor valoración global, 
los grafos tienden a mostrar mayor interconexión entre pilares, reflejando narrativas 
de experiencia más cohesionadas y positivas.
                    """, style={'lineHeight': '1.8', 'fontSize': '0.97em'}),
                ]),
                html.Div(style={'flex': '1'}, children=[
                    html.Img(src='/assets/Nodos.png', style={
                        'width': '100%', 'borderRadius': '12px',
                        'border': '1px solid #DDE3EC',
                        'boxShadow': '0 4px 16px rgba(0,0,0,0.06)',
                    }),
                ]),
            ]),
        ]),

        # ── METODOLOGÍA ───────────────────────────────────────────
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Contexto Metodológico", style={
                'color': COLORES['accent'], 'fontSize': '1.4em',
                'borderBottom': f'2px solid {COLORES["accent"]}',
                'paddingBottom': '12px', 'marginBottom': '20px',
            }),
            dcc.Markdown(INTRO_METODOLOGIA, style={'lineHeight': '1.85', 'fontSize': '1.0em', 'color': COLORES['text']}),
            html.Hr(style={'border': 'none', 'borderTop': '1px solid #DDE3EC', 'margin': '24px 0'}),
            dcc.Markdown(LEYENDA_GRAFOS, style={'lineHeight': '1.7', 'fontSize': '0.97em'}),
        ]),

        # ── AUDITORÍA ─────────────────────────────────────────────
        html.Div(style=ESTILO_CARD, children=[
            html.H2("Auditoría de Reseñas Clasificadas", style={
                'color': COLORES['accent'], 'fontSize': '1.4em',
                'borderBottom': f'2px solid {COLORES["accent"]}',
                'paddingBottom': '12px', 'marginBottom': '20px',
            }),
            html.P("Muestra de los primeros 100 registros del corpus procesado con etiqueta de sentimiento y tema asignado.",
                   style={'color': COLORES['muted'], 'marginBottom': '20px', 'fontSize': '0.95em'}),
            dash_table.DataTable(
                data=df.head(100).to_dict('records'),
                columns=[
                    {"name": "Tema",               "id": "Tema"},
                    {"name": "Sentimiento",         "id": "Sentiment_Label"},
                    {"name": "Score",               "id": "Sentiment_Score"},
                    {"name": "Comentario procesado","id": "Text_Clean"},
                ],
                page_size=10,
                style_cell={
                    'textAlign': 'left', 'padding': '14px 16px', 'fontSize': '13px',
                    'fontFamily': 'IBM Plex Mono, monospace',
                    'borderBottom': '1px solid #EDF0F5', 'whiteSpace': 'normal',
                    'maxWidth': '480px', 'overflow': 'hidden', 'textOverflow': 'ellipsis',
                },
                style_header={
                    'backgroundColor': COLORES['accent'], 'color': 'white',
                    'fontWeight': '700', 'fontSize': '12px', 'letterSpacing': '0.05em',
                    'border': 'none', 'padding': '14px 16px',
                },
                style_data_conditional=[
                    {'if': {'filter_query': '{Sentiment_Label} = "positive"'}, 'color': COLORES['positive'], 'fontWeight': '600'},
                    {'if': {'filter_query': '{Sentiment_Label} = "negative"'}, 'color': COLORES['negative'], 'fontWeight': '600'},
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#F8FAFC'},
                ],
                style_table={'overflowX': 'auto', 'borderRadius': '8px', 'overflow': 'hidden'},
            ),
        ]),
    ]),

    # ── FOOTER ────────────────────────────────────────────────────
    html.Footer(style={
        'textAlign': 'center', 'padding': '40px 64px',
        'borderTop': '1px solid #DDE3EC', 'color': COLORES['muted'], 'fontSize': '0.88em',
    }, children=[
        html.P("© 2026 · Análisis de Opinión Pública y Modelos Predictivos III · "
               "Pipeline: Python → NLTK/VADER → NetworkX → Gephi → Dash"),
    ]),
])


# 9. CALLBACK
# =================================================================
@app.callback(Output('tabs-content-pilares', 'children'), Input('tabs-pilares', 'value'))
def render_pilar(tab):
    data = PILARES[tab]
    return html.Div(style={'display': 'flex', 'gap': '48px', 'alignItems': 'flex-start'}, children=[
        html.Div(style={'flex': '1.1', 'minWidth': '0'}, children=[
            html.Span(data['badge'], style={
                'display': 'inline-block', 'backgroundColor': data['badge_color'],
                'color': 'white', 'fontSize': '0.72em', 'fontWeight': '700',
                'letterSpacing': '0.1em', 'padding': '4px 12px', 'borderRadius': '4px',
                'marginBottom': '16px', 'textTransform': 'uppercase',
            }),
            html.H3(data['title'], style={
                'color': data['kpi_color'], 'fontSize': '1.25em',
                'margin': '0 0 20px', 'fontWeight': '700',
            }),
            dcc.Markdown(data['analisis'], style={
                'lineHeight': '1.85', 'fontSize': '0.97em', 'color': COLORES['text'],
            }),
        ]),
        html.Div(style={'flex': '0.9', 'minWidth': '0'}, children=[
            html.Img(src=f'/assets/{data["img"]}', style={
                'width': '100%', 'borderRadius': '12px',
                'border': '1px solid #DDE3EC',
                'boxShadow': '0 8px 24px rgba(7,53,144,0.08)', 'display': 'block',
            }),
            html.P(f'Red semántica · {data["title"].split(":")[-1].strip()}',
                   style={'textAlign': 'center', 'marginTop': '10px',
                          'fontSize': '0.8em', 'color': COLORES['muted'], 'fontStyle': 'italic'}),
        ]),
    ])


# 10. EJECUCIÓN
# =================================================================
if __name__ == '__main__':
    app.run(debug=True, port=8055)