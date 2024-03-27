import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import matplotlib.pyplot as plt

# Directorio donde se encuentran los archivos CSV
directorio = '/home/julian/Documentos/Catedra-SostyCC'

# Cargar los datos del archivo CSV de matriculados
ruta_csv_matriculados = os.path.join('/home/julian/Documentos/Catedra-SostyCC/matriculados/matriculados.csv')
datos_matriculados = pd.read_csv(ruta_csv_matriculados)
# Calcular el porcentaje de matriculados por categoría
porcentaje_matriculados = datos_matriculados['OBSERVACIÓN'].value_counts(normalize=True) * 100
# Obtener la lista de archivos CSV en el directorio
archivos_csv = [archivo for archivo in os.listdir(directorio) if archivo.endswith('.csv')]
####grafica ausentes
# Leer los datos desde el archivo de texto
df_ausentes_por_sesion = pd.read_csv('sesiones_asistencia_ausentes.txt', sep='\t')

# Convertir la columna 'sesion' a tipo string
df_ausentes_por_sesion['sesion'] = df_ausentes_por_sesion['sesion'].astype(str)

# Eliminar el texto 'sesion' de los valores
df_ausentes_por_sesion['sesion'] = df_ausentes_por_sesion['sesion'].str.replace('sesion ', '')

# Convertir la columna 'sesion' a tipo entero
df_ausentes_por_sesion['sesion'] = df_ausentes_por_sesion['sesion'].astype(int)

# Ordenar el DataFrame por la columna 'sesion' para asegurar que los puntos en la gráfica estén en orden
df_ausentes_por_sesion = df_ausentes_por_sesion.sort_values(by='sesion')

#define el color del grafico
custom_template = {
    "layout": {
        "plot_bgcolor": "rgba(0, 0, 0, 0)",  # Fondo transparente del gráfico
        "paper_bgcolor": "rgba(0, 0, 0, 0)"  # Fondo transparente del área exterior del gráfico
    }
}

# Crear la aplicación Dash
app = dash.Dash(__name__)
server = app.server

# Layout de la aplicación
app.layout = html.Div([
    html.H1('Catedra Nacional de Sostenibilidad y cambio climatico'),

    

    # Dropdown para seleccionar la opción
    dcc.Dropdown(
        id='dropdown-opcion',
        options=[
            {'label': 'Matriculados', 'value': 'matriculados'},
            {'label': 'Ausentes', 'value': 'ausentes'},
            {'label': 'Asistencia por sesión', 'value': 'asistencia_por_sesion'}
        ] + [{'label': f"{archivo[:-4]}", 'value': archivo} for archivo in archivos_csv],
        value='matriculados',
        searchable=False,
        className='dropdown-style'
    ),
    

    # Div para contener los gráficos de sesiones
    html.Div(id='graficos-sesiones-container',className='container-style'),
    # Div para contener los gráficos de ausentes
    html.Div(id='graficos-ausentes-container',className='container-style'),

])

# Callback para actualizar los gráficos según la opción seleccionada
@app.callback(
    [Output('graficos-sesiones-container', 'children'),
     Output('graficos-ausentes-container', 'children')],
    [Input('dropdown-opcion', 'value')]
)
def actualizar_graficos_sesiones(opcion_seleccionada):
    if opcion_seleccionada == 'matriculados':
        # Crear el gráfico de pastel para matriculados
        fig_barras_matriculados = px.pie(values=porcentaje_matriculados.values,
                                          names=porcentaje_matriculados.index,
                                          title='Porcentaje de Matriculados por Categoría',
                                          template=custom_template)
        return dcc.Graph(figure=fig_barras_matriculados), None
    
    elif opcion_seleccionada == 'ausentes':
        # Crear el gráfico de lineas
        # Extraer los datos para la gráfica
        sesiones = df_ausentes_por_sesion['sesion']
        ausentes = df_ausentes_por_sesion['ausentes']
        asistencia = df_ausentes_por_sesion['asistencia']
        # Crear la gráfica de líneas
        fig_ausentes = px.line(x=sesiones, y=ausentes, markers=True, 
                               title='Número de ausentes por sesión',
                               template=custom_template)
        return None, dcc.Graph(figure=fig_ausentes)
    elif opcion_seleccionada == 'asistencia_por_sesion':  # Nueva opción
        # Crear el gráfico de barras para asistencia por sesión
        fig_barras_ausentes_asistentes = px.bar(df_ausentes_por_sesion, 
                                                 x='sesion', 
                                                 y=['asistencia', 'ausentes'], 
                                                 title='Asistencia por Sesión',
                                                 labels={'sesion': 'Sesión', 'value': 'Estudiantes', 'variable': 'Estado'},
                                                 color_discrete_sequence=['khaki', 'lightslategray'],  # Colores para ausentes y presentes
                                                 barmode='group',
                                                 template=custom_template)  # Agrupar barras
        return dcc.Graph(figure=fig_barras_ausentes_asistentes), None

    else:
        # Ruta completa del archivo seleccionado
        ruta_archivo = os.path.join(directorio, opcion_seleccionada)

        # Cargar datos desde el archivo CSV seleccionado
        sesion_seleccionada = pd.read_csv(ruta_archivo)
        
        # Obtener la séptima columna (asistencia por sede)
        datos_sede = sesion_seleccionada.iloc[:, 6]

        # Calcular el porcentaje de asistencia por sede
        porcentaje_asistencia = datos_sede.value_counts(normalize=True) * 100

        # Crear el gráfico de pastel para asistencia
        fig_pastel_asistencia = px.pie(values=porcentaje_asistencia.values, 
                                        names=porcentaje_asistencia.index, 
                                        title='% Asistencia por sede')

        # Crear el gráfico de barras para estudiantes
        fig_barras_estudiantes = px.bar(x=porcentaje_asistencia.index, 
                                        y=porcentaje_asistencia.values, 
                                        title='# Estudiantes por sede',
                                        color=porcentaje_asistencia.index,
                                        color_discrete_sequence=px.colors.qualitative.Set3,
                                        template=custom_template)
        fig_barras_estudiantes.update_layout(xaxis_title='Sede', yaxis_title='Número de Estudiantes')

        return [dcc.Graph(figure=fig_pastel_asistencia), dcc.Graph(figure=fig_barras_estudiantes)], None


if __name__ == '__main__':
    app.run_server(debug=True)
