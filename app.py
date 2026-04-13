import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os

# 1. CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="Resultados Tiro - Pro v1.0", layout="wide")

# Estilo CSS para botones y estética
st.markdown("""
    <style>
    .stButton > button { width: 100%; border-radius: 20px; font-weight: bold; transition: 0.3s; }
    .stButton > button:hover { background-color: #ff4b4b; color: white; }
    /* Estilo para subcategorías (botones pequeños) */
    div[data-testid="column"] .stButton > button { height: 30px; font-size: 11px; margin-top: -10px; }
    </style>
""", unsafe_allow_html=True)

# 2. GESTIÓN DE BANNERS (Local / Carpeta)
# Para que funcione, crea una carpeta en GitHub llamada 'publicidad' y sube tus fotos
st.write("---")
cols_ban = st.columns([1, 2, 1])
with cols_ban[1]:
    if os.path.exists("publicidad/banner.png"):
        st.image("publicidad/banner.png", use_container_width=True)
    else:
        st.info("💡 Consejo: Sube tu logo a una carpeta llamada 'publicidad' con el nombre 'banner.png'")
st.write("---")

# 3. CARGA Y PROCESAMIENTO DE DATOS (VERIFICADO)
try:
    # Usamos header=2 porque tu Excel tiene títulos en las primeras filas
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip() # Limpiar espacios en nombres de columnas
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Asegurar que los puntos sean números para que el orden sea real (25 > 2)
    cols_puntos = ["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL"]
    for col in cols_puntos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # LÓGICA DE DESEMPATE PROFESIONAL:
    # 1. Total (Desc) -> 2. S4 (Desc) -> 3. S3 (Desc) -> 4. S2 (Desc) -> 5. S1 (Desc) -> 6. Dorsal (Asc)
    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)

    # 4. SISTEMA DE FILTROS (BOTONES)
    if 'cat' not in st.session_state: st.session_state.cat = "GENERAL"
    if 'sub' not in st.session_state: st.session_state.sub = "TODOS"

    st.subheader(f"📍 Mostrando: {st.session_state.cat} | {st.session_state.sub}")
    
    # Fila de Categorías (Botones Principales)
    c = st.columns(5)
    cats = ["GENERAL", "1", "2", "3", "4"]
    for i, nombre in enumerate(cats):
        if c[i].button(nombre): st.session_state.cat = nombre

    # Fila de Subcategorías (Botones pequeños debajo)
    s = st.columns(6)
    subs = ["TODOS", "DAMAS", "JUNIOR", "VETERANO", "SUPERVETERANO", "ADAPTADOS"]
    # Mapeo de nombres de Excel
    map_sub = {"DAMAS": "DAM", "JUNIOR": "JR", "VETERANO": "VET", "SUPERVETERANO": "SV", "ADAPTADOS": "AD"}
    
    for i, nombre in enumerate(subs):
        if s[i].button(nombre, key=f"sub_{nombre}"): st.session_state.sub = nombre

    # Aplicar Filtros
    df_final = df_sorted.copy()
    if st.session_state.cat != "GENERAL":
        df_final = df_final[df_final["CAT. FU"].astype(str).str.contains(st.session_state.cat)]
    if st.session_state.sub != "TODOS":
        target = map_sub.get(st.session_state.sub, "")
        df_final = df_final[df_final["SUBC"].astype(str).str.contains(target)]

    # 5. COMPONENTE VISUAL: PODIO FIJO Y SCROLL AUTOMÁTICO
    podio = df_final.head(3)
    resto = df_final.iloc[3:]

    # Construcción del HTML para el efecto visual
    def build_html(p, r):
        # Filas del Podio
        p_rows = ""
        colors = ["#FFD700", "#C0C0C0", "#CD7F32"] # Oro, Plata, Bronce
        for idx, row in p.iterrows():
            p_rows += f"""
            <tr style="background-color: {colors[idx]}44; font-weight: bold;">
                <td style="width:50px">{idx+1}º</td>
                <td>{row['NOMBRE Y APELLIDOS']}</td>
                <td style="width:40px">{row['S-1']}</td><td style="width:40px">{row['S-2']}</td>
                <td style="width:40px">{row['S-3']}</td><td style="width:40px">{row['S-4']}</td>
                <td style="color:red; width:60px">{int(row['TOTAL'])}</td>
            </tr>"""

        # Filas del Resto para el Scroll
        r_rows = ""
        for i, row in enumerate(r.values):
            r_rows += f"""
            <tr>
                <td style="width:50px">{i+4}º</td>
                <td>{row[4]}</td> <td style="width:40px">{int(row[10])}</td><td>{int(row[11])}</td>
                <td style="width:40px">{int(row[12])}</td><td>{int(row[13])}</td>
                <td style="width:60px">{int(row[14])}</td>
            </tr>"""

        return f"""
        <style>
            table {{ width: 100%; border-collapse: collapse; font-family: 'Segoe UI', sans-serif; font-size: 14px; }}
            th {{ background: #262730; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #eee; }}
            .scroll-box {{ height: 350px; overflow: hidden; border: 1px solid #ddd; }}
        </style>
        <table>
            <thead>
                <tr><th style="width:50px">Pos</th><th>Tirador</th><th style="width:40px">S1</th><th style="width:40px">S2</th><th style="width:40px">S3</th><th style="width:40px">S4</th><th style="width:60px">Tot</th></tr>
            </thead>
            <tbody>{p_rows}</tbody>
        </table>
        <div class="scroll-box" id="scr">
            <table id="tbl_resto"><tbody>{r_rows}</tbody></table>
        </div>
        <script>
            var box = document.getElementById('scr');
            var speed = 1;
            var pause = false;
            function scroll() {{
                if(!pause) {{
                    box.scrollTop += speed;
                    if(box.scrollTop >= box.scrollHeight - box.clientHeight) box.scrollTop = 0;
                }}
            }}
            var interval = setInterval(scroll, 40);
            box.onmouseover = function() {{ pause = true; }};
            box.onmouseout = function() {{ pause = false; }};
        </script>
        """

    components.html(build_html(podio, resto), height=600)

except Exception as e:
    st.error(f"❌ Error crítico en el código: {e}")
    st.info("Verifica que el archivo '1ª Tirada Año2026.xlsm' esté en la carpeta principal de GitHub.")
