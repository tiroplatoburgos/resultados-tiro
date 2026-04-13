import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os

# --- CONFIGURACIÓN PERSONALIZABLE ---
TITULO_TIRADA = "NOMBRE DE TU GRAN TIRADA 2026"
# ------------------------------------

st.set_page_config(page_title="Marcador Profesional de Tiro", layout="wide")

# Estilos CSS para Cabecera y Botones
st.markdown(f"""
    <style>
    .stApp {{ background-color: #fdfaf6; }}
    .block-container {{ max-width: 1100px; padding-top: 1rem; margin: auto; }}
    
    /* Cabecera Profesional */
    .header-container {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }}
    .header-title {{
        flex-grow: 1;
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        color: #1a365d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .logo-img {{ height: 80px; width: auto; object-fit: contain; }}

    /* Botones Compactos en Fila */
    div.stButton > button {{
        width: 100%;
        height: 38px;
        font-size: 13px !important;
        border-radius: 6px;
        border: 1px solid #cbd5e1;
        transition: 0.3s;
    }}
    </style>
""", unsafe_allow_html=True)

# 3. RENDERIZADO DE CABECERA (LOGOS + TITULO)
col_l, col_t, col_r = st.columns([1, 4, 1])

with col_l:
    if os.path.exists("logo_izquierdo.png"):
        st.image("logo_izquierdo.png")
with col_t:
    st.markdown(f"<div class='header-title'>{TITULO_TIRADA}</div>", unsafe_allow_html=True)
with col_r:
    if os.path.exists("logo_derecho.png"):
        st.image("logo_derecho.png")

