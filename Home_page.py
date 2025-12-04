import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")

# ENCABEZADO: escudo Melgar + escudo Liga1
colA, colB, colC = st.columns([1, 7, 1])
with colA:
    st.image('logo-dirac.png', use_column_width=True)
with colB:
    pass
with colC:
    st.image('logo-dirac.png', use_column_width=True)
    pass

#FORMATO
st.header(f'Bienvenido, DT Cesar Salas!!')





