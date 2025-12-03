import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, Sbopen)
from scipy.ndimage import gaussian_filter
from matplotlib.colors import LinearSegmentedColormap



#-----------  FUNCION GENERAR DF CON DOS PUNTOS (INICIO Y FIN)
def startfin_df (df, evento):
    df_out = df[df.Event==evento]
    split_pase_xy = df_out['XY'].str.split(' ', expand=True)
    split_pase_xy2 = split_pase_xy[1].str.split(';', expand=True)
    def safe_convert_to_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return ''
    df_out['X_end'] = split_pase_xy2[0].apply(safe_convert_to_int)
    df_out['Y_end'] = split_pase_xy2[1].apply(safe_convert_to_int)
    # Dirección correcta de los eventos END
    def adjust_x_end(row):
        if row['invertido']:
            return 100 - row['X_end']
        else:
            return row['X_end']
    def adjust_y_end(row):
        if row['invertido']:
            return 100 - row['Y_end']
        else:
            return row['Y_end']
            
    df_out['X_end'] = df_out.apply(adjust_x_end, axis=1)
    df_out['Y_end'] = df_out.apply(adjust_y_end, axis=1)
    df_out['x_end'] = df_out['X_end']*1.2
    df_out['y_end'] = df_out['Y_end']*0.8
    
    return df_out


# --------------------------- FUNCION GRÁFICO DE BARRAS + LINEAS --------
def graph_barras(df_stats, metrica,mapa_color):
    fig = go.Figure()

    # Crear las barras para "local"
    fig.add_trace(
        go.Bar(
            x=df_stats[df_stats['localidad'] == 'local']['n'],  # Filtrar filas donde localidad es "local"
            y=df_stats[df_stats['localidad'] == 'local'][metrica],
            marker_color=mapa_color['local'],
            name='Local',  # Nombre en la leyenda
            text=df_stats[df_stats['localidad'] == 'local']['match_filter'],
            hovertemplate='Partido: %{text}<br>Valor: %{y}<extra></extra>'
        )
    )
    # Crear las barras para "visita"
    fig.add_trace(
        go.Bar(
            x=df_stats[df_stats['localidad'] == 'visita']['n'],  # Filtrar filas donde localidad es "visita"
            y=df_stats[df_stats['localidad'] == 'visita'][metrica],
            marker_color=mapa_color['visita'],
            name='Visita',  # Nombre en la leyenda
            text=df_stats[df_stats['localidad'] == 'visita']['match_filter'],
            hovertemplate='Partido: %{text}<br>Valor: %{y}<extra></extra>'
        )
    )

    # Crear el gráfico de líneas para la media
    fig.add_trace(
        go.Scatter(
            x=df_stats['n'],
            y=[df_stats[metrica].mean()] * df_stats.shape[0],
            name='Media',
            marker_color='red',
            mode='lines'
        )
    )
    # Personalizar el layout del gráfico
    fig.update_layout(
        width=350,
        height=280,
        title=f'Evolución {metrica}',
        xaxis_title='Partidos',
        #barmode='stack'  # Cambiar a "stack" si deseas apilar las barras o "group" para separarlas
    )
    
    return fig


########----------------- FUNCION 2 MAPAS DE PASES SEPARADOS--- 
def mapa_pases(df_pass,output_pass,oponente):
    pitch = Pitch(pitch_color='#22312b', line_color='#c7d5cc')
    fig_pass_map, axs = pitch.grid(endnote_height=0.03, endnote_space=0, figheight=12,
                        title_height=0.06, title_space=0, grid_height=0.86,
                        axis=False)
    fig_pass_map.set_facecolor('#22312b')

    if output_pass=='Correcto': 
        color_f='#ad993c'
        output='COMPLETOS'
    elif output_pass=='Erroneo':
        color_f='#ba4f45'
        output='INCOMPLETOS'

    # Plot
    mask_complete = df_pass.output==output_pass
    pitch.arrows(df_pass[mask_complete].x, df_pass[mask_complete].y,
                df_pass[mask_complete].x_end, df_pass[mask_complete].y_end, width=2, headwidth=10,
                headlength=10, color=color_f, ax=axs['pitch'],
                label=output
                )
    # Set up the legend
    legend = axs['pitch'].legend(facecolor='#22312b', handlelength=5, edgecolor='None',
                                loc='best')
    for text in legend.get_texts():
        text.set_fontsize(25)
    # endnote and title
    axs['endnote'].text(1, 0.5, '@dirac.sportech', va='center', ha='right', fontsize=20,
                        color='#dee6ea')

    axs['title'].text(0.5, 0.5, f'MAPA DE PASES {output} VS  {oponente}', color='#dee6ea',
                        va='center', ha='center',
                        fontsize=25)

    st.pyplot(fig_pass_map)

