import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN PERSONALIZABLE
# ==========================================
TITULO_TIRADA = "I TIRADA GRAN PREMIO DE ESPAÑA"
FECHA_TIRADA = "12 de Abril de 2026"
URL_BANNER_TOP = "https://via.placeholder.com/1200x200.png?text=TU+PUBLICIDAD+AQUÍ" 
URL_BANNER_SIDE = "https://via.placeholder.com/300x600.png?text=ANUNCIO+LATERAL"

st.set_page_config(page_title=TITULO_TIRADA, layout="wide")

# Estilos CSS para los botones y colores
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%; border-radius: 20px; font-weight: bold; height: 3em;
    }
    /* Estilo para que la tabla ocupe toda la pantalla */
    .stTable { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# Banner y Cabecera
st.image(URL_BANNER_TOP, use_container_width=True)
st.title(f"🏆 {TITULO_TIRADA}")
st.write(f"📅 **Fecha:** {FECHA_TIRADA}")

try:
    # 1. CARGA DE DATOS (Fila 3 de Excel es el encabezado)
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Limpieza de números
    cols_puntos = ["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"]
    for col in cols_puntos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 2. BOTONES DE NAVEGACIÓN
    if 'cat' not in st.session_state: st.session_state.cat = "GENERAL"
    
    cols_btn = st.columns(5)
    nombres_cat = ["GENERAL", "1", "2", "3", "4"]
    for i, n in enumerate(nombres_cat):
        if cols_btn[i].button(f"🔘 {n}"):
            st.session_state.cat = n

    # 3. FILTROS LATERALES
    st.sidebar.image(URL_BANNER_SIDE)
    st.sidebar.header("Opciones de Filtrado")
    
    mapeo_subc = {"Dama": "DAM", "Junior": "JUN", "Veterano": "VET"}
    seleccion_sub = st.sidebar.multiselect("Filtrar Subcategoría:", list(mapeo_subc.keys()))

    # 4. LÓGICA DE FILTRADO
    df_f = df.copy()
    if st.session_state.cat != "GENERAL":
        df_f = df_f[df_f["CAT. FU"].astype(str).str.contains(st.session_state.cat)]

    if seleccion_sub:
        siglas = [mapeo_subc[s] for s in seleccion_sub]
        # Usamos str.contains para evitar fallos si hay espacios
        df_f = df_f[df_f["SUBC"].astype(str).isin(siglas)]

    # 5. ORDENACIÓN OFICIAL (TOTAL > S4 > S3 > S2 > S1 > DORSAL)
    df_f = df_f.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)
    df_f.insert(0, "Pos", df_f.index + 1)

    # 6. FUNCIÓN DE COLORES (25 ROJO, 24 VERDE)
    def color_puntos(val):
        if val == 25: return 'color: red; font-weight: bold'
        if val == 24: return 'color: green; font-weight: bold'
        return ''

    # 7. MOSTRAR TABLA ESTILO WEB
    st.subheader(f"📍 Clasificación {st.session_state.cat}")
    
    columnas = ["Pos", "DORSAL", "NOMBRE Y APELLIDOS", "CAT. FU", "SUBC", "S-1", "S-2", "S-3", "S-4", "TOTAL"]
    
    # Aquí está la corrección: usamos .map() en lugar de .applymap()
    df_styled = df_f[columnas].style.map(color_puntos, subset=["S-1", "S-2", "S-3", "S-4", "TOTAL"])
    
    st.table(df_styled)

except Exception as e:
    st.error(f"Error detectado: {e}")