# 4. PROCESAMIENTO DE DATOS
try:
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Conversión limpia a números
    for col in ["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL", "CAT. FU"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)

    # FILTROS EN UNA SOLA FILA
    if 'cat_f' not in st.session_state: st.session_state.cat_f = "GENERAL"
    if 'sub_f' not in st.session_state: st.session_state.sub_f = None

    # Creamos 9 columnas para los 9 botones (General + 4 Cats + 4 Subs)
    btn_cols = st.columns(9)
    
    # Botón General
    with btn_cols[0]:
        if st.button("GENERAL", type="primary" if st.session_state.cat_f == "GENERAL" else "secondary"):
            st.session_state.cat_f = "GENERAL"; st.session_state.sub_f = None

    # Categorías
    cats_map = {"1ª CAT": 1, "2ª CAT": 2, "3ª CAT": 3, "4ª CAT": 4}
    for i, (label, val) in enumerate(cats_map.items()):
        with btn_cols[i+1]:
            if st.button(label, type="primary" if st.session_state.cat_f == val else "secondary"):
                st.session_state.cat_f = "GENERAL" if st.session_state.cat_f == val else val

    # Subcategorías
    subs_map = {"SENIOR": "SR", "DAMAS": "DM", "JUNIOR": "JR", "VET.": "VET"}
    for i, (label, val) in enumerate(subs_map.items()):
        with btn_cols[i+5]:
            if st.button(label, type="primary" if st.session_state.sub_f == val else "secondary"):
                st.session_state.sub_f = None if st.session_state.sub_f == val else val

    # Aplicar filtros y resetear índice para el Podio
    df_f = df_sorted.copy()
    if st.session_state.cat_f != "GENERAL":
        df_f = df_f[df_f["CAT. FU"] == st.session_state.cat_f]
    if st.session_state.sub_f:
        df_f = df_f[df_f["SUBC"] == st.session_state.sub_f]
    
    df_f = df_f.reset_index(drop=True)
    podio = df_f.head(3)
    resto = df_f.iloc[3:]

    # 5. TABLA DEFINITIVA CON ALINEACIÓN MILIMÉTRICA
    def generate_html(p, r):
        # Definimos los anchos una sola vez para que ambas tablas coincidan
        w = {"pos":"6%", "dor":"6%", "nom":"26%", "prov":"12%", "cat":"8%", "sub":"8%", "s":"6%", "tot":"10%"}
        
        style = f"""
        <style>
            table {{ width: 100%; border-collapse: collapse; table-layout: fixed; font-family: sans-serif; background: #fff; }}
            th, td {{ padding: 12px 2px; text-align: center; font-size: 14px; border-bottom: 1px solid #eee; overflow: hidden; white-space: nowrap; }}
            .w-pos {{ width: {w['pos']}; }} .w-dor {{ width: {w['dor']}; }} .w-nom {{ width: {w['nom']}; text-align: left; padding-left: 10px; }}
            .w-prov {{ width: {w['prov']}; }} .w-cat {{ width: {w['cat']}; }} .w-sub {{ width: {w['sub']}; }} .w-s {{ width: {w['s']}; }} .w-tot {{ width: {w['tot']}; }}
            
            thead tr {{ background: #1f4e78; color: white; font-size: 13px; }}
            .oro {{ background: #fff9c4; font-weight: bold; border-left: 5px solid #ffd700; }}
            .plata {{ background: #f5f5f5; font-weight: bold; border-left: 5px solid #c0c0c0; }}
            .bronce {{ background: #efebe9; font-weight: bold; border-left: 5px solid #cd7f32; }}
            .z1 {{ background: #ffffff; }} .z2 {{ background: #f9f9f9; }}
            .total-val {{ font-weight: 900; color: #d32f2f; font-size: 17px; }}
            .scroll-window {{ height: 500px; overflow: hidden; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px; }}
        </style>
        """

        header = f"""
        {style}
        <table>
            <thead>
                <tr>
                    <th class="w-pos">Pos</th><th class="w-dor">Dor</th><th class="w-nom">Nombre y Apellidos</th>
                    <th class="w-prov">Prov</th><th class="w-cat">Cat</th><th class="w-sub">Sub</th>
                    <th class="w-s">S1</th><th class="w-s">S2</th><th class="w-s">S3</th><th class="w-s">S4</th>
                    <th class="w-tot">Total</th>
                </tr>
            </thead>
            <tbody>"""
        
        p_html = ""
        colors = ["oro", "plata", "bronce"]
        for i, row in p.iterrows():
            c = colors[i] if i < 3 else ""
            p_html += f"<tr class='{c}'>"
            p_html += f"<td>{i+1}º</td><td>{row['DORSAL']}</td><td>{row['NOMBRE Y APELLIDOS']}</td>"
            p_html += f"<td>{row['PROV']}</td><td>{row['CAT. FU']}</td><td>{row['SUBC']}</td>"
            p_html += f"<td>{row['S-1']}</td><td>{row['S-2']}</td><td>{row['S-3']}</td><td>{row['S-4']}</td>"
            p_html += f"<td class='total-val'>{row['TOTAL']}</td></tr>"
        
        r_html = ""
        for i, row in enumerate(r.values):
            z = "z1" if i % 2 == 0 else "z2"
            r_html += f"<tr class='{z}'>"
            r_html += f"<td class='w-pos'>{i+4}º</td><td class='w-dor'>{row[2]}</td><td class='w-nom'>{row[4]}</td>"
            r_html += f"<td class='w-prov'>{row[6]}</td><td class="w-cat">{row[8]}</td><td class="w-sub">{row[9]}</td>"
            r_html += f"<td class='w-s'>{row[10]}</td><td class='w-s'>{row[11]}</td><td class='w-s'>{row[12]}</td><td class='w-s'>{row[13]}</td>"
            r_html += f"<td class='w-tot' style='font-weight:bold;'>{row[14]}</td></tr>"

        return header + p_html + "</tbody></table><div class='scroll-window' id='sc'><table><tbody>" + r_html + "</tbody></table></div>" + """
        <script>
            var el = document.getElementById('sc');
            var p = false;
            function run() { if(!p) { el.scrollTop += 1; if(el.scrollTop >= (el.scrollHeight - el.clientHeight)) el.scrollTop = 0; } }
            setInterval(run, 80);
            el.onmouseover = () => p = true; el.onmouseout = () => p = false;
        </script>"""

    components.html(generate_html(podio, resto), height=900)

except Exception as e:
    st.error(f"Error: {e}")
