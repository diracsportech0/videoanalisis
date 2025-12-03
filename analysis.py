import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, Sbopen)
#from Home_page import name_club, id_club
from etl import df, df_pass
from functions import mapa_pases, passmap_player,player_passmap


import plotly.express as px
from plotly.graph_objs import Scatter
from streamlit_plotly_events import plotly_events
from PIL import Image
#url_powerbi = '<iframe title="Plataforma Dirac v1.1" width="900" height="500" src="https://app.powerbi.com/view?r=eyJrIjoiOWM0YmNkMGEtMzc4Ni00MTI4LTk0OGEtZmFhNzc5NTZiYTkxIiwidCI6IjBlMGNiMDYwLTA5YWQtNDlmNS1hMDA1LTY4YjliNDlhYTFmNiIsImMiOjR9" frameborder="0" allowFullScreen="true"></iframe>'
#st.markdown(url_powerbi, unsafe_allow_html=True)

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
    #ETAPA
    etapas = df.etapa.unique()
    etapa_filter = st.sidebar.selectbox(
        "Etapa",
        etapas,
        0)
    df = df[df.etapa==etapa_filter]
    #RIVALES
    rivales = df.match_filter.unique()
    n_partido = len(rivales)-1
    match = st.sidebar.selectbox(
        "Rival",
        rivales,
        n_partido)
    #EL RESTO
    events = df.Event.unique()
    events_list = events.tolist()
    #events_filter = sorted([event for event in events_list if event not in ['Pase']])
    zona = list(df.zone.unique())
    mitades = df.tiempo.unique().tolist()
    mitad = st.sidebar.selectbox(
        "Periodo",
        ['Completo']+mitades,
        0)
    type_event = st.sidebar.selectbox(
        "Evento",
        sorted(events_list),
        0)
    pitch_zone = st.sidebar.selectbox(
        "Zona del campo",
        ['Todo']+zona,
        0)
    
    #FILTRADO DE data
    #df = df[df.etapa==etapa_filter]
    df = df[df.match_filter==match]
    df = df[df.Event==type_event]
    if mitad == 'Completo':
        pass
    else:
        df = df[df.tiempo==mitad]
    if pitch_zone == 'Todo':
        pass
    else:
        df = df[df.zone==pitch_zone]   

    #------ TABLA DE ESTADITICAS DE PARTIDO --
    accion_counts = df.groupby('Event').size().reset_index(name='counts')
    # Calcular el número de eventos correctos por cada acción
    correct_counts = df[df['output'] == 'Correcto'].groupby('Event').size().reset_index(name='correct_counts')
    accion_counts = accion_counts.merge(correct_counts, on='Event', how='left')
    # Calcular la efectividad
    accion_counts['efectividad'] = accion_counts.apply(
        lambda row: row['correct_counts'] / row['counts'] if row['counts'] > 0 else None,
        axis=1)
    # Reemplazar la efectividad con None para eventos que tienen siempre output vacío
    accion_counts['efectividad'] = accion_counts.apply(
        lambda row: None if df[(df['Event'] == row['Event']) & (df['output'] == '')].shape[0] == row['counts'] else row['efectividad'],
        axis=1)
    cola1, cola2 = st.columns([1,1])
    with cola1: st.write(accion_counts)
    with cola2: pass

# Si se escoge pases hacer tambien un mapa de pases
    ######## --------------- MAPA DE PASES
    if type_event == 'Pase':
        df_pass = df_pass[df_pass.match_filter==match]
        if mitad != 'Completo': df_pass = df_pass[df_pass.tiempo==mitad]
        if pitch_zone != 'Todo': df_pass = df_pass[df_pass.zone==pitch_zone]
        colb1, colb2 = st.columns([1,1])
        with colb1: mapa_pases(df_pass,'Correcto',match)
        with colb2: mapa_pases(df_pass,'Erroneo',match)

    df['output'] = df['output'].fillna('No definido')
