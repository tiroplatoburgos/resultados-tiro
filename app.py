import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os

# ==========================================
# CONFIGURACIÓN PERSONALIZABLE (Cambia aquí)
# ==========================================
TITULO_TIRADA = "1ª TIRADA AÑO 2026 - CLUB DE TIRO"
# ==========================================

st.set_page_config(page_title="Marcador Profesional", layout="wide")

# Estilos Visuales
st.markdown(f"""
    <style>
    .stApp {{ background-color: #fdfaf6; }}
    .block-container {{ max-width: 1100px; padding-top: 1rem; margin: auto; }}
    
    /* Cabecera */
    .header-container {{
        display: flex;
        align-items: center;
        justify-content: space-around;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }}
    .header-title {{
        text-align: center;
        font-size: 26px;
        font-weight: 800;
        color: #1a365d;
        text-transform: uppercase;
    }}

    /* Botones uniformes */
    div.stButton > button {{
        width: 100%;
        height: 40px;
        font-size: 13px !important;
        border-radius: 6px;
    }}
    </style>
""", unsafe_allow_html=True)

# 1. CABECERA CON LOGOS
col_l, col_t, col_r = st.columns([1, 4, 1])
with col_l:
    if os.path.exists("logo_izquierdo.png"):
        st.image("logo_izquierdo.png")
with col_t:
    st.markdown(f"<div class='header-title'>{TITULO_TIRADA}</div>", unsafe_allow_html=True)
with col_r:
    if os.path.exists("logo_derecho.png"):
        st.image("logo_derecho.png")

# 2. CARGA DE DATOS
try:
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    for col in ["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL", "CAT. FU"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)

    # 3. FILTROS (BOTONES EN FILA)
    if 'c_f' not in st.session_state: st.session_state.c_f = "GENERAL"
    if 's_f' not in st.session_state: st.session_state.s_f = None

    btn_cols = st.columns(9)
    
    with btn_cols[0]:
        if st.button("GENERAL", type="primary" if st.session_state.c_f == "GENERAL" else "secondary"):
            st.session_state.c_f = "GENERAL"; st.session_state.s_f = None

    c_map = {"1ª CAT": 1, "2ª CAT": 2, "3ª CAT": 3, "4ª CAT": 4}
    for i, (lab, val) in enumerate(c_map.items()):
        with btn_cols[i+1]:
            if st.button(lab, type="primary" if st.session_state.c_f == val else "secondary"):
                st.session_state.c_f = "GENERAL" if st.session_state.c_f == val else val

    s_map = {"SENIOR": "SR", "DAMAS": "DM", "JUNIOR": "JR", "VET.": "VET"}
    for i, (lab, val) in enumerate(s_map.items()):
        with btn_cols[i+5]:
            if st.button(lab, type="primary" if st.session_state.s_f == val else "secondary"):
                st.session_state.s_f = None if st.session_state.s_f == val else val

    # Filtrar
    df_f = df_sorted.copy()
    if st.session_state.c_f != "GENERAL":
        df_f = df_f[df_f["CAT. FU"] == st.session_state.c_f]
    if st.session_state.s_f:
        df_f = df_f[df_f["SUBC"] == st.session_state.s_f]
    
    df_f = df_f.reset_index(drop=True)
    podio = df_f.head(3)
    resto = df_f.iloc[3:]

    # 4. TABLA HTML
    def draw_table(p, r):
        # Definición de anchos fijos para evitar descuadres
        w = {"pos":"6%", "dor":"6%", "nom":"26%", "prov":"12%", "cat":"8%", "sub":"8%", "s":"6%", "tot":"10%"}
        
        style = f"""
        <style>
            table {{ width: 100%; border-collapse: collapse; table-layout: fixed; background: #fff; font-family: sans-serif; }}
            th, td {{ padding: 10px 2px; text-align: center; font-size: 14px; border-bottom: 1px solid #eee; overflow: hidden; white-space: nowrap; }}
            .w-pos {{ width: {w['pos']}; }} .w-dor {{ width: {w['dor']}; }} .w-nom {{ width: {w['nom']}; text-align: left; padding-left: 10px; }}
            .w-prov {{ width: {w['prov']}; }} .w-cat {{ width: {w['cat']}; }} .w-sub {{ width: {w['sub']}; }} .w-s {{ width: {w['s']}; }} .w-tot {{ width: {w['tot']}; }}
            thead tr {{ background: #1f4e78; color: white; font-size: 13px; }}
            .oro {{ background: #fff9c4; font-weight: bold; border-left: 4px solid #ffd700; }}
            .plata {{ background: #f5f5f5; font-weight: bold; border-left: 4px solid #c0c0c0; }}
            .bronce {{ background: #efebe9; font-weight: bold; border-left: 4px solid #cd7f32; }}
            .total-red {{ color: #d32f2f; font-weight: 900; font-size: 16px; }}
            .scroll-window {{ height: 500px; overflow: hidden; border: 1px solid #ddd; border-top: none; }}
        </style>
        """

        html = style + "<table><thead><tr>"
        html += "<th class='w-pos'>Pos</th><th class='w-dor'>Dor</th><th class='w-nom'>Nombre y Apellidos</th>"
        html += "<th class='w-prov'>Prov</th><th class='w-cat'>Cat</th><th class='w-sub'>Sub</th>"
        html += "<th class='w-s'>S1</th><th class='w-s'>S2</th><th class='w-s'>S3</th><th class='w-s'>S4</th>"
        html += "<th class='w-tot'>Total</th></tr></thead><tbody>"

        for i, row in p.iterrows():
            cls = ["oro", "plata", "bronce"][i] if i < 3 else ""
            html += f"<tr class='{cls}'>"
            html += f"<td>{i+1}º</td><td>{row['DORSAL']}</td><td>{row['NOMBRE Y APELLIDOS']}</td>"
            html += f"<td>{row['PROV']}</td><td>{row['CAT. FU']}</td><td>{row['SUBC']}</td>"
            html += f"<td>{row['S-1']}</td><td>{row['S-2']}</td><td>{row['S-3']}</td><td>{row['S-4']}</td>"
            html += f"<td class='total-red'>{row['TOTAL']}</td></tr>"
        
        html += "</tbody></table><div class='scroll-window' id='sc'><table><tbody>"
        
        for i, row in enumerate(r.values):
            bg = "#ffffff" if i % 2 == 0 else "#f9f9f9"
            html += f"<tr style='background:{bg};'>"
            html += f"<td class='w-pos'>{i+4}º</td><td class='w-dor'>{row[2]}</td><td class='w-nom'>{row[4]}</td>"
            html += f"<td class='w-prov'>{row[6]}</td><td class='w-cat'>{row[8]}</td><td class='w-sub'>{row[9]}</td>"
            html += f"<td class='w-s'>{row[10]}</td><td class='w-s'>{row[11]}</td><td class='w-s'>{row[12]}</td><td class='w-s'>{row[13]}</td>"
            html += f"<td class='w-tot' style='font-weight:bold;'>{row[14]}</td></tr>"

        html += "</tbody></table></div>"
        html += """<script>
            var e = document.getElementById('sc');
            var stop = false;
            function sc() { if(!stop) { e.scrollTop += 1; if(e.scrollTop >= (e.scrollHeight-e.clientHeight)) e.scrollTop=0; } }
            setInterval(sc, 80);
            e.onmouseover = () => stop=true; e.onmouseout = () => stop=false;
        </script>"""
        return html

    components.html(draw_table(podio, resto), height=850)

except Exception as e:
    st.error(f"Error: {e}")
