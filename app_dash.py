import dash
from dash import dcc, html
from dash import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from dash.dependencies import Input, Output
from statsmodels.tsa.stattools import adfuller, acf, pacf  # Importar acf y pacf desde tsa.stattools

# Inicializamos la app Dash
app = dash.Dash(__name__)

# Cargar el DataFrame
dftra = pd.read_csv("/Users/juansebastianquintanacontreras/Desktop/Entrega#2_avance_PF/26-09-2022.txt", sep=",", header=0)

# Limpiar espacios en los nombres de las columnas
dftra.columns = dftra.columns.str.strip()

# Convertir la columna 'fecha' a formato datetime
dftra['fecha'] = pd.to_datetime(dftra['fecha'], errors='coerce')

# Establecer la columna 'fecha' como índice para operaciones temporales
dftra.set_index('fecha', inplace=True)

# Crear la columna 'hora' basada en el índice
dftra['hora'] = dftra.index.hour

# Convertir todas las columnas posibles a numéricas, ignorando errores
for col in dftra.columns:
    dftra[col] = pd.to_numeric(dftra[col], errors='coerce')

# Filtrar solo columnas numéricas para operaciones de agregación como mean()
dftra_numeric = dftra.select_dtypes(include=['number'])

# Resamplear los datos
df5min = dftra_numeric.resample('5min').mean() 
df30min = dftra_numeric.resample('30min').mean()
dfhora = dftra_numeric.resample('1h').mean()  # Cambiado 'H' por 'h'

# Aplicar diferenciación a la serie 'precio_bid'
dftra['precio_bid_diff'] = dftra['precio_bid'].diff()

# Número de lags
nlag_5min = 60
nlag_30min = 23
nlag_hora = 11

# Pruebas ADF
adf_result_5min = adfuller(df5min['precio_bid'].dropna())
adf_result_30min = adfuller(df30min['precio_bid'].dropna())
adf_result_hora = adfuller(dfhora['precio_bid'].dropna())

# Cálculo de autocorrelación y autocorrelación parcial
acf_vals_5min = acf(df5min['precio_bid'].dropna(), nlags=nlag_5min)
pacf_vals_5min = pacf(df5min['precio_bid'].dropna(), nlags=nlag_5min)

acf_vals_30min = acf(df30min['precio_bid'].dropna(), nlags=nlag_30min)
pacf_vals_30min = pacf(df30min['precio_bid'].dropna(), nlags=nlag_30min)

acf_vals_hora = acf(dfhora['precio_bid'].dropna(), nlags=nlag_hora)
pacf_vals_hora = pacf(dfhora['precio_bid'].dropna(), nlags=nlag_hora)

# Descripción del DataFrame
num_filas = dftra_numeric.shape[0]
nombres_columnas = dftra_numeric.columns.tolist()
resumen_dftra = dftra_numeric.describe(include='all')

