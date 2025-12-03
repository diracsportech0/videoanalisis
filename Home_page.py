import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")

# ENCABEZADO: escudo Melgar + escudo Liga1
colA, colB, colC = st.columns([1, 7, 1])
with colA:
    st.image('logo-equipo.png', use_column_width=True)
with colB:
    pass
with colC:
    st.image('logo-dirac.png', use_column_width=True)
    pass

#Lectura de datos
id_club = 4010102
df_clubs = pd.read_excel('db_club.xlsx')
dicc = df_clubs.set_index('id_club')['name_club'].to_dict()
name_club = dicc[id_club]

df_matches = pd.read_excel('Matches.xlsx')
df_matches = df_matches[df_matches['name_club1']==name_club]
df_matches = df_matches.sort_values('fecha', ascending=False)

#df_posiciones = pd.read_excel('tabla_posiciones_departamental.xlsx')
#df_temporada = pd.read_excel('posiciones_totales.xlsx')

#FORMATO
st.header(f'Bienvenido, {name_club}!!')

#colA2, colB2 = st.columns([7, 1])
#with colA2:
#    st.write('RECORRIDO 2024:')
#    st.write(df_temporada)
#with colB2:
#    #st.image('img-plataforma.png', use_column_width=True)
#    pass

st.write('RESULTADOS:')
#df_matches['Resultado'] = df_matches.apply(lambda row: '✅' if row['gol'] > row['gol_against'] else('➖' if row['gol']==row['gol_against'] else '❌'), axis=1)
dicc_ver_table = {'fecha':st.column_config.DateColumn('Fecha',format="DD/MM/YYYY"),
                    'id_distrito':None, 'id_club1':None, 'id_club2':None, 'name_club1':None, 'match':'Partido',
                    'gol':'G', 'gol_against':'G_contra', 'video':None, 'name_club2':None, 'match_filter':None,
                    'npartido':None, 'match_id':None,}
st.dataframe(df_matches, column_config=dicc_ver_table)

#Glosario
st.write('GLOSARIO')
glosario = pd.read_excel('Glosario eventos.xlsx')

st.markdown("""
    <style>
        div[data-testid="stTable"] td:nth-of-type(2) {
            max-width: 300px;
            word-wrap: break-word;
            white-space: normal;
        }
    </style>
""", unsafe_allow_html=True)

st.table(glosario)
#st.write(glosario)

#logo de empresa
colD, colE, colF = st.columns([4, 4, 1])
with colD:
    pass
with colE:
    pass
with colF:
    #st.write('Powered by')
    #st.image('piad-sinfondo.png', use_column_width=True)
    pass




