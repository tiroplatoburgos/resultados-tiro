import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURACIÓN Y ESTILO PROFESIONAL
# ==========================================
st.set_page_config(page_title="Resultados Tiro al Plato", layout="wide")

# CSS personalizado para botones de distintos tamaños y colores
st.markdown("""
    <style>
    /* Botones de Categoría (Grandes) */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    /* Estilo específico para subcategorías (botones más pequeños/discretos) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(n) .stButton > button {
        font-size: 14px;
        height: 2.5em;
    }
    
    /* Colores en la tabla */
    .text-25 { color: #ff0000; font-weight: bold; }
    .text-24 { color: #008000; font-weight: bold; }
    
    /* Tabla sin bordes y limpia */
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #1f4e78; color: white; padding: 10px; text-align: left; }
    td { padding: 8px; border-bottom: 1px solid #eee; }
    tr:nth-child(even) { background-color: #f2f2f2; }
    </style>
""", unsafe_allow_html=True)

# Variables de Sesión para mantener los filtros
if 'cat_sel' not in st.session_state: st.session_state.cat_sel = "GENERAL"
if 'sub_sel' not in st.session_state: st.session_state.sub_sel = "TODOS"

st.title("🏆 Resultados en Directo")
st.subheader(f"Filtro activo: {st.session_state.cat_sel} / {st.session_state.sub_sel}")

# ==========================================
# 2. BLOQUE DE BOTONES (CATEGORÍAS Y SUBCATEGORÍAS)
# ==========================================

# Fila 1: Categorías Principales
cols1 = st.columns(5)
btns_cat = ["GENERAL", "1ª CAT", "2ª CAT", "3ª CAT", "4ª CAT"]
for i, cat in enumerate(btns_cat):
    if cols1[i].button(cat, type="primary" if st.session_state.cat_sel in cat else "secondary"):
        st.session_state.cat_sel = cat
        st.session_state.sub_sel = "TODOS" # Reset subcat al cambiar categoría

# Fila 2: Subcategorías (Más pequeños)
st.write("---") # Separador visual fino
cols2 = st.columns(6)
btns_sub = ["TODOS", "DAMAS", "JUNIOR", "VETERANO", "SENIOR", "ADAPTADO"]
mapeo_sub = {"TODOS": "TODOS", "DAMAS": "DAM", "JUNIOR": "JUN", "VETERANO": "VET", "SENIOR": "SR", "ADAPTADO": "ADA"}

for i, sub in enumerate(btns_sub):
    if cols2[i].button(sub, use_container_width=True):
        st.session_state.sub_sel = sub

# ==========================================
# 3. PROCESAMIENTO DE DATOS
# ==========================================
try:
    # Carga de datos (ajustado a tu Excel "RESULTADOS WEB.xlsm")
    df = pd.read_excel("RESULTADOS WEB.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Conversión a enteros para evitar decimales (.0)
    for col in ["DORSAL", "TOTAL", "S-1", "S-2", "S-3", "S-4"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # --- FILTRADO ---
    df_f = df.copy()
    
    # Filtro Categoría
    if st.session_state.cat_sel != "GENERAL":
        # Extraemos el número del botón (ej: "2ª CAT" -> "2")
        num_cat = st.session_state.cat_sel[0]
        df_f = df_f[df_f["CAT. FU"].astype(str).str.contains(num_cat)]

    # Filtro Subcategoría
    if st.session_state.sub_sel != "TODOS":
        sigla = mapeo_sub[st.session_state.sub_sel]
        df_f = df_f[df_f["SUBC"].astype(str).str.contains(sigla)]

    # --- ORDENACIÓN (Lógica de desempate) ---
    df_f = df_f.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    )

    # --- RENDERIZADO DE TABLA HTML (Para colores 24 y 25) ---
    html = """<table><thead><tr>
                <th>POS</th><th>DORSAL</th><th>NOMBRE Y APELLIDOS</th><th>CAT</th><th>SUBC</th>
                <th>S1</th><th>S2</th><th>S3</th><th>S4</th><th>TOTAL</th>
              </tr></thead><tbody>"""

    for i, (_, row) in enumerate(df_f.iterrows()):
        pos = i + 1
        html += f"<tr><td>{pos}</td><td>{row['DORSAL']}</td><td>{row['NOMBRE Y APELLIDOS']}</td>"
        html += f"<td>{row['CAT. FU']}</td><td>{row['SUBC']}</td>"
        
        # Aplicar colores a las series y total
        for col in ["S-1", "S-2", "S-3", "S-4", "TOTAL"]:
            val = row[col]
            clase = ""
            if val == 25: clase = ' class="text-25"'
            elif val == 24: clase = ' class="text-24"'
            html += f"<td{clase}>{val}</td>"
        html += "</tr>"
    
    html += "</tbody></table>"
    st.write(html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error técnico: {e}")
    st.info("Revisa que el archivo se llame 'RESULTADOS WEB.xlsm' en GitHub.")
