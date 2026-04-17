import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os

# ==========================================
# CONFIGURACIÓN PERSONALIZABLE
# ==========================================
TITULO_TIRADA = "1ª TIRADA AÑO 2026 - MARCADOR OFICIAL"
# ==========================================

st.set_page_config(page_title="Marcador Profesional", layout="wide")

# Estilos CSS de Alta Visibilidad
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
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        margin-bottom: 20px;
    }}
    .header-text {{
        flex: 1;
        text-align: center;
        font-size: clamp(22px, 5vw, 34px);
        font-weight: 850;
        color: #1a365d;
        text-transform: uppercase;
    }}
    .logo-frame img {{ max-height: 90px; width: auto; }}

    /* Estilo para los Interruptores (Toggles) */
    .stToggle {{
        background: #f1f5f9;
        padding: 5px 10px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }}
    </style>
""", unsafe_allow_html=True)

# 1. RENDERIZADO DE CABECERA
logo_izq = "logo_izquierdo.png" if os.path.exists("logo_izquierdo.png") else ""
logo_der = "logo_derecho.png" if os.path.exists("logo_derecho.png") else ""

st.markdown(f"""
    <div class="header-box">
        <div class="logo-frame">{"<img src='app/static/"+logo_izq+"'>" if logo_izq else ""}</div>
        <div class="header-text">{TITULO_TIRADA}</div>
        <div class="logo-frame">{"<img src='app/static/"+logo_der+"'>" if logo_der else ""}</div>
    </div>
""", unsafe_allow_html=True)

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

    # 3. FILTROS MULTIPLE (INTERRUPTORES)
    # Organizamos en una fila compacta
    st.write("🔧 **FILTROS COMBINADOS** (Activa varios para sumar categorías)")
    
    t_cols = st.columns(9)
    selec_cats = []
    selec_subs = []

    c_map = {"1ª CAT": 1, "2ª CAT": 2, "3ª CAT": 3, "4ª CAT": 4}
    s_map = {"SENIOR": "SR", "DAMAS": "DM", "JUNIOR": "JR", "VET.": "VET"}

    # Toggles de Categoría
    for i, (lab, val) in enumerate(c_map.items()):
        with t_cols[i]:
            if st.toggle(lab, key=f"t_c_{val}"):
                selec_cats.append(val)

    # Toggles de Subcategoría
    for i, (lab, val) in enumerate(s_map.items()):
        with t_cols[i+4]:
            if st.toggle(lab, key=f"t_s_{val}"):
                selec_subs.append(val)

    # Lógica de filtrado dinámico
    df_f = df_sorted.copy()
    if selec_cats:
        df_f = df_f[df_f["CAT. FU"].isin(selec_cats)]
    if selec_subs:
        df_f = df_f[df_f["SUBC"].isin(selec_subs)]
    
    df_f = df_f.reset_index(drop=True)
    podio = df_f.head(3)
    resto = df_f.iloc[3:]

    # 4. TABLA HTML REFORZADA
    def draw_table(p, r):
        # Anchos y fuentes más grandes para móvil
        w = {"pos":"8%", "dor":"8%", "nom":"42%", "cat":"10%", "sub":"10%", "s":"0%", "tot":"12%"}
        
        style = f"""
        <style>
            .main-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; background: #fff; }}
            th, td {{ padding: 16px 4px; text-align: center; font-size: 16px; border-bottom: 1px solid #eee; overflow: hidden; white-space: nowrap; font-family: sans-serif; }}
            
            .w-pos {{ width: {w['pos']}; }} .w-dor {{ width: {w['dor']}; }} 
            .w-nom {{ width: {w['nom']}; text-align: left; padding-left: 15px; font-weight: 600; }}
            .w-cat {{ width: {w['cat']}; }} .w-sub {{ width: {w['sub']}; }} 
            .w-tot {{ width: {w['tot']}; }}
            
            thead tr {{ background: #1a365d; color: white; font-size: 14px; }}
            
            /* Podio con fuentes extra grandes */
            .oro {{ background: #fff9c4 !important; border-left: 8px solid #ffd700; font-size: 18px !important; }}
            .plata {{ background: #f5f5f5 !important; border-left: 8px solid #c0c0c0; font-size: 18px !important; }}
            .bronce {{ background: #efebe9 !important; border-left: 8px solid #cd7f32; font-size: 18px !important; }}
            
            .fila-normal {{ border-left: 8px solid transparent; }}
            .val-total {{ font-weight: 900; color: #d32f2f; font-size: 22px; }}
            
            /* Altura para mostrar ~25 tiradores */
            .scroll-window {{ height: 850px; overflow: hidden; border: 1px solid #ddd; border-top: none; }}
            
            @media (max-width: 600px) {{
                td {{ font-size: 14px; padding: 12px 2px; }}
                .val-total {{ font-size: 18px; }}
            }}
        </style>
        """

        html = style + "<table class='main-table'><thead><tr>"
        html += "<th class='w-pos'>Pos</th><th class='w-dor'>Dor</th><th class='w-nom'>Nombre y Apellidos</th>"
        html += "<th class='w-cat'>Cat</th><th class='w-sub'>Sub</th>"
        html += "<th class='w-tot'>Total</th></tr></thead><tbody>"

        for i, row in p.iterrows():
            medal = ["oro", "plata", "bronce"][i]
            html += f"<tr class='{medal}'>"
            html += f"<td>{i+1}º</td><td>{row['DORSAL']}</td><td>{row['NOMBRE Y APELLIDOS']}</td>"
            html += f"<td>{row['CAT. FU']}</td><td>{row['SUBC']}</td>"
            html += f"<td class='val-total'>{row['TOTAL']}</td></tr>"
        
        html += "</tbody></table>"
        html += "<div class='scroll-window' id='scr'><table class='main-table'><tbody>"
        
        for i, row in enumerate(r.values):
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            html += f"<tr class='fila-normal' style='background:{bg};'>"
            html += f"<td class='w-pos'>{i+4}º</td><td class='w-dor'>{row[2]}</td><td class='w-nom'>{row[4]}</td>"
            html += f"<td class='w-cat'>{row[8]}</td><td class='w-sub'>{row[9]}</td>"
            html += f"<td class='w-tot' style='font-weight:bold; font-size:18px;'>{row[14]}</td></tr>"

        html += "</tbody></table></div>"
        html += """<script>
            var b = document.getElementById('scr');
            var p = false;
            function run() { if(!p) { b.scrollTop += 1; if(b.scrollTop >= (b.scrollHeight - b.clientHeight)) b.scrollTop = 0; } }
            setInterval(run, 80);
            b.onmouseover = () => p = true; b.onmouseout = () => p = false;
        </script>"""
        return html

    components.html(draw_table(podio, resto), height=1100)

except Exception as e:
    st.error(f"Error técnico: {e}")
