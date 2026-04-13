import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO
st.set_page_config(page_title="Resultados Tiro al Plato", layout="wide")

st.markdown("""
    <style>
    /* Botones de Categorías (Grandes) */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        font-size: 18px !important; /* Letra más grande */
        height: 50px;
        background-color: #f8f9fa;
        border: 2px solid #dee2e6;
    }
    /* Botones de Subcategorías (Más pequeños) */
    div[data-testid="column"] .stButton > button {
        height: 35px;
        font-size: 14px !important;
        margin-top: 5px;
    }
    /* Estética general */
    .main { background-color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS (Basado exactamente en tu Excel)
try:
    # Leemos la hoja INSCRIPCIONES saltando las 2 primeras filas de título
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip() # Limpiar espacios
    
    # Limpiamos filas vacías basándonos en la columna de Nombres
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Convertimos columnas a números enteros (sin decimales)
    cols_a_entero = ["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL", "CAT. FU"]
    for col in cols_a_entero:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Lógica de desempate profesional: Total -> S4 -> S3 -> S2 -> S1 -> Dorsal (menor primero)
    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)

    # 3. SISTEMA DE FILTROS QUE SÍ FUNCIONA (Session State)
    if 'c' not in st.session_state: st.session_state.c = "GENERAL"
    if 's' not in st.session_state: st.session_state.s = "TODOS"

    # Botones de Categoría
    st.write("### 🏆 Filtrar por Categoría")
    col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
    with col_c1: 
        if st.button("GENERAL"): st.session_state.c = "GENERAL"
    with col_c2: 
        if st.button("1ª CAT"): st.session_state.c = 1
    with col_c3: 
        if st.button("2ª CAT"): st.session_state.c = 2
    with col_c4: 
        if st.button("3ª CAT"): st.session_state.c = 3
    with col_c5: 
        if st.button("4ª CAT"): st.session_state.c = 4

    # Botones de Subcategoría (Según tu Excel real)
    st.write("#### 👥 Filtrar por Subcategoría")
    col_s1, col_s2, col_s3, col_s4, col_s5, col_s6 = st.columns(6)
    map_sub = {"SENIOR": "SR", "DAMAS": "DAM", "JUNIOR": "JR", "VETERANO": "VET", "SUPERVET.": "SV"}
    
    with col_s1: 
        if st.button("TODAS"): st.session_state.s = "TODOS"
    with col_s2: 
        if st.button("SENIOR"): st.session_state.s = "SR"
    with col_s3: 
        if st.button("DAMAS"): st.session_state.s = "DAM"
    with col_s4: 
        if st.button("JUNIOR"): st.session_state.s = "JR"
    with col_s5: 
        if st.button("VETERANO"): st.session_state.s = "VET"
    with col_s6: 
        if st.button("SUPERVET."): st.session_state.s = "SV"

    # Aplicar Filtros Dinámicos
    df_f = df_sorted.copy()
    if st.session_state.c != "GENERAL":
        df_f = df_f[df_f["CAT. FU"] == st.session_state.c]
    if st.session_state.s != "TODOS":
        df_f = df_f[df_f["SUBC"] == st.session_state.s]

    st.info(f"Mostrando: Categoría {st.session_state.c} | Subcategoría {st.session_state.s}")

    # 4. TABLA PROFESIONAL (Podio Fijo + Scroll 20 filas)
    podio = df_f.head(3)
    resto = df_f.iloc[3:]

    def html_completo(p, r):
        # Cabecera con letra más grande
        header = """
        <tr style='background:#1f4e78; color:white; font-size: 16px;'>
            <th style='width:40px'>Pos</th>
            <th style='width:40px'>Dor</th>
            <th>Nombre y Apellidos</th>
            <th style='width:40px'>Cat</th>
            <th style='width:45px'>Sub</th>
            <th style='width:35px'>S1</th><th style='width:35px'>S2</th>
            <th style='width:35px'>S3</th><th style='width:35px'>S4</th>
            <th style='width:50px'>Tot</th>
        </tr>"""
        
        # Filas Podio
        p_rows = ""
        colors = ["#FFD700", "#C0C0C0", "#CD7F32"] # Oro, Plata, Bronce
        for idx, row in p.iterrows():
            p_rows += f"<tr style='background:{colors[idx]}33; font-weight:bold; font-size:15px;'>"
            p_rows += f"<td>{idx+1}º</td><td>{row['DORSAL']}</td><td>{row['NOMBRE Y APELLIDOS']}</td>"
            p_rows += f"<td>{row['CAT. FU']}</td><td>{row['SUBC']}</td>"
            p_rows += f"<td>{row['S-1']}</td><td>{row['S-2']}</td><td>{row['S-3']}</td><td>{row['S-4']}</td>"
            p_rows += f"<td style='color:red; font-size:18px;'>{row['TOTAL']}</td></tr>"

        # Filas Scroll (Resto)
        r_rows = ""
        for i, row in enumerate(r.values):
            # i+4 porque el resto empieza en el cuarto puesto
            r_rows += f"<tr style='font-size:15px;'><td>{i+4}º</td>"
            r_rows += f"<td>{row[2]}</td>" # Dorsal
            r_rows += f"<td style='text-align:left;'>{row[4]}</td>" # Nombre
            r_rows += f"<td>{row[8]}</td>" # Cat
            r_rows += f"<td>{row[9]}</td>" # Sub
            r_rows += f"<td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td><td>{row[13]}</td>"
            r_rows += f"<td style='font-weight:bold;'>{row[14]}</td></tr>"

        return f"""
        <style>
            table {{ width: 100%; border-collapse: collapse; font-family: 'Segoe UI', sans-serif; table-layout: fixed; }}
            th, td {{ padding: 12px 4px; border-bottom: 1px solid #eee; text-align: center; }}
            td:nth-child(3) {{ text-align: left; padding-left: 10px; overflow: hidden; white-space: nowrap; }}
            .scroll-container {{ height: 600px; overflow: hidden; border: 1px solid #ccc; background: #fff; }}
        </style>
        <table>{header}<tbody>{p_rows}</tbody></table>
        <div class="scroll-container" id="scr">
            <table><tbody>{r_rows}</tbody></table>
        </div>
        <script>
            var box = document.getElementById('scr');
            var speed = 1;
            var pause = false;
            function auto() {{
                if(!pause) {{
                    box.scrollTop += speed;
                    if(box.scrollTop >= box.scrollHeight - box.clientHeight) box.scrollTop = 0;
                }}
            }}
            var loop = setInterval(auto, 45);
            box.onmouseover = () => pause = true;
            box.onmouseout = () => pause = false;
            box.ontouchstart = () => pause = true;
        </script>
        """

    # Renderizamos con altura suficiente para 20 personas
    components.html(html_completo(podio, resto), height=850)

except Exception as e:
    st.error(f"Error al procesar el Excel: {e}")
    st.warning("Asegúrate de que el archivo se llame '1ª Tirada Año2026.xlsm' y tenga la hoja 'INSCRIPCIONES'.")