#--------------------- -MAPA DE CALOR (escogiendo lista de metricas)-------------
def heat_map(df, metricas):
    # Si no se pasan métricas, usamos todas las del DataFrame
    if metricas is None or len(metricas) == 0:
        metricas = df['Event'].unique()
    # Filtrar solo las métricas deseadas
    df = df[df['Event'].isin(metricas)]
    
    # setup pitch
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2,
                pitch_color='#22312b', line_color='#efefef')
    # draw
    fig, ax = pitch.draw(figsize=(6.6, 4.125))
    fig.set_facecolor('#22312b')
    bin_statistic = pitch.bin_statistic(df.x, df.y, statistic='count', bins=(25, 25))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
    pcm = pitch.heatmap(bin_statistic, ax=ax, cmap='hot', edgecolors='#22312b')
    # Add the colorbar and format off-white
    #cbar = fig.colorbar(pcm, ax=ax, shrink=0.6)
    #cbar.outline.set_edgecolor('#efefef')
    #cbar.ax.yaxis.set_tick_params(color='#efefef')
    #ticks = plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#efefef')
    st.pyplot(fig)

# --------------------- FUNCION MAPA DE PASES DE UN JUGADOR (completo + incompletos) --------
def player_passmap(df_pass, player, oponente):
    mask_complete = df_pass.output=='Correcto'
    # Set up the pitch
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    #pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='green')
    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor('#22312b')
    #Efectividad
    n_pass_corr = df_pass[mask_complete].shape[0]
    n_pass = df_pass.shape[0]
    efectiv_pass = n_pass_corr/n_pass
    # Plot the completed passes
    pitch.arrows(df_pass[mask_complete].x, df_pass[mask_complete].y,
                df_pass[mask_complete].x_end, df_pass[mask_complete].y_end, width=2,
                headwidth=10, headlength=10, color='#ad993c', ax=ax, label='completo')
    # Plot the other passes
    pitch.arrows(df_pass[~mask_complete].x, df_pass[~mask_complete].y,
                df_pass[~mask_complete].x_end, df_pass[~mask_complete].y_end, width=2,
                headwidth=6, headlength=5, headaxislength=12,
                color='#ba4f45', ax=ax, label='incompleto')
    # Set up the legend
    ax.legend(facecolor='#22312b', handlelength=5, edgecolor='None', fontsize=18, loc='best',labelcolor='white')
    # Añadir pie de página
    footer_text = str(round(efectiv_pass*100,2)) + "%"
    ax.text(120, 82, footer_text, fontsize=20, color='white', ha='right', va='top', alpha=0.7)   
    # Set the title
    ax_title = ax.set_title(f'Pases {player} vs {oponente}', fontsize=25, color='white')
    st.pyplot(fig)


####################### FUNCION PORCENTAJE POR CADA CUADRICULA