# ------ GRAFICANDO CAMPOGRAMA
    fig = px.scatter(
        df, x='x', y='y', labels={'output': 'Resultado'},
        #color='Event'
        color='output',
        color_discrete_map={
            'Correcto': 'black',
            'Erroneo': 'red',
            'No definido': 'blue'
        },
        title=f'{type_event} vs {match} <br> ➜', hover_data=['player','time','x','y']
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
    output_list = list(df.output.unique())
    df['CurveN'] = df['output'].apply(lambda x: output_list.index(x) if x in output_list else -1)
    df['ptIndx'] = df.groupby('CurveN').cumcount()
    #st.write(df)
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
        video_url = df.at[point_idx, 'video'] #cuidado aqui, si hay dos fuente de video no funcionará
        curve_n = selected_points[0]['curveNumber']
        start_time = get_seg(df, curve_n, point_idx,'seg_star')
        end_time = get_seg(df, curve_n, point_idx,'seg_end')
        st.video(video_url, start_time=start_time, end_time=end_time, loop=0, muted=0)

# ----------- ANALISIS: JUGADORES -------------------------------------
elif choice == 'Jugadores':
    # Barra lateral
    df_players = df_players.dropna(subset=['player'])
    rivales = df_players.match_filter.unique()
    n_partid = len(rivales)
    #rivales = df_players.name_club2.unique()
    events = df_players.Event.unique()
    events_list = sorted(events.tolist())
    #events_filter = [event for event in events_list if event not in ['Pase']]
    zona = list(df_players.zone.unique())
    players = sorted(df_players.player.unique())
    mitades = df_players.tiempo.unique().tolist()

    jugador = st.sidebar.selectbox(
        "Jugador",
        players,
        0)
    #type_event = st.sidebar.selectbox(
    #   "Evento",
    #  events_list,
    #   0)
    rival = st.sidebar.selectbox(
        "Rival",
        rivales,
        n_partid-1) #mostrar ultimo partido por defecto: n_partid-1
    mitad = st.sidebar.selectbox(
        "Periodo",
        ['Completo']+mitades,
        0)
    pitch_zone = st.sidebar.selectbox(
        "Zona del campo",
        ['Todo']+zona,
        0)
    #FILTRAR data
    df_players = df_players[df_players.player==jugador]
    #df = df[df.Event==type_event]
    df_players = df_players[df_players.match_filter==rival]
    if mitad == 'Completo':
        pass
    else:
        df_players = df_players[df_players.tiempo==mitad]
    if pitch_zone == 'Todo':
        pass
    else:
        df_players = df_players[df_players.zone==pitch_zone]  

    df_players = df_players.reset_index(drop=True) #ayuda a encontrar los indices
    
    ######## --------------- MAPA DE PASES
    df_pass_player = df_pass[df_pass.player==jugador]
    df_pass_player = df_pass_player[df_pass_player.match_filter==rival]
    if mitad != 'Completo': df_pass_player = df_pass_player[df_pass_player.tiempo==mitad]
    if pitch_zone != 'Todo': df_pass_player = df_pass_player[df_pass_player.zone==pitch_zone]
    player_passmap(df_pass_player,jugador,rival)

    df_players['output'] = df_players['output'].fillna('no aplica')
    # --- GRAFICANDO CAMPOGRAMA
    fig = px.scatter(
        df_players, x='x', y='y', color='Event', labels={'output': 'Resultado'},
        title=f'Acciones {jugador} vs {rival} <br> ➜', hover_data=['time','output']
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
            opacity=0.9,
            layer="below",
        )
    )

    # Fijar el tamaño de los ejes
    fig.update_xaxes(range=[0, 120], tickvals=[40,80])
    fig.update_yaxes(range=[80, 0], tickvals=[25,55]) 
    fig.update_layout(
        margin=dict(l=40, r=5, t=50, b=30), # Ajustar los márgenes
        #plot_bgcolor='lightgray',
        paper_bgcolor='lightgray',  # Color de fondo alrededor del gráfico
        hovermode='closest'  # closest' asegura que el punto más cercano al cursor será seleccionado.
    )

    #Mapeo de punto al que se hace clic con el evento
    #Esto se realiza solo para jugadores porque se grafican diferentes eventos y
    #al hacer clic cada evento tiene su propio CurveNumber
    events_player = list(df_players.Event.unique())
    df_players['CurveN'] = df_players['Event'].apply(lambda x: events_player.index(x) if x in events_player else -1)
    df_players['ptIndx'] = df_players.groupby('CurveN').cumcount()
    #st.write(df_players)

    #funcion para entraer el tiempo de inicio y fin de la jugada
    def get_seg(df, curve_value, point_value, get_col):
        result = df.loc[(df['CurveN'] == curve_value) & (df['ptIndx'] == point_value), get_col]
        return result.iloc[0] if not result.empty else None 

    # Capturar el clic del usuario en el gráfico
    selected_points = plotly_events(fig, click_event=True, hover_event=False)
    #st.write(selected_points)

    # Si se ha seleccionado un punto, mostrar el video asociado
    if selected_points:
        point_idx = selected_points[0]['pointIndex']
        curve_n = selected_points[0]['curveNumber']
        video_url = df_players.at[point_idx, 'video']
        start_time = get_seg(df_players, curve_n, point_idx,'seg_star')
        end_time = get_seg(df_players, curve_n, point_idx,'seg_end')
        #start_time = df_players.loc[point_idx, 'seg_star']
        #end_time = df_players.loc[point_idx, 'seg_end']
        st.video(video_url, start_time=start_time, end_time=end_time, loop=0, muted=0)