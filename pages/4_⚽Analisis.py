import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, Sbopen)
#from Home_page import name_club, id_club
from etl import df# df_pass
#from functions import mapa_pases, passmap_player,player_passmap


import plotly.express as px
from plotly.graph_objs import Scatter
from streamlit_plotly_events import plotly_events
from PIL import Image
#url_powerbi = '<iframe title="Plataforma Dirac v1.1" width="900" height="500" src="https://app.powerbi.com/view?r=eyJrIjoiOWM0YmNkMGEtMzc4Ni00MTI4LTk0OGEtZmFhNzc5NTZiYTkxIiwidCI6IjBlMGNiMDYwLTA5YWQtNDlmNS1hMDA1LTY4YjliNDlhYTFmNiIsImMiOjR9" frameborder="0" allowFullScreen="true"></iframe>'
#st.markdown(url_powerbi, unsafe_allow_html=True)
st.write(df)
#----------------------

#st.title(f'⚽ {name_club}')
colX, colY, colZ = st.columns([7, 8, 2])
with colX:st.title('⚽ ANÁLISIS')
with colY:pass
with colZ:st.image('logo-dirac.png', use_column_width=True)
#------------ 1. MENU LATERAL
menu_analisis = ['Equipo','Jugadores']
choice = st.sidebar.radio("Submenú - Análisis", menu_analisis, 0) #el 0 es el indice de la opcion por defecto
df_players = df.copy()
# ------------------- ANALISIS: EQUIPO ------
if choice == 'Equipo':
    # Barra lateral
    #RIVAL
    rivales = df.Rival.unique()
    n_partido = len(rivales)-1
    menu_match = st.sidebar.selectbox(
        "Rival",
        rivales,
        n_partido)
    #FASE Y TERCIO
    fases = df.Fase.unique()
    fases_list = fases.tolist()
    zona = list(df.Tercio.unique())
    #FASE --OK
    menu_fases = st.sidebar.selectbox(
        "Fase",
        sorted(fases_list),
        0)
    #TERCIO -- OK
    menu_zone = st.sidebar.selectbox(
        "Zona del campo",
        ['Todo']+zona,
        0)
    #Tipo de fase
    tipo_fase = df.Tipo.unique()
    tipo_list = tipo_fase.tolist()
    menu_tipo = st.sidebar.selectbox(
        "Tipo",
        ['Todos']+tipo_list,
        0)


    #FILTRADO DE data
    df = df[df.Rival==menu_match]
    df = df[df.Fase==menu_fases]
    if menu_zone == 'Todo':
        pass
    else:
        df = df[df.Tercio==menu_zone]
    if menu_tipo == 'Todos':
        pass
    else:
        df = df[df.Tipo==menu_tipo]      

# ------ GRAFICOS O TABLA RESUMEN DE DATA


# ------ GRAFICANDO CAMPOGRAMA
    fig = px.scatter(
        df, x='x', y='y',# labels={'Tipo': 'Tipo'},
        #color='Tipo',
        #color_discrete_map={
        #    'Correcto': 'black',
        #    'Erroneo': 'red',
        #    'No definido': 'blue'
        #},
        title=f'{menu_fases} vs {menu_match} <br> ➜', hover_data=['Tipo','Rival']
    )
    # Agregar la imagen de fondo al layout
    image = Image.open('campo.png')
    fig.add_layout_image(
        dict(
            source=image,
            xref="x", yref="y",
            x=0,y=0,
            sizex=120,sizey=80,
            sizing="stretch",
            opacity=0.8,
            layer="below",
        )
    )
    # Fijar el tamaño de los ejes
    fig.update_xaxes(range=[0, 120], tickvals=[40,80])
    fig.update_yaxes(range=[80, 0], tickvals=[25,55]) 
    fig.update_layout(
        margin=dict(l=40, r=5, t=50, b=30), # Ajustar los márgenes
        plot_bgcolor='lightgray', #fondo
        paper_bgcolor='lightgray',  # Color de fondo alrededor del gráfico
        hovermode='closest'  # closest' asegura que el punto más cercano al cursor será seleccionado.
    )


    #Mapeo de punto al que se hace clic con el evento
    #Esto se realiza porque se colocaron varios colores
    tipo_list = list(df.Tipo.unique())
    df['CurveN'] = df['Fase'].apply(lambda x: tipo_list.index(x) if x in tipo_list else -1)
    df['ptIndx'] = df.groupby('CurveN').cumcount()
    st.write(df)
    
    #funcion para entraer el tiempo de inicio y fin de la jugada
    def get_seg(df, curve_value, point_value, get_col):
        result = df.loc[(df['CurveN'] == curve_value) & (df['ptIndx'] == point_value), get_col]
        return result.iloc[0] if not result.empty else None 


    # Capturar el clic del usuario en el gráfico
    selected_points = plotly_events(fig, click_event=True, hover_event=False)
    # Si se ha seleccionado un punto, mostrar el video asociado
    df = df.reset_index(drop=True)
    if selected_points:
        point_idx = selected_points[0]['pointIndex']
        video_url = df.at[point_idx, 'Video'] #cuidado aqui, si hay dos fuente de video no funcionará
        curve_n = selected_points[0]['curveNumber']
        start_time = get_seg(df, curve_n, point_idx,'seg_start')
        end_time = get_seg(df, curve_n, point_idx,'seg_end')
        st.video(video_url, start_time=start_time, end_time=end_time, loop=0, muted=0)

# ----------- ANALISIS: JUGADORES -------------------------------------
elif choice == 'Jugadores':
    st.write("NO DISPONIBLE")