def graph_percents(df,mask, metrica, rival,colormapeo,
                   df_extra=pd.DataFrame(columns=["Event","x_end", "y_end"])):
    df_sel = df.loc[mask, ['Event','x', 'y']]
    # artificio para incluir dentro de las perdidas el punto final de los pases no completados
    df_extra = df_extra[['Event','x_end','y_end']]
    df_extra.rename(columns={'x_end': 'x', 'y_end': 'y'}, inplace=True)
    df_sel = pd.concat([df_sel,df_extra], axis=0, ignore_index=True)
    st.write(df_sel)
    #
    #st.write(df_sel)
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0',line_color='#595b5a')
    fig, ax = pitch.draw(figsize=(8.25, 12))

    fig.set_facecolor('#f4edf0')
    bin_statistic = pitch.bin_statistic(df_sel.x, df_sel.y, statistic='count', bins=(6, 5), normalize=True)
    pitch.heatmap(bin_statistic, ax=ax, cmap=colormapeo, edgecolor='#f9f9f9')
    labels = pitch.label_heatmap(bin_statistic, color='#f4edf0', fontsize=14,
                                ax=ax, ha='center', va='center',
                                str_format='{:.0%}', path_effects=path_eff)

    ax.set_title(f'Gráfico % {metrica} vs {rival}', fontsize=16, color='black', pad=1)
    fig.text(0.75, 0.26, 'PIAD SPORTS', ha='center', fontsize=10, color='gray')
    st.pyplot(fig)


# --------------------------- FUNCION MAPA DE TIROS --------
def shot_map(df, mask):
    df_sel = df.loc[mask, ['x', 'y','type']]
    # Crear el campo (medio campo de StatsBomb)
    pitch = VerticalPitch(pitch_type='statsbomb',  # Usamos pitch tipo StatsBomb
                        half=True,  # Medio campo
                        pitch_color='#22312b',
                        line_color='#c7d5cc')
    # Crear la figura y los ejes
    fig, ax = plt.subplots(figsize=(10, 8))
    pitch.draw(ax=ax)

    # Definir colores para los diferentes tipos de tiros
    colors = {
        'Tiro bloqueado': 'green',
        'Tiro arco': 'red',
        'Tiro desviado': 'blue'
    }
    # Dibujar los tiros en diferentes colores según el tipo de tiro
    for event_type, color in colors.items():
        df_event = df[(df['Event'] == event_type) & (df['type'] != 'Gol')]  # Filtrar los no goles
        pitch.scatter(df_event['x'], df_event['y'], ax=ax, color=color, s=300, edgecolors='black', label=event_type, zorder=3)
    # Dibujar los tiros que son GOLES con una imagen o marcador de pelota
    df_goals = df_sel[df_sel['type'] == 'Gol']
    pitch.scatter(df_goals['x'], df_goals['y'], ax=ax, color='yellow', s=500, marker='*', edgecolors='black', zorder=4, label='Goal')
    '''
    for idx, row in df_goals.iterrows():
        pitch.scatter(row['x'], row['y'], ax=ax, color='yellow', s=500, marker='*', edgecolors='black', label='Gol', zorder=4)
    '''
    # Añadir la leyenda
    plt.legend(loc='upper left', fontsize=12)

    st.pyplot(fig)


######### MAPA DE CALOR COMPLETO
def complete_heatmap(df,mask,rival,periodo,titulo):
    df_sel = df.loc[mask, ['x', 'y']]

    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b',
                        )
    fig, axs = pitch.grid(endnote_height=0.03, endnote_space=0,
                        # leave some space for the colorbar
                        grid_width=0.88, left=0.025,
                        title_height=0.06, title_space=0,
                        # Turn off the endnote/title axis. I usually do this after
                        # I am happy with the chart layout and text placement
                        axis=False,
                        grid_height=0.86)
    fig.set_facecolor('#22312b')

    # plot heatmap
    bin_statistic = pitch.bin_statistic(df_sel.x, df_sel.y, statistic='count', bins=(25, 25))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
    pcm = pitch.heatmap(bin_statistic, ax=axs['pitch'], cmap='hot', edgecolors='#22312b')

    # add cbar
    ax_cbar = fig.add_axes((0.915, 0.093, 0.03, 0.786))
    cbar = plt.colorbar(pcm, cax=ax_cbar)
    cbar.outline.set_edgecolor('#efefef')
    cbar.ax.yaxis.set_tick_params(color='#efefef')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#efefef')
    for label in cbar.ax.get_yticklabels():
        label.set_fontproperties(robotto_regular.prop)
        label.set_fontsize(15)

    # endnote and title
    axs['endnote'].text(1, 0.5, '@dirac.sportech', va='center', ha='right', fontsize=15,
                        fontproperties=robotto_regular.prop, color='#dee6ea')
    ax_title = axs['title'].text(0.5, 0.5, f"{titulo} vs {rival} - {periodo}", color='white',
                                va='center', ha='center', path_effects=path_eff,
                                fontproperties=robotto_regular.prop, fontsize=30)
    
    st.pyplot(fig)


