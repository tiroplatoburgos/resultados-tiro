import streamlit as st
import pandas as pd

# 1. Configuración de Estilo Profesional
st.set_page_config(page_title="Dashboard Tiro al Plato", layout="wide")

# CSS para mejorar la apariencia de los botones
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
    }
    div.stButton > button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏆 Panel de Control: Resultados en Directo")

try:
    # 2. Carga y Preparación de Datos
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])
    
    # Convertir a numérico para ordenación técnica
    cols_puntos = ["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"]
    for col in cols_puntos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. Lógica de Menú de Categorías (Botones)
    if 'cat_sel' not in st.session_state:
        st.session_state.cat_sel = "GENERAL"

    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🌐 GENERAL"): st.session_state.cat_sel = "GENERAL"
    with col2:
        if st.button("🎯 CATEGORÍA 1"): st.session_state.cat_sel = "1"
    with col3:
        if st.button("🎯 CATEGORÍA 2"): st.session_state.cat_sel = "2"
    with col4:
        if st.button("🎯 CATEGORÍA 3"): st.session_state.cat_sel = "3"
    with col5:
        if st.button("🎯 CATEGORÍA 4"): st.session_state.cat_sel = "4"

    # 4. Filtros Laterales (Subcategorías)
    st.sidebar.header("Filtros Avanzados")
    sub_opciones = ["Todos", "Dama", "Junior", "Veterano"]
    sub_sel = st.sidebar.multiselect("Subcategorías:", sub_opciones, default="Todos")

    # 5. Aplicar Filtrado Jerárquico
    # Filtrar por Categoría
    if st.session_state.cat_sel != "GENERAL":
        df_filtrado = df[df["CAT. FU"].astype(str).str.contains(st.session_state.cat_sel)]
    else:
        df_filtrado = df.copy()

    # Filtrar por Subcategoría (mapeando con tu columna SUBC)
    if "Todos" not in sub_sel and sub_sel:
        # Mapeo de términos para que coincidan con los datos del Excel
        mapeo = {"Dama": "DAM", "Junior": "JUN", "Veterano": "VET"}
        terminos_busqueda = [mapeo.get(s, s) for s in sub_sel]
        df_filtrado = df_filtrado[df_filtrado["SUBC"].isin(terminos_busqueda)]

    # 6. Ordenación de Competición
    df_sorted = df_filtrado.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    )

    # Añadir ranking visual
    df_sorted.insert(0, "RANK", range(1, len(df_sorted) + 1))

    # 7. Visualización Final
    st.subheader(f"Mostrando: {st.session_state.cat_sel}")
    
    columnas_finales = ["RANK", "DORSAL", "NOMBRE Y APELLIDOS", "CAT. FU", "SUBC", "S-1", "S-2", "S-3", "S-4", "TOTAL"]
    st.dataframe(df_sorted[columnas_finales], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error en el dashboard: {e}")