# Crear la columna 'INTERVALO_HORAS'
dftra['INTERVALO_HORAS'] = (dftra['hora'] // 2) * 2
dftra['INTERVALO_HORAS'] = dftra['INTERVALO_HORAS'].apply(lambda x: f"{x:02d}:00 - {x+2:02d}:00")

# Análisis de los NA's
total_na = dftra_numeric.isna().sum().sum()
na_summary = dftra_numeric.isnull().sum().reset_index()
na_summary.columns = ['Columna', 'Valores NA']

# Frecuencia de transacciones por intervalos de 2 horas
frecuencia_transacciones_intervalos = dftra.groupby('INTERVALO_HORAS').size().reset_index(name='Frecuencia')

# Matriz de correlación
df_numeric = dftra_numeric[['hora', 'precio_bid', 'volumen_bid', 'precio_ask']].dropna()
correlation_matrix = df_numeric.corr()

resample_df = dftra_numeric.resample('H').mean()

# Series diferenciadas resampleadas
df_hora = dftra['precio_bid_diff'].resample('1H').mean()
df_30min = dftra['precio_bid_diff'].resample('30min').mean()
df_5min = dftra['precio_bid_diff'].resample('5min').mean()

# Aplicar diferenciación a la serie 'precio_bid'
dftra['precio_bid_diff'] = dftra['precio_bid'].diff()

# Layout de la aplicación Dash
app.layout = html.Div([
    html.H1("Análisis Exploratorio de Datos (EDA) de la Divisa EUR/USD"),
    
    # Sección de introducción
    html.Div([
        html.H2("Introducción del EDA de la Divisa EUR/USD"),
        html.P("El análisis exploratorio de datos (EDA) es una etapa crucial para comprender los detalles en las series temporales de trading, especialmente en el contexto de divisas. "
               "En este estudio, nos enfocamos en la divisa EUR/USD, que representa el valor del euro en términos de dólares estadounidenses."),
        
        html.H3("Objetivo del EDA"),
        html.Ul([
            html.Li("Variaciones del Precio a lo Largo del Día"),
            html.Li("Análisis de Tendencias y Volatilidad"),
            html.Li("Visualización de Datos"),
            html.Li("Detección de Anomalías")
        ]),
    ]),
    
    # Información del DataFrame
    html.Div([
        html.H3(f"Número de filas: {num_filas}"),
        html.H3(f"Nombres de las columnas: {nombres_columnas}"),
        
        # Resumen del DataFrame
        html.H3("Resumen del DataFrame:"),
        dash_table.DataTable(
            data=resumen_dftra.reset_index().to_dict('records'),
            columns=[{"name": i, "id": i} for i in resumen_dftra.reset_index().columns],
            style_table={'overflowX': 'scroll'},
            style_cell={'textAlign': 'left'}
        )
    ]),
    
    # Gráfico de Frecuencia de Transacciones por Intervalos de 2 Horas
    html.H3("Frecuencia de Transacciones por Intervalos de 2 Horas"),
    dcc.Graph(
        id='frecuencia-intervalos',
        figure=go.Figure([go.Bar(
            x=frecuencia_transacciones_intervalos['INTERVALO_HORAS'],
            y=frecuencia_transacciones_intervalos['Frecuencia'],
            marker_color='lightgreen'
        )]).update_layout(
            title='Frecuencia de Transacciones por Intervalos de 2 Horas',
            xaxis_title='Intervalo de Hora',
            yaxis_title='Frecuencia',
            xaxis_tickangle=90
        )
    ),
    
    # Gráfico de la Distribución de la Hora Exacta en Nanosegundos
    html.H3("Distribución de la Hora Exacta en Nanosegundos"),
    dcc.Graph(
        id='distribucion-hora',
        figure=px.histogram(dftra, x='hora', nbins=50, color_discrete_sequence=['lightgreen'])
        .update_layout(title='Distribución de la Hora Exacta', xaxis_title='Hora', yaxis_title='Frecuencia')
    ),
    
    # Gráfico de la Distribución del Precio Bid
    html.H3("Distribución del Precio Bid"),
    dcc.Graph(
        id='distribucion-precio-bid',
        figure=px.histogram(dftra, x='precio_bid', nbins=50, color_discrete_sequence=['lightblue'])
        .update_layout(title='Distribución del Precio Bid', xaxis_title='Precio Bid', yaxis_title='Frecuencia')
    ),
    
    # Gráfico de la Distribución del Precio Ask
    html.H3("Distribución del Precio Ask"),
    dcc.Graph(
        id='distribucion-precio-ask',
        figure=px.histogram(dftra, x='precio_ask', nbins=50, color_discrete_sequence=['lightcoral'])
        .update_layout(title='Distribución del Precio Ask', xaxis_title='Precio Ask', yaxis_title='Frecuencia')
    ),
    
    # Gráfico de la Distribución del Volumen Bid
    html.H3("Distribución del Volumen Bid"),
    dcc.Graph(
        id='distribucion-volumen-bid',
        figure=px.histogram(dftra, x='volumen_bid', nbins=50, color_discrete_sequence=['blue'])
        .update_layout(title='Distribución del Volumen Bid', xaxis_title='Volumen Bid', yaxis_title='Frecuencia')
    ),

    # Análisis de NA's
    html.H3(f"Total de valores faltantes (NA's) en el DataFrame: {total_na}"),
    html.H3("Resumen de valores faltantes (por columna):"),
    dash_table.DataTable(
        data=na_summary.to_dict('records'),
        columns=[{"name": i, "id": i} for i in na_summary.columns],
        style_table={'overflowX': 'scroll'},
        style_cell={'textAlign': 'left'}
    ),
    
    # Matriz de correlación
    html.H3("Matriz de Correlación"),
    dcc.Graph(
        id='matriz-correlacion',
        figure=ff.create_annotated_heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns.tolist(),
            y=correlation_matrix.columns.tolist(),
            colorscale='Viridis',
            showscale=True
        )
    ),
    
    # Gráfico de la serie temporal del precio_bid
    html.H3("Serie de Tiempo - Precio Bid"),
    dcc.Graph(
        id='serie-precio-bid',
        figure=px.line(dftra_numeric, x=dftra_numeric.index, y='precio_bid', title='Serie de Tiempo - Precio Bid')
    ),
    
    # Resampleo y gráficas
    html.H3("Series de Tiempo Resampleadas"),
    dcc.Graph(
        id='resampleo-precio-bid',
        figure=px.line(resample_df, x=resample_df.index, y='precio_bid', title='Resampleo por Hora - Media Precio Bid')
    ),

    # Gráfico de autocorrelación y PACF - Resampleo 5 minutos
    html.H3("Autocorrelación y PACF - Resampleo 5 Minutos"),
    dcc.Graph(
        id='acf-pacf-5min',
        figure=go.Figure([
            go.Scatter(x=list(range(len(acf_vals_5min))), y=acf_vals_5min, mode='lines', name='ACF'),
            go.Scatter(x=list(range(len(pacf_vals_5min))), y=pacf_vals_5min, mode='lines', name='PACF')
        ]).update_layout(
            title='ACF y PACF - Resampleo a 5 Minutos',
            xaxis_title='Lags',
            yaxis_title='Autocorrelación'
        )
    ),

    
        # Gráfico de autocorrelación y PACF - Resampleo 30 minutos
    html.H3("Autocorrelación y PACF - Resampleo 30 Minutos"),
    dcc.Graph(
        id='acf-pacf-30min',
        figure=go.Figure([
            go.Scatter(x=list(range(len(acf_vals_30min))), y=acf_vals_30min, mode='lines', name='ACF'),
            go.Scatter(x=list(range(len(pacf_vals_30min))), y=pacf_vals_30min, mode='lines', name='PACF')
        ]).update_layout(
            title='ACF y PACF - Resampleo a 30 Minutos',
            xaxis_title='Lags',
            yaxis_title='Autocorrelación'
        )
    ),

    # Gráfico de autocorrelación y PACF - Resampleo 1 hora
    html.H3("Autocorrelación y PACF - Resampleo 1 Hora"),
    dcc.Graph(
        id='acf-pacf-1h',
        figure=go.Figure([
            go.Scatter(x=list(range(len(acf_vals_hora))), y=acf_vals_hora, mode='lines', name='ACF'),
            go.Scatter(x=list(range(len(pacf_vals_hora))), y=pacf_vals_hora, mode='lines', name='PACF')
        ]).update_layout(
            title='ACF y PACF - Resampleo a 1 Hora',
            xaxis_title='Lags',
            yaxis_title='Autocorrelación'
        )
    ),

    
    # Boxplots
    html.H3("Distribución del Precio Bid (Boxplots)"),
    dcc.Graph(
        id='boxplots-precio-bid',
        figure=px.box(dftra_numeric, y='precio_bid', points='all', title='Distribución General del Precio Bid')
    ),

    html.H3("Resultados de la Prueba ADF"),
    html.Pre(f'''
    Resample a 5 Minutos:
    ADF Statistic: {adf_result_5min[0]}
    p-value: {adf_result_5min[1]}

    Resample a 30 Minutos:
    ADF Statistic: {adf_result_30min[0]}
    p-value: {adf_result_30min[1]}

    Resample por Hora:
    ADF Statistic: {adf_result_hora[0]}
    p-value: {adf_result_hora[1]}
    '''),


    html.H3("Serie de Tiempo - Precio Bid (Original)"),
    dcc.Graph(
        id='serie-precio-bid-original',
        figure=px.line(dftra, x=dftra.index, y='precio_bid', title='Serie de Tiempo - Precio Bid Original')
    ),
    
    # Gráfico de la serie diferenciada
    html.H3("Serie de Tiempo - Precio Bid Diferenciado"),
    dcc.Graph(
        id='serie-precio-bid-diff',
        figure=px.line(dftra, x=dftra.index, y='precio_bid_diff', title='Serie de Tiempo - Precio Bid Diferenciado')
    ),


    # Gráfico de series resampleadas diferenciadas
    html.H3("Series de Tiempo Resampleadas - Diferenciada"),
    dcc.Graph(
        id='resampleo-precio-bid-diff',
        figure=px.line(df_hora, x=df_hora.index, y=df_hora.values, title='Resampleo por Hora - Precio Bid Diferenciado')
    ),

])

# Ejecutar la app
if __name__ == '__main__':
    app.run_server(debug=True)