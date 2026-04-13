import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA Y ESTÉTICA VISUAL (FONDO CÁLIDO)
st.set_page_config(page_title="Resultados Tiro Pro", layout="wide")

st.markdown("""
    <style>
    /* Fondo de la pantalla (Tono cálido suave) */
    .stApp {
        background-color: #fdfaf6;
    }
    
    /* Centrar contenedores */
    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        margin: auto;
    }

    /* Estilo de botones uniformes */
    div.stButton > button {
        width: 100%;
        height: 50px;
        border-radius: 10px;
        font-size: 16px !important;
        font-weight: bold;
        border: 1px solid #d1d5db;
        transition: all 0.3s;
    }
    
    /* Títulos centrados */
    h3, h4 {
        text-align: center;
        color: #1f4e78;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA Y PROCESAMIENTO DE DATOS
try:
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Limpieza de números
    cols_num = ["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL", "CAT. FU"]
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Ordenación por reglamento (Total -> S4 -> S3 -> S2 -> S1 -> Dorsal)
    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)

    # 3. LÓGICA DE BOTONES (TOGGLE)
    if 'cat_sel' not in st.session_state: st.session_state.cat_sel = "GENERAL"
    if 'sub_sel' not in st.session_state: st.session_state.sub_sel = None

    # --- BLOQUE CATEGORÍAS ---
    st.write("### 🏆 CATEGORÍAS")
    c_cols = st.columns(5)
    categorias = {
        "GENERAL": "GENERAL",
        "1ª CATEGORÍA": 1,
        "2ª CATEGORÍA": 2,
        "3ª CATEGORÍA": 3,
        "4ª CATEGORÍA": 4
    }

    for i, (label, val) in enumerate(categorias.items()):
        with c_cols[i]:
            # Si el botón es el seleccionado, lo ponemos en azul (primary)
            es_activo = (st.session_state.cat_sel == val)
            tipo = "primary" if es_activo else "secondary"
            if st.button(label, key=f"cat_{val}", type=tipo):
                # Si vuelvo a pulsar el activo, vuelvo a GENERAL
                st.session_state.cat_sel = "GENERAL" if es_activo else val

    # --- BLOQUE SUBCATEGORÍAS ---
    st.write("#### 👥 SUBCATEGORÍAS")
    s_cols = st.columns(4)
    subcategorias = {
        "SENIOR": "SR",
        "DAMAS": "DM",
        "JUNIOR": "JR",
        "VETERANO": "VET"
    }

    for i, (label, val) in enumerate(subcategorias.items()):
        with s_cols[i]:
            es_activo_sub = (st.session_state.sub_sel == val)
            tipo_sub = "primary" if es_activo_sub else "secondary"
            if st.button(label, key=f"sub_{val}", type=tipo_sub):
                # Si vuelvo a pulsar, desmarco (None)
                st.session_state.sub_sel = None if es_activo_sub else val

    # FILTRADO DINÁMICO
    df_f = df_sorted.copy()
    if st.session_state.cat_sel != "GENERAL":
        df_f = df_f[df_f["CAT. FU"] == st.session_state.cat_sel]
    if st.session_state.sub_sel:
        df_f = df_f[df_f["SUBC"] == st.session_state.sub_sel]

    # 4. RENDERIZADO DE TABLA (PODIO Y SCROLL)
    podio = df_f.head(3)
    resto = df_f.iloc[3:]

    def crear_tabla_html(p, r):
        # Configuración de anchos para alineación perfecta
        # Pos(40) | Dor(40) | Nombre(280) | Cat(60) | Sub(60) | S1-S4(35x4) | Tot(60)
        
        style = """
        <style>
            .tv-table { width: 850px; margin: auto; border-collapse: collapse; font-family: 'Segoe UI', sans-serif; table-layout: fixed; background: white; border-radius: 10px 10px 0 0; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            th, td { padding: 12px 5px; text-align: center; border-bottom: 1px solid #eee; }
            .col-pos { width: 45px; } .col-dor { width: 45px; } .col-nom { width: 280px; text-align: left; padding-left: 15px; }
            .col-cat { width: 60px; } .col-sub { width: 60px; } .col-s { width: 40px; } .col-tot { width: 65px; }
            
            thead tr { background-color: #1f4e78; color: white; font-size: 14px; }
            
            /* Colores del Podio (Se aplican siempre a los 3 primeros del filtro) */
            .oro { background-color: #fff9c4 !important; font-weight: bold; border-left: 5px solid #fbc02d; }
            .plata { background-color: #f5f5f5 !important; font-weight: bold; border-left: 5px solid #bdbdbd; }
            .bronce { background-color: #efebe9 !important; font-weight: bold; border-left: 5px solid #8d6e63; }
            
            /* Zebra Stripes para el resto */
            .zebra-1 { background-color: #ffffff; }
            .zebra-2 { background-color: #f8f9fa; }
            
            .scroll-area { width: 850px; margin: auto; height: 550px; overflow: hidden; border: 1px solid #ddd; border-top: none; background: white; border-radius: 0 0 10px 10px; }
            .tot-val { font-weight: bold; color: #d32f2f; font-size: 18px; }
        </style>
        """

        # Cabecera
        html = style + "<table class='tv-table'><thead><tr>"
        html += "<th class='col-pos'>Pos</th><th class='col-dor'>Dor</th><th class='col-nom'>Nombre y Apellidos</th>"
        html += "<th class='col-cat'>Cat</th><th class='col-sub'>Sub</th>"
        html += "<th class='col-s'>S1</th><th class='col-s'>S2</th><th class='col-s'>S3</th><th class='col-s'>S4</th>"
        html += "<th class='col-tot'>Tot</th></tr></thead><tbody>"

        # Filas Podio (Dinámico)
        medallas = ["oro", "plata", "bronce"]
        for i, row in p.iterrows():
            m_class = medallas[i] if i < len(p) else ""
            html += f"<tr class='{m_class}'>"
            html += f"<td class='col-pos'>{i+1}º</td><td class='col-dor'>{row['DORSAL']}</td><td class='col-nom'>{row['NOMBRE Y APELLIDOS']}</td>"
            html += f"<td class='col-cat'>{row['CAT. FU']}</td><td class='col-sub'>{row['SUBC']}</td>"
            html += f"<td>{row['S-1']}</td><td>{row['S-2']}</td><td>{row['S-3']}</td><td>{row['S-4']}</td>"
            html += f"<td class='col-tot tot-val'>{row['TOTAL']}</td></tr>"
        html += "</tbody></table>"

        # Área de Scroll (Cebra y lento)
        html += "<div class='scroll-area' id='scrollBox'><table class='tv-table' style='box-shadow:none; border-radius:0;'><tbody>"
        for i, row in enumerate(r.values):
            z_class = "zebra-1" if i % 2 == 0 else "zebra-2"
            html += f"<tr class='{z_class}'>"
            html += f"<td class='col-pos'>{i+4}º</td><td class='col-dor'>{row[2]}</td><td class='col-nom'>{row[4]}</td>"
            html += f"<td class='col-cat'>{row[8]}</td><td class='col-sub'>{row[9]}</td>"
            html += f"<td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td><td>{row[13]}</td>"
            html += f"<td class='col-tot' style='font-weight:bold;'>{row[14]}</td></tr>"
        html += "</tbody></table></div>"

        # JS Scroll Suave
        html += """
        <script>
            var b = document.getElementById('scrollBox');
            var p = false;
            function run() {
                if(!p) {
                    b.scrollTop += 1;
                    if(b.scrollTop >= (b.scrollHeight - b.clientHeight)) b.scrollTop = 0;
                }
            }
            setInterval(run, 70); // Velocidad más pausada
            b.onmouseover = () => p = true;
            b.onmouseout = () => p = false;
        </script>
        """
        return html

    components.html(crear_tabla_html(podio, resto), height=850)

except Exception as e:
    st.error(f"Error en el sistema: {e}")
