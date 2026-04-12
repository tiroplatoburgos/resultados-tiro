import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN PERSONALIZABLE
# ==========================================
TITULO_TIRADA = "1ª TIRADA DEL AÑO 2026"
FECHA_TIRADA = "12 de Abril de 2026"
URL_BANNER_TOP = "https://via.placeholder.com/1200x200.png?text=TU+PUBLICIDAD+AQUÍ"

st.set_page_config(page_title=TITULO_TIRADA, layout="wide")

# CSS Avanzado para estética de Dashboard Profesional (Estilo Cebra y sin bordes)
st.markdown("""
    <style>
    /* Estilo de los botones de categoría */
    div.stButton > button {
        width: 100%; border-radius: 10px; font-weight: bold; height: 3.5em;
        background-color: #f8f9fa; border: 1px solid #ddd;
    }
    div.stButton > button:hover { border-color: #007bff; color: #007bff; }
    
    /* Estilo de la tabla HTML */
    .puntos-table { width: 100%; border-collapse: collapse; font-family: sans-serif; }
    .puntos-table th { background-color: #1f4e78; color: white; padding: 12px; text-align: center; border: none; }
    .puntos-table td { padding: 10px; text-align: center; border: none; }
    .puntos-table tr:nth-child(even) { background-color: #f2f2f2; } /* Fila Oscura */
    .puntos-table tr:nth-child(odd) { background-color: #ffffff; }  /* Fila Clara */
    
    .text-25 { color: red; font-weight: bold; }
    .text-24 { color: green; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.image(URL_BANNER_TOP, use_container_width=True)
st.title(f"🏆 {TITULO_TIRADA}")
st.write(f"📅 **{FECHA_TIRADA}**")

try:
    # 1. CARGA Y LIMPIEZA TOTAL
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # CONVERSIÓN A ENTEROS (Adiós a los decimales .0)
    cols_num = ["DORSAL", "S-1", "S-2", "S-3", "S-4", "TOTAL"]
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 2. BOTONES DE CATEGORÍA CON NUEVOS NOMBRES
    if 'cat_sel' not in st.session_state: st.session_state.cat_sel = "GENERAL"
    
    col_nav = st.columns(5)
    labels = ["GENERAL", "1ª CATEGORIA", "2ª CATEGORIA", "3ª CATEGORIA", "4ª CATEGORIA"]
    values = ["GENERAL", "1", "2", "3", "4"]
    
    for i in range(5):
        if col_nav[i].button(labels[i]):
            st.session_state.cat_sel = values[i]

    # 3. FILTROS DE SUBCATEGORÍA (JR y DM corregidos)
    st.sidebar.header("Filtros Especiales")
    # Mapeo exacto según tus indicaciones
    mapeo_sub = {"Dama": "DM", "Junior": "JR", "Veterano": "VET"}
    sel_sub = st.sidebar.multiselect("Subcategoría:", list(mapeo_sub.keys()))

    # 4. FILTRADO LÓGICO
    df_f = df.copy()
    if st.session_state.cat_sel != "GENERAL":
        df_f = df_f[df_f["CAT. FU"].astype(str).str.contains(st.session_state.cat_sel)]

    if sel_sub:
        siglas = [mapeo_sub[s] for s in sel_sub]
        df_f = df_f[df_f["SUBC"].astype(str).str.strip().isin(siglas)]

    # 5. ORDENACIÓN OFICIAL
    df_f = df_f.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)
    df_f.insert(0, "Pos", range(1, len(df_f) + 1))

    # 6. CONSTRUCCIÓN DE LA TABLA HTML (Estilo Profesional)
    st.subheader(f"📍 Clasificación: {st.session_state.cat_sel if st.session_state.cat_sel == 'GENERAL' else st.session_state.cat_sel + 'ª Cat'}")
    
    # Iniciamos la tabla
    html = '<table class="puntos-table"><thead><tr>'
    columnas = ["Pos", "DORSAL", "NOMBRE Y APELLIDOS", "CAT. FU", "SUBC", "S-1", "S-2", "S-3", "S-4", "TOTAL"]
    for col in columnas:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'

    for _, row in df_f.iterrows():
        html += '<tr>'
        for col in columnas:
            val = row[col]
            # Aplicar colores a los resultados
            style_class = ""
            if col in ["S-1", "S-2", "S-3", "S-4", "TOTAL"]:
                if val == 25: style_class = ' class="text-25"'
                elif val == 24: style_class = ' class="text-24"'
            
            html += f'<td{style_class}>{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    
    # Renderizar la tabla
    st.write(html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error técnico: {e}")
