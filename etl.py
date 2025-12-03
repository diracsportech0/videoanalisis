import streamlit as st
import numpy as np
import pandas as pd
from Home_page import name_club, id_club
from functions import startfin_df
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, Sbopen)

#-------------------  LECTURA DE DATOS -----------
df = pd.read_excel('events.xlsx')
#df_players_excel = pd.read_excel('players.xlsx')
#-------------- ----  LIMPIEZA DE DATOS -----------
df = df.dropna(subset=['XY'])
#Añadir columna con segundos totales
def convert_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(':'))
    return minutes * 60 + seconds

# Aplicar la función a la columna 'time' y crear una nueva columna 'seconds'
df['seg_start'] = df['start_time'].apply(convert_to_seconds)
df['seg_clic'] = df['time'].apply(convert_to_seconds)
df['seg_end'] = df['end_time'].apply(convert_to_seconds)

#Limpieza columna XY
split_xy = df['XY'].str.split(' ', expand=True)
split_xy1 = split_xy[0].str.split(';', expand=True)
df['X'] = split_xy1[0].astype(int)
df['Y'] = split_xy1[1].astype(int)
#Excluir algunos eventos
#df = df[~df['Event'].isin(['Duelo Ofensivo'])]

# Dirección correcta de los eventos
def adjust_x(row):
    if row['invertido']:
        return 100 - row['X']
    else:
        return row['X']
def adjust_y(row):
    if row['invertido']:
        return 100 - row['Y']
    else:
        return row['Y']
df['X'] = df.apply(adjust_x, axis=1)
df['Y'] = df.apply(adjust_y, axis=1)
#Añadir columna con el tercio del campo
bins = [float('-inf'), 33, 67, float('inf')]
labels = ["1er tercio", "2do tercio", "3er tercio"]
df['zone'] = pd.cut(df['X'], bins=bins, labels=labels) #nueva columna usando pd.cut
# Formato 100x100 a 120x80
df['x'] = df['X']*1.2
df['y'] = df['Y']*0.8

'''
# -----Df de pases
df_pass = startfin_df (df,'Pase')
#---- DF CORNER
#df_corner= startfin_df (df,'Corner')

# SEPARAR EVENTOS
list_event_conteo = ['Carrera','Corner', 'Corner en contra', 'Despeje','Falta cometida', 'Falta recibida','Interceptación',
                     'Off-side', 'Otras perdidas','Presión','Tiro arco','Tiro desviado',
                     'Tiro bloqueado', 'Tiro en contra', 'Tiro libre', 'Tiro libre en contra', 'Recuperación'
                     ]
list_event_efectiv = ['Duelo aereo', 'Duelo defensivo','Pase','Regate'] #eventos que tienen efectividad
df_tipo1 = df[df['Event'].isin(list_event_conteo)]
df_tipo2 = df[df['Event'].isin(list_event_efectiv)]
'''