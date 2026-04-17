import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os

# ==========================================
# CONFIGURACIÓN PERSONALIZABLE
# ==========================================
TITULO_TIRADA = "1ª TIRADA AÑO 2026 - MARCADOR OFICIAL"
# ==========================================

st.set_page_config(page_title="Marcador Profesional FU", layout="wide")

# Estilos CSS de Alta Precisión
st.markdown(f"""
    <style>
    .stApp {{ background-color: #fdfaf6; }}
    .block-container {{ max-width: 1200px; padding-top: 1rem; margin: auto; }}
    
    /* Cabecera */
    .header-box {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        margin-bottom: 15px;
    }}
    .header-text {{
        flex: 1;
        text-align: center;
        font-size: clamp(18px, 4vw, 30px);
        font-weight: 900;
        color: #1a365d;
        text-transform: uppercase;
    }}

    /* Ajuste de Toggles */
    div[data-testid="stMarkdownContainer"] p {{
        font-size: 13px !important;
        font-weight: bold;
        white-space: nowrap;
    }}
    </style>
""", unsafe_allow_html=True)

# 1. CABECERA
logo_izq = "logo_izquierdo.png" if os.path.exists("logo_izquierdo.png") else ""
logo_der = "logo_derecho.png" if os.path.exists("logo_derecho.png") else ""

st.markdown(f"""
    <div class="header-box">
        <div class="logo-frame">{"<img src='app/static/"+logo_izq+"' style='max-height:70px'>" if logo_izq else ""}</div>
        <div class="header-text">{TITULO_TIRADA}</div>
        <div class="logo-frame">{"<img src='app/static/"+logo_der+"' style='max-height:70px'>" if logo_der else ""}</div>
    </div>
""", unsafe_allow_html=True)

