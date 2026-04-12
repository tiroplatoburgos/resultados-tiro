import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN PERSONALIZABLE
# ==========================================
TITULO_TIRADA = "I TIRADA GRAN PREMIO DE ESPAÑA"
FECHA_TIRADA = "12 de Abril de 2026"
URL_BANNER_TOP = "https://via.placeholder.com/1200x200.png?text=TU+PUBLICIDAD+AQUÍ" # Cambia por tu URL
URL_BANNER_SIDE = "https://tiroolimpicoburgos.es/wp-content/uploads/2022/12/cropped-logo.png"

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO
# ==========================================
st.set_page_config(page_title=TITULO_TIRADA, layout="wide")

# CSS Avanzado para colores y tabla a pantalla completa
st.markdown(f"""
    <style>
    /* Estilo para los botones de categoría */
    div.stButton > button {{
        width: 100%;
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        background-color: white;
        font-weight: bold;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{
        border-color: #ff4b4b;
        background-color: #fff5f5;
        color: #ff4b4b;
    }}
    /* Colores para las celdas */
    .puntos-25 {{ color: #ff0000; font-weight: bold; }}
    .puntos-24 {{ color: #008000; font-weight: bold; }}
    
    /* Hacer que la tabla use todo el ancho y no tenga scroll interno raro */
    .stDataFrame {{ width: 100%; }}
    </style>
""", unsafe_allow_html=True)

# Banner Superior
st.image(URL_BANNER_TOP, use_container_width=True)

st.title(f"🏆 {TITULO_TIRADA}")
st.subheader(f"📅 {FECHA_TIRADA}")

try:
    # 3. CARGA DE DATOS
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])
    
    # Limpiar numéricos
    cols_puntos = ["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"]
    for col in cols_puntos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 4. BOTONES DE CATEGORÍA (GENERAL + 1,2,3,4)
    if 'cat' not in st.session_state: st.session_state.cat = "GENERAL"
    
    cols_btn = st.columns(5)
    for i, nombre in enumerate(["GENERAL", "1", "2", "3", "4"]):
        if cols_btn[i].button(f"🔘 {nombre}"):
            st.session_state.cat = nombre

    # 5. SIDEBAR: SUBCATEGORÍAS Y PUBLICIDAD
    st.sidebar.image(URL_BANNER_SIDE, caption="Patrocinador Oficial")
    st.sidebar.header("Filtrar por Especialidad")
    
    # Mapeo exacto para evitar el fallo de "SUBC"
    mapeo_subc = {"Dama": "DAM", "Junior": "JUN", "Veterano": "VET", "Senior": "SR"}
    seleccion_sub = st.sidebar.multiselect("Subcategorías:", list(mapeo_subc.keys()))

    # 6. FILTRADO LÓGICO
    df_f = df.copy()
    
    # Filtro Categoría
    if st.session_state.cat != "GENERAL":
        df_f = df_f[df_f["CAT. FU"].astype(str).str.contains(st.session_state.cat)]

    # Filtro Subcategoría (Corregido)
    if seleccion_sub:
        siglas = [mapeo_subc[s] for s in seleccion_sub]
        df_f = df_f[df_f["SUBC"].isin(siglas)]

    # 7. ORDENACIÓN Y RANKING
    df_f = df_f.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)
    df_f.insert(0, "Pos", df_f.index + 1)

    # 8. ESTILO DE CELDAS (25 Rojo, 24 Verde)
    def highlight_scores(val):
        if val == 25: return 'color: red; font-weight: bold'
        if val == 24: return 'color: green; font-weight: bold'
        return ''

    # Seleccionamos y formateamos columnas
    columnas_web = ["Pos", "DORSAL", "NOMBRE Y APELLIDOS", "CAT. FU", "SUBC", "S-1", "S-2", "S-3", "S-4", "TOTAL"]
    df_display = df_f[columnas_web]

    # Aplicamos el estilo
    st.subheader(f"📍 Clasificación: {st.session_state.cat}")
    st.table(df_display.style.applymap(highlight_scores, subset=["S-1", "S-2", "S-3", "S-4", "TOTAL"]))

except Exception as e:
    st.error(f"Error al cargar la web: {e}")
