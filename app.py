import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="Resultados En Directo", layout="wide")

# CSS para botones profesionales y colores
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
    }
    /* Estilo para el botón activo */
    .active-btn { background-color: #1f4e78 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS Y LIMPIEZA
try:
    # Leemos el excel saltando las filas de título
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Convertir a entero para quitar los ".0"
    cols_num = ["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL"]
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Lógica de desempate
    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)

    # 3. GESTIÓN DE FILTROS (ESTADO DE SESIÓN)
    if 'c' not in st.session_state: st.session_state.c = "GENERAL"
    if 's' not in st.session_state: st.session_state.s = "TODOS"

    # --- BOTONES DE CATEGORÍAS ---
    st.write("### 🏆 Categorías")
    cats = ["GENERAL", "1", "2", "3", "4"]
    cols_cat = st.columns(5)
    for i, cat in enumerate(cats):
        if cols_cat[i].button(cat, key=f"btn_{cat}"):
            st.session_state.c = cat

    # --- BOTONES DE SUBCATEGORÍAS (Pequeños) ---
    st.write("###### 👥 Subcategorías")
    subs = ["TODOS", "DAMAS", "JUNIOR", "VETERANO", "ADAPTADOS"]
    cols_sub = st.columns(5)
    map_sub = {"DAMAS": "DAM", "JUNIOR": "JR", "VETERANO": "VET", "ADAPTADOS": "AD"}
    
    for i, sub in enumerate(subs):
        if cols_sub[i].button(sub, key=f"sub_{sub}"):
            st.session_state.s = sub

    # Filtrado Real
    df_f = df_sorted.copy()
    if st.session_state.c != "GENERAL":
        df_f = df_f[df_f["CAT. FU"].astype(str).str.contains(st.session_state.c)]
    if st.session_state.s != "TODOS":
        target = map_sub.get(st.session_state.s, "")
        df_f = df_f[df_f["SUBC"].astype(str).str.contains(target)]

    # 4. CONSTRUCCIÓN DE LA TABLA (PODIO + SCROLL DE 20 FILAS)
    podio = df_f.head(3)
    resto = df_f.iloc[3:]

    def build_table_html(p, r):
        # Definimos anchos fijos para que todo cuadre perfectamente
        header = """
        <tr style='background:#1f4e78; color:white;'>
            <th style='width:40px'>Pos</th>
            <th>Tirador</th>
            <th style='width:35px'>S1</th><th style='width:35px'>S2</th>
            <th style='width:35px'>S3</th><th style='width:35px'>S4</th>
            <th style='width:45px'>Tot</th>
        </tr>"""
        
        p_rows = ""
        colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
        for idx, row in p.iterrows():
            p_rows += f"<tr style='background:{colors[idx]}33; font-weight:bold;'>"
            p_rows += f"<td>{idx+1}º</td><td>{row['NOMBRE Y APELLIDOS']}</td>"
            p_rows += f"<td>{row['S-1']}</td><td>{row['S-2']}</td><td>{row['S-3']}</td><td>{row['S-4']}</td>"
            p_rows += f"<td style='color:red'>{row['TOTAL']}</td></tr>"

        r_rows = ""
        for i, row in enumerate(r.values):
            # Usamos índices fijos basados en tu Excel para evitar errores de nombre
            r_rows += f"<tr><td style='width:40px'>{i+4}º</td>"
            r_rows += f"<td>{row[4]}</td>" # Nombre
            r_rows += f"<td style='width:35px'>{row[10]}</td><td style='width:35px'>{row[11]}</td>"
            r_rows += f"<td style='width:35px'>{row[12]}</td><td style='width:35px'>{row[13]}</td>"
            r_rows += f"<td style='width:45px; font-weight:bold;'>{row[14]}</td></tr>"

        return f"""
        <style>
            table {{ width: 100%; border-collapse: collapse; font-family: sans-serif; table-layout: fixed; }}
            th, td {{ padding: 8px 4px; border-bottom: 1px solid #eee; text-align: center; font-size: 13px; }}
            td:nth-child(2), th:nth-child(2) {{ text-align: left; overflow: hidden; white-space: nowrap; }}
            .scroll-box {{ height: 650px; overflow: hidden; border: 1px solid #ddd; }}
        </style>
        <table>{header}<tbody>{p_rows}</tbody></table>
        <div class="scroll-box" id="scr">
            <table id="target"><tbody>{r_rows}</tbody></table>
        </div>
        <script>
            var box = document.getElementById('scr');
            var speed = 1;
            var pause = false;
            function sc() {{
                if(!pause) {{
                    box.scrollTop += speed;
                    if(box.scrollTop >= box.scrollHeight - box.clientHeight) box.scrollTop = 0;
                }}
            }}
            setInterval(sc, 45);
            box.onmouseover = () => pause = true;
            box.onmouseout = () => pause = false;
            box.ontouchstart = () => pause = true;
        </script>
        """

    # Altura ajustada para unos 20-25 tiradores (800px total)
    components.html(build_table_html(podio, resto), height=850)

except Exception as e:
    st.error(f"Error detectado: {e}")
