import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Resultados Tiro al Plato", layout="wide")

# Estilos CSS Profesionales
st.markdown("""
    <style>
    /* Botones de Categorías y Subcategorías */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
        font-size: 16px !important;
        background-color: #f1f3f5;
        border: 1px solid #ced4da;
    }
    /* Estilo para destacar el filtro activo */
    .stButton > button:active, .stButton > button:focus {
        background-color: #1f4e78 !important;
        color: white !important;
    }
    /* Contenedor principal para centrar la tabla en TV */
    .reportview-container .main .block-container {
        max-width: 1000px;
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. PROCESAMIENTO DE DATOS (Basado en tu Excel real)
try:
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Limpiar datos numéricos (Sin decimales)
    cols_entero = ["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL", "CAT. FU"]
    for col in cols_entero:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Ordenación por reglamento
    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)

    # 3. INTERFAZ DE FILTROS
    if 'cat_f' not in st.session_state: st.session_state.cat_f = "GENERAL"
    if 'sub_f' not in st.session_state: st.session_state.sub_f = "TODAS"

    st.write("### 🏆 CATEGORÍAS")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("GENERAL"): st.session_state.cat_f = "GENERAL"
    with c2: 
        if st.button("1ª CAT"): st.session_state.cat_f = 1
    with c3: 
        if st.button("2ª CAT"): st.session_state.cat_f = 2
    with c4: 
        if st.button("3ª CAT"): st.session_state.cat_f = 3
    with c5: 
        if st.button("4ª CAT"): st.session_state.cat_f = 4

    st.write("#### 👥 SUBCATEGORÍAS")
    s1, s2, s3, s4, s5 = st.columns(5)
    # Mapeo exacto según tu Excel: SR, DAM, JR, VET
    with s1: 
        if st.button("TODAS"): st.session_state.sub_f = "TODAS"
    with s2: 
        if st.button("SENIOR"): st.session_state.sub_f = "SR"
    with s3: 
        if st.button("DAMAS"): st.session_state.sub_f = "DM"
    with s4: 
        if st.button("JUNIOR"): st.session_state.sub_f = "JR"
    with s5: 
        if st.button("VETERANO"): st.session_state.sub_f = "VET"

    # Filtrado
    df_final = df_sorted.copy()
    if st.session_state.cat_f != "GENERAL":
        df_final = df_final[df_final["CAT. FU"] == st.session_state.cat_f]
    if st.session_state.sub_f != "TODAS":
        df_final = df_final[df_final["SUBC"] == st.session_state.sub_f]

    # 4. TABLA CONSTRUIDA A MEDIDA (HTML/JS)
    podio = df_final.head(3)
    resto = df_final.iloc[3:]

    def render_tv_table(p, r):
        # Definición de anchos fijos para alineación perfecta
        # Pos(50) + Dor(50) + Nom(300) + Cat(50) + Sub(50) + S1-4(40x4) + Tot(60) = 720px total aprox.
        
        style = """
        <style>
            .main-table { width: 900px; margin: auto; border-collapse: collapse; font-family: Arial, sans-serif; table-layout: fixed; }
            th, td { padding: 10px 5px; text-align: center; border-bottom: 1px solid #eee; font-size: 17px; }
            .col-pos { width: 50px; } .col-dor { width: 50px; } .col-nom { width: 320px; text-align: left; }
            .col-cat { width: 60px; } .col-sub { width: 60px; } .col-s { width: 45px; } .col-tot { width: 65px; }
            
            thead tr { background-color: #1f4e78; color: white; }
            .row-podio { font-weight: bold; background-color: #f8f9fa; }
            .oro { background-color: rgba(255, 215, 0, 0.2); }
            .plata { background-color: rgba(192, 192, 192, 0.2); }
            .bronce { background-color: rgba(205, 127, 50, 0.2); }
            
            .scroll-window { width: 900px; margin: auto; height: 600px; overflow: hidden; border: 1px solid #ddd; }
            .total-bold { font-weight: bold; color: #d9534f; font-size: 19px; }
        </style>
        """

        # Cabecera
        html = style + "<table class='main-table'><thead><tr>"
        html += "<th class='col-pos'>Pos</th><th class='col-dor'>Dor</th><th class='col-nom'>Tirador</th>"
        html += "<th class='col-cat'>Cat</th><th class='col-sub'>Sub</th>"
        html += "<th class='col-s'>S1</th><th class='col-s'>S2</th><th class='col-s'>S3</th><th class='col-s'>S4</th>"
        html += "<th class='col-tot'>Tot</th></tr></thead><tbody>"

        # Filas del Podio
        podio_colors = ["oro", "plata", "bronce"]
        for i, row in p.iterrows():
            cls = podio_colors[i] if i < 3 else ""
            html += f"<tr class='row-podio {cls}'>"
            html += f"<td class='col-pos'>{i+1}º</td><td class='col-dor'>{row['DORSAL']}</td><td class='col-nom'>{row['NOMBRE Y APELLIDOS']}</td>"
            html += f"<td class='col-cat'>{row['CAT. FU']}</td><td class='col-sub'>{row['SUBC']}</td>"
            html += f"<td class='col-s'>{row['S-1']}</td><td class='col-s'>{row['S-2']}</td><td class='col-s'>{row['S-3']}</td><td class='col-s'>{row['S-4']}</td>"
            html += f"<td class='col-tot total-bold'>{row['TOTAL']}</td></tr>"
        html += "</tbody></table>"

        # Ventana de Scroll
        html += "<div class='scroll-window' id='win'><table class='main-table'><tbody>"
        for i, row in enumerate(r.values):
            html += "<tr>"
            html += f"<td class='col-pos'>{i+4}º</td><td class='col-dor'>{row[2]}</td><td class='col-nom'>{row[4]}</td>"
            html += f"<td class='col-cat'>{row[8]}</td><td class='col-sub'>{row[9]}</td>"
            html += f"<td class='col-s'>{row[10]}</td><td class='col-s'>{row[11]}</td><td class='col-s'>{row[12]}</td><td class='col-s'>{row[13]}</td>"
            html += f"<td class='col-tot' style='font-weight:bold;'>{row[14]}</td></tr>"
        html += "</tbody></table></div>"

        # JavaScript para Scroll Lento (60ms)
        html += """
        <script>
            var w = document.getElementById('win');
            var p = false;
            function scroll() {
                if(!p) {
                    w.scrollTop += 1;
                    if(w.scrollTop >= (w.scrollHeight - w.clientHeight)) { w.scrollTop = 0; }
                }
            }
            setInterval(scroll, 60);
            w.onmouseover = function() { p = true; };
            w.onmouseout = function() { p = false; };
        </script>
        """
        return html

    components.html(render_tv_table(podio, resto), height=850)

except Exception as e:
    st.error(f"Error detectado: {e}")
