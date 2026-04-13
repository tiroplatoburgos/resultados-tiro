import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os

# ==========================================
# CONFIGURACIÓN PERSONALIZABLE
# ==========================================
TITULO_TIRADA = "1ª TIRADA AÑO 2026 - MARCADOR OFICIAL"
# ==========================================

st.set_page_config(page_title="Marcador Profesional de Tiro", layout="wide")

# Estilos CSS de Alta Precisión
st.markdown(f"""
    <style>
    .stApp {{ background-color: #fdfaf6; }}
    .block-container {{ max-width: 1200px; padding-top: 1rem; margin: auto; }}
    
    /* Cabecera Profesional Multi-dispositivo */
    .header-box {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }}
    .header-text {{
        flex: 1;
        text-align: center;
        font-size: clamp(20px, 5vw, 32px);
        font-weight: 800;
        color: #1a365d;
        text-transform: uppercase;
        margin: 0 20px;
    }}
    .logo-frame {{ width: 120px; display: flex; justify-content: center; }}
    .logo-frame img {{ max-height: 90px; width: auto; }}

    /* Botones de Control */
    div.stButton > button {{
        width: 100%;
        height: 40px;
        font-size: 13px !important;
        font-weight: bold;
        border-radius: 8px;
        transition: 0.2s;
    }}
    </style>
""", unsafe_allow_html=True)

# 1. RENDERIZADO DE CABECERA (LOGOS Y TITULO)
# Intentamos cargar los logos si existen en el repositorio
logo_izq = "app/static/logo_izquierdo.png" if os.path.exists("logo_izquierdo.png") else ""
logo_der = "app/static/logo_derecho.png" if os.path.exists("logo_derecho.png") else ""

st.markdown(f"""
    <div class="header-box">
        <div class="logo-frame">{"<img src='"+logo_izq+"'>" if logo_izq else ""}</div>
        <div class="header-text">{TITULO_TIRADA}</div>
        <div class="logo-frame">{"<img src='"+logo_der+"'>" if logo_der else ""}</div>
    </div>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS DESDE EL EXCEL
try:
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Limpieza de columnas numéricas
    for col in ["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL", "CAT. FU"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Ordenación por reglamento
    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)

    # 3. FILTROS DINÁMICOS (Botones en fila)
    if 'cat_f' not in st.session_state: st.session_state.cat_f = "GENERAL"
    if 'sub_f' not in st.session_state: st.session_state.sub_f = None

    btn_cols = st.columns(9)
    with btn_cols[0]:
        if st.button("GENERAL", type="primary" if st.session_state.cat_f == "GENERAL" else "secondary"):
            st.session_state.cat_f = "GENERAL"; st.session_state.sub_f = None
    
    c_list = {"1ª CAT": 1, "2ª CAT": 2, "3ª CAT": 3, "4ª CAT": 4}
    for i, (l, v) in enumerate(c_list.items()):
        with btn_cols[i+1]:
            if st.button(l, type="primary" if st.session_state.cat_f == v else "secondary"):
                st.session_state.cat_f = "GENERAL" if st.session_state.cat_f == v else v

    s_list = {"SENIOR": "SR", "DAMAS": "DM", "JUNIOR": "JR", "VET.": "VET"}
    for i, (l, v) in enumerate(s_list.items()):
        with btn_cols[i+5]:
            if st.button(l, type="primary" if st.session_state.sub_f == v else "secondary"):
                st.session_state.sub_f = None if st.session_state.sub_f == v else v

    # Aplicar filtrado
    df_f = df_sorted.copy()
    if st.session_state.cat_f != "GENERAL":
        df_f = df_f[df_f["CAT. FU"] == st.session_state.cat_f]
    if st.session_state.sub_f:
        df_f = df_f[df_f["SUBC"] == st.session_state.sub_f]
    
    df_f = df_f.reset_index(drop=True)
    podio = df_f.head(3)
    resto = df_f.iloc[3:]  # Quitamos el límite para que salgan TODOS en el scroll

    # 4. CONSTRUCCIÓN DEL MARCADOR HTML
    def build_scoreboard(p, r):
        # Definición de anchos (%) para alineación perfecta
        w = {"pos":"7%", "dor":"7%", "nom":"43%", "cat":"8%", "sub":"8%", "s":"6%", "tot":"9%"}
        
        style = f"""
        <style>
            .main-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; background: #fff; font-family: 'Segoe UI', sans-serif; }}
            th, td {{ padding: 14px 5px; text-align: center; font-size: 15px; border-bottom: 1px solid #eee; overflow: hidden; white-space: nowrap; }}
            
            /* Columnas con anchos fijos */
            .w-pos {{ width: {w['pos']}; }} .w-dor {{ width: {w['dor']}; }} 
            .w-nom {{ width: {w['nom']}; text-align: left; padding-left: 15px; }}
            .w-cat {{ width: {w['cat']}; }} .w-sub {{ width: {w['sub']}; }} 
            .w-s {{ width: {w['s']}; }} .w-tot {{ width: {w['tot']}; }}
            
            thead tr {{ background: #1a365d; color: white; font-size: 14px; text-transform: uppercase; }}
            
            /* Estilos de Podio (Borde izquierdo de color) */
            .oro {{ background: #fff9c4 !important; font-weight: bold; border-left: 6px solid #ffd700; }}
            .plata {{ background: #f5f5f5 !important; font-weight: bold; border-left: 6px solid #c0c0c0; }}
            .bronce {{ background: #efebe9 !important; font-weight: bold; border-left: 6px solid #cd7f32; }}
            
            /* Fila normal con borde transparente para alinear el texto con el podio */
            .fila-normal {{ border-left: 6px solid transparent; }}
            
            .val-total {{ font-weight: 900; color: #d32f2f; font-size: 18px; }}
            .scroll-container {{ height: 550px; overflow: hidden; border: 1px solid #ddd; border-top: none; border-radius: 0 0 12px 12px; }}
        </style>
        """

        # Cabecera y Podio
        html = style + "<table class='main-table'><thead><tr>"
        html += "<th class='w-pos'>Pos</th><th class='w-dor'>Dor</th><th class='w-nom'>Nombre y Apellidos</th>"
        html += "<th class='w-cat'>Cat</th><th class='w-sub'>Sub</th>"
        html += "<th class='w-s'>S1</th><th class='w-s'>S2</th><th class='w-s'>S3</th><th class='w-s'>S4</th>"
        html += "<th class='w-tot'>Total</th></tr></thead><tbody>"

        for i, row in p.iterrows():
            medal = ["oro", "plata", "bronce"][i]
            html += f"<tr class='{medal}'>"
            html += f"<td class='w-pos'>{i+1}º</td><td class='w-dor'>{row['DORSAL']}</td><td class='w-nom'>{row['NOMBRE Y APELLIDOS']}</td>"
            html += f"<td class='w-cat'>{row['CAT. FU']}</td><td class='w-sub'>{row['SUBC']}</td>"
            html += f"<td class='w-s'>{row['S-1']}</td><td class='w-s'>{row['S-2']}</td><td class='w-s'>{row['S-3']}</td><td class='w-s'>{row['S-4']}</td>"
            html += f"<td class='w-tot val-total'>{row['TOTAL']}</td></tr>"
        
        html += "</tbody></table>"

        # Ventana de Scroll con el resto de tiradores
        html += "<div class='scroll-container' id='marquee'><table class='main-table'><tbody>"
        for i, row in enumerate(r.values):
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            html += f"<tr class='fila-normal' style='background:{bg};'>"
            html += f"<td class='w-pos'>{i+4}º</td><td class='w-dor'>{row[2]}</td><td class='w-nom'>{row[4]}</td>"
            html += f"<td class='w-cat'>{row[8]}</td><td class='w-sub'>{row[9]}</td>"
            html += f"<td class='w-s'>{row[10]}</td><td class='w-s'>{row[11]}</td><td class='w-s'>{row[12]}</td><td class='w-s'>{row[13]}</td>"
            html += f"<td class='w-tot' style='font-weight:bold;'>{row[14]}</td></tr>"

        html += "</tbody></table></div>"

        # JavaScript para Scroll Infinito y Suave
        html += """
        <script>
            var box = document.getElementById('marquee');
            var isPaused = false;
            function scrollLoop() {
                if(!isPaused) {
                    box.scrollTop += 1;
                    if(box.scrollTop >= (box.scrollHeight - box.clientHeight)) {
                        box.scrollTop = 0;
                    }
                }
            }
            setInterval(scrollLoop, 80); // Velocidad equilibrada
            box.onmouseover = () => isPaused = true;
            box.onmouseout = () => isPaused = false;
        </script>
        """
        return html

    components.html(build_scoreboard(podio, resto), height=950)

except Exception as e:
    st.error(f"Error al cargar el marcador: {e}")