# ----------------- FUNCION GRAFICO EVENTO CON DOS PUNTOS (completo + incompletos) --------
def graph_event_inifin(df,oponente, periodo,name_event):
    #df = df[df.Event==evento]
    mask_complete = df.output=='Correcto'
    # Set up the pitch
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    #pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='green')
    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor('#22312b')
    # Plot the completed passes
    pitch.arrows(df[mask_complete].x, df[mask_complete].y,
                df[mask_complete].x_end, df[mask_complete].y_end, width=2,
                headwidth=10, headlength=10, color='#ad993c', ax=ax, label='completo')
    # Plot the other passes
    pitch.arrows(df[~mask_complete].x, df[~mask_complete].y,
                df[~mask_complete].x_end, df[~mask_complete].y_end, width=2,
                headwidth=6, headlength=5, headaxislength=12,
                color='#ba4f45', ax=ax, label='incompleto')
    # Set up the legend
    ax.legend(facecolor='#22312b', handlelength=5, edgecolor='None', fontsize=18, loc='best',labelcolor='white')
    # Set the title
    ax_title = ax.set_title(f' {name_event} vs {oponente} - {periodo}', fontsize=25, color='white')
    st.pyplot(fig)

##########m IGUAL QUE EL ANTERIOR PERO CON LINEAS Y O FLECHAS
def graph_event_inifin_lines(df,oponente, periodo,name_event):
    #df = df[df.Event==evento]
    mask_complete = df.output=='Correcto'
    # Set up the pitch
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    #pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='green')
    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor('#22312b')
    # Plot the completed passes
    pitch.lines(df[mask_complete].x, df[mask_complete].y,
                df[mask_complete].x_end, df[mask_complete].y_end,
                lw=5, transparent=True, comet=True, color='#ad993c', ax=ax, label='completo')
    # Plot the other passes
    pitch.lines(df[~mask_complete].x, df[~mask_complete].y,
                df[~mask_complete].x_end, df[~mask_complete].y_end,
                lw=5, transparent=True, comet=True,
                color='#ba4f45', ax=ax, label='incompleto')
    # Set up the legend
    ax.legend(facecolor='#22312b', handlelength=5, edgecolor='None', fontsize=18, loc='best',labelcolor='white')
    # Set the title
    ax_title = ax.set_title(f' {name_event} vs {oponente} - {periodo}', fontsize=25, color='white')
    st.pyplot(fig)

###################################################################



# --------------------------- FUNCION GRÁFICO % POR ZONAS (zonas modelo posesión)--------
robotto_regular = FontManager()
import matplotlib.patheffects as path_effects
path_eff = [path_effects.Stroke(linewidth=3, foreground='black'),
            path_effects.Normal()]