# 2. PROCESAMIENTO DE DATOS
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

    # 3. FILTROS MULTI-SELECCIÓN
    st.write("🎯 **FILTROS DE COMPETICIÓN** (Activa varios para combinar)")
    t_cols = st.columns(9)
    selec_cats, selec_subs = [], []

    c_map = {"1ª CAT": 1, "2ª CAT": 2, "3ª CAT": 3, "4ª CAT": 4}
    s_map = {"SENIOR": "SR", "DAMAS": "DM", "JUNIOR": "JR", "VET.": "VET"}

    for i, (lab, val) in enumerate(c_map.items()):
        with t_cols[i]:
            if st.toggle(lab, key=f"c_{val}"): selec_cats.append(val)
    for i, (lab, val) in enumerate(s_map.items()):
        with t_cols[i+5]:
            if st.toggle(lab, key=f"s_{val}"): selec_subs.append(val)

    df_f = df_sorted.copy()
    if selec_cats: df_f = df_f[df_f["CAT. FU"].isin(selec_cats)]
    if selec_subs: df_f = df_f[df_f["SUBC"].isin(selec_subs)]
    
    df_f = df_f.reset_index(drop=True)
    podio = df_f.head(3)
    resto = df_f.iloc[3:]

    # 4. TABLA HTML CON RESALTADO DE COLOR
    def build_table(p, r):
        # Función interna para el color de las series
        def get_s_style(val):
            if val == 25: return "style='color:#d32f2f; font-weight:900;'" # Rojo para pleno
            if val == 24: return "style='color:#2e7d32; font-weight:900;'" # Verde para 24
            return "style='color:#666;'"

        # Reparto exacto de anchos
        w = {"pos":"6%", "dor":"6%", "nom":"30%", "cat":"7%", "sub":"7%", "s":"6%", "tot":"10%"}
        
        style = f"""
        <style>
            .tab {{ width: 100%; border-collapse: collapse; table-layout: fixed; background: #fff; font-family: sans-serif; }}
            th, td {{ padding: 12px 2px; text-align: center; font-size: 16px; border-bottom: 1px solid #eee; overflow: hidden; white-space: nowrap; box-sizing: border-box; }}
            .w-pos {{ width: {w['pos']}; }} .w-dor {{ width: {w['dor']}; }} 
            .w-nom {{ width: {w['nom']}; text-align: left; padding-left: 12px; font-weight: bold; }}
            .w-cat {{ width: {w['cat']}; }} .w-sub {{ width: {w['sub']}; }} 
            .w-s {{ width: {w['s']}; font-size: 15px; }}
            .w-tot {{ width: {w['tot']}; }}
            thead tr {{ background: #1a365d; color: white; font-size: 14px; }}
            
            /* Alineación: Borde de 8px en todas las filas */
            .oro {{ background: #fff9c4 !important; border-left: 8px solid #ffd700; }}
            .plata {{ background: #f5f5f5 !important; border-left: 8px solid #c0c0c0; }}
            .bronce {{ background: #efebe9 !important; border-left: 8px solid #cd7f32; }}
            .normal {{ border-left: 8px solid transparent; }}
            
            .t-red {{ color: #d32f2f; font-weight: 900; font-size: 22px; }}
            .win {{ height: 850px; overflow: hidden; border: 1px solid #ddd; border-top: none; }}
            
            @media (max-width: 600px) {{
                td {{ font-size: 13px; padding: 10px 1px; }}
                .w-nom {{ padding-left: 5px; }}
                .t-red {{ font-size: 18px; }}
            }}
        </style>
        """

        html = style + "<table class='tab'><thead><tr>"
        html += "<th class='w-pos'>Pos</th><th class='w-dor'>Dor</th><th class='w-nom'>Nombre</th>"
        html += "<th class='w-cat'>Cat</th><th class='w-sub'>Sub</th>"
        html += "<th class='w-s'>S1</th><th class='w-s'>S2</th><th class='w-s'>S3</th><th class='w-s'>S4</th>"
        html += "<th class='w-tot'>TOT</th></tr></thead><tbody>"

        # Podio
        for i, row in p.iterrows():
            cls = ["oro", "plata", "bronce"][i]
            html += f"<tr class='{cls}'>"
            html += f"<td class='w-pos'>{i+1}º</td><td class='w-dor'>{row['DORSAL']}</td><td class='w-nom'>{row['NOMBRE Y APELLIDOS']}</td>"
            html += f"<td class='w-cat'>{row['CAT. FU']}</td><td class='w-sub'>{row['SUBC']}</td>"
            html += f"<td class='w-s' {get_s_style(row['S-1'])}>{row['S-1']}</td>"
            html += f"<td class='w-s' {get_s_style(row['S-2'])}>{row['S-2']}</td>"
            html += f"<td class='w-s' {get_s_style(row['S-3'])}>{row['S-3']}</td>"
            html += f"<td class='w-s' {get_s_style(row['S-4'])}>{row['S-4']}</td>"
            html += f"<td class='w-tot t-red'>{row['TOTAL']}</td></tr>"
        
        html += "</tbody></table>"
        html += "<div class='win' id='scrol'><table class='tab'><tbody>"
        
        # Resto con scroll
        for i, row in enumerate(r.values):
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            html += f"<tr class='normal' style='background:{bg};'>"
            html += f"<td class='w-pos'>{i+4}º</td><td class='w-dor'>{row[2]}</td><td class='w-nom'>{row[4]}</td>"
            html += f"<td class='w-cat'>{row[8]}</td><td class='w-sub'>{row[9]}</td>"
            html += f"<td class='w-s' {get_s_style(row[10])}>{row[10]}</td>"
            html += f"<td class='w-s' {get_s_style(row[11])}>{row[11]}</td>"
            html += f"<td class='w-s' {get_s_style(row[12])}>{row[12]}</td>"
            html += f"<td class='w-s' {get_s_style(row[13])}>{row[13]}</td>"
            html += f"<td class='w-tot' style='font-weight:bold; font-size:18px;'>{row[14]}</td></tr>"

        html += "</tbody></table></div>"
        html += """<script>
            var d = document.getElementById('scrol');
            var p = false;
            function f() { if(!p) { d.scrollTop += 1; if(d.scrollTop >= (d.scrollHeight - d.clientHeight)) d.scrollTop = 0; } }
            setInterval(f, 85);
            d.onmouseover = () => p = true; d.onmouseout = () => p = false;
        </script>"""
        return html

    components.html(build_table(podio, resto), height=1100)

except Exception as e:
    st.error(f"Error técnico: {e}")