def graph_zone_percent(df,mask,partido,periodo,color_map,titulo):
    df_sel = df.loc[mask, ['x', 'y']]

    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#1e4259',
                        )
    fig, axs = pitch.grid(endnote_height=0.03, endnote_space=0,
                        title_height=0.08, title_space=0,
                        # Turn off the endnote/title axis. I usually do this after
                        # I am happy with the chart layout and text placement
                        axis=False,
                        grid_height=0.84)
    fig.set_facecolor('#1e4259')

    # heatmap and labels
    bin_statistic = pitch.bin_statistic_positional(df_sel.x, df_sel.y, statistic='count',
                                                positional='full', normalize=True)
    pitch.heatmap_positional(bin_statistic, ax=axs['pitch'],
                            cmap=color_map, edgecolors='#22312b')
    labels = pitch.label_heatmap(bin_statistic, color='#f4edf0', fontsize=18,
                                ax=axs['pitch'], ha='center', va='center',
                                str_format='{:.0%}', path_effects=path_eff)

    # endnote and title
    axs['endnote'].text(1, 0.5, '@dirac.sportech', va='center', ha='right', fontsize=15,
                        fontproperties=robotto_regular.prop, color='#dee6ea')
    axs['title'].text(0.5, 0.5, f"{titulo} vs {partido} - {periodo}", color='#dee6ea',
                    va='center', ha='center', path_effects=path_eff,
                    fontproperties=robotto_regular.prop, fontsize=20)
    st.pyplot(fig)


    
# --------------------------- FUNCION MAPA DE PASES FONDO BLANCO - DISEÑO ANTIGUO --------
def passmap_player(df_pass,player,oponente):
    pitch = Pitch(pitch_color='white', line_color='green', stripe=False, pitch_length=120, pitch_width=80)
    fig, ax = pitch.draw(figsize=(10, 5))

    X_id = df_pass.columns.get_loc('x')
    Y_id = df_pass.columns.get_loc('y')
    Xend_id = df_pass.columns.get_loc('x_end')
    Yend_id = df_pass.columns.get_loc('y_end')
   #Pase normal exitoso
    pases_exito = df_pass[df_pass.output=='Correcto']
    pases_exito.plot(kind='scatter', x='x', y='y', ax=ax, grid=False, color='black', label='Exitoso')
    for d in range (pases_exito.shape[0]):
        plt.arrow(pases_exito.iloc[d,X_id],pases_exito.iloc[d,Y_id],pases_exito.iloc[d,Xend_id]-pases_exito.iloc[d,X_id],
                  pases_exito.iloc[d,Yend_id]-pases_exito.iloc[d,Y_id],shape='full', color='k',
                length_includes_head=True, zorder=1, head_length=2., head_width=1.3, linewidth=0.5,
                head_starts_at_zero=False)
    #Pase normal erróneo
    pases_error = df_pass[df_pass.output=='Erroneo']
    pases_error.plot(kind='scatter', x='x', y='y', ax=ax, grid=False, color='red', label='Erróneo')
    for d in range (pases_error.shape[0]):
        plt.arrow(pases_error.iloc[d,X_id],pases_error.iloc[d,Y_id],pases_error.iloc[d,Xend_id]-pases_error.iloc[d,X_id], pases_error.iloc[d,Yend_id]-pases_error.iloc[d,Y_id],shape='full', color='r', length_includes_head=True,
        zorder=1, head_length=3., head_width=1.5)
    titulo = f'Pases de  {player} vs. {oponente}'
    ax.set_title(titulo,fontsize=15)
    st.pyplot(fig)



'''
    def graph_barras(df_stats, metrica, color_map):
    colors = df_stats['localidad'].map(color_map)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_stats['n'],
            y=df_stats[metrica],
            #marker_color=color,
            marker_color=colors,
            #text=df_stats[metrica],
            #name='valor'),
            text=df_stats['match_filter'],  # Usa 'text' para mostrar 'match_filter' en el hover
            name='valor',
            hovertemplate='Partido: %{text}<br>Valor: %{y}<extra></extra>',)  # Formato de tooltip
    )
    # Crear el gráfico de líneas
    fig.add_trace(
        go.Scatter(
            x=df_stats['n'],
            y=[df_stats[metrica].mean()] * df_stats.shape[0],
            name='media',
            marker_color='red',
            mode='lines')
    )
    # Personalizar el layout del gráfico
    fig.update_layout(
        width=350,
        height=280,
        title= f'Evolución {metrica}',
        xaxis_title='Partidos',
        #yaxis_title='Cantidad',
    )
    #st.plotly_chart(fig)
    return fig
'''