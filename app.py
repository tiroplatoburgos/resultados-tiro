import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Resultados Tiro - En Directo", layout="wide")

st.markdown("""
    <style>
    /* Estilo para los botones de categorías */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    /* Estilo para subcategorías (botones más pequeños) */
    div[data-testid="column"] .stButton > button {
        height: 25px;
        font-size: 12px;
        padding: 0px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BANNERS DE PUBLICIDAD ---
# Cambia 'publicidad/banner1.png' por el nombre real de tus archivos en GitHub
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    try:
        st.image("publicidad/banner_principal.png", use_container_width=True) # Banner central
    except:
        st.info("Sube tu banner a la carpeta 'publicidad' para verlo aquí")

# 2. CARGA DE DATOS
try:
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])
    
    # Convertir a numérico para ordenación
    cols_puntos = ["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"]
    for col in cols_puntos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # LÓGICA DE ORDENACIÓN (Reglamento)
    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    )

    # 3. FILTROS (Categorías y Subcategorías)
    if 'cat' not in st.session_state: st.session_state.cat = "GENERAL"
    if 'sub' not in st.session_state: st.session_state.sub = "TODOS"

    # Fila de Categorías (Botones grandes)
    st.write("### Categorías")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("GENERAL"): st.session_state.cat = "GENERAL"
    with c2: 
        if st.button("CATEGORÍA 1"): st.session_state.cat = "1"
    with c3: 
        if st.button("CATEGORÍA 2"): st.session_state.cat = "2"
    with c4: 
        if st.button("CATEGORÍA 3"): st.session_state.cat = "3"
    with c5: 
        if st.button("CATEGORÍA 4"): st.session_state.cat = "4"

    # Fila de Subcategorías (Botones pequeños debajo)
    st.write("###### Subcategorías")
    s1, s2, s3, s4, s5 = st.columns(5)
    with s1: 
        if st.button("Damas", key="b_dama"): st.session_state.sub = "DAM"
    with s2: 
        if st.button("Junior", key="b_jr"): st.session_state.sub = "JR"
    with s3: 
        if st.button("Veteranos", key="b_vet"): st.session_state.sub = "VET"
    with s4: 
        if st.button("Adaptados", key="b_ad"): st.session_state.sub = "ADAPT"
    with s5: 
        if st.button("Limpiar Filtros", key="b_clear"): 
            st.session_state.cat = "GENERAL"
            st.session_state.sub = "TODOS"

    # APLICAR FILTROS
    df_filtrado = df_sorted.copy()
    if st.session_state.cat != "GENERAL":
        df_filtrado = df_filtrado[df_filtrado["CAT. FU"].astype(str).str.contains(st.session_state.cat)]
    if st.session_state.sub != "TODOS":
        df_filtrado = df_filtrado[df_filtrado["SUBC"].astype(str).str.contains(st.session_state.sub)]

    # 4. PREPARAR EL TABLERO (Podio + Scroll)
    # Separamos los 3 primeros del resto
    podio = df_filtrado.head(3)
    resto = df_filtrado.iloc[3:]

    # Generamos el HTML para la tabla con Scroll Automático
    def generar_html_tabla(df_podio, df_resto):
        # Filas del Podio
        filas_podio = ""
        for i, r in df_podio.iterrows():
            # Color oro, plata, bronce para los 3 primeros
            color = "#FFD700" if len(filas_podio) == 0 else ("#C0C0C0" if "1" in filas_podio else "#CD7F32")
            filas_podio += f"<tr style='background-color: {color}44; font-weight: bold;'><td>{i+1}</td><td>{r['NOMBRE Y APELLIDOS']}</td><td>{r['S-1']}</td><td>{r['S-2']}</td><td>{r['S-3']}</td><td>{r['S-4']}</td><td>{r['TOTAL']}</td></tr>"

        # Filas del Resto
        filas_resto = ""
        for idx, r in enumerate(df_resto.values):
            filas_resto += f"<tr><td>{idx+4}</td><td>{r[4]}</td><td>{r[10]}</td><td>{r[11]}</td><td>{r[12]}</td><td>{r[13]}</td><td>{r[14]}</td></tr>"

        return f"""
        <style>
            table {{ width: 100%; border-collapse: collapse; font-family: sans-serif; }}
            th, td {{ padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #262730; color: white; position: sticky; top: 0; }}
            .scroll-container {{ height: 400px; overflow: hidden; position: relative; }}
        </style>
        
        <table>
            <thead>
                <tr><th>Pos</th><th>Nombre</th><th>S1</th><th>S2</th><th>S3</th><th>S4</th><th>Total</th></tr>
            </thead>
            <tbody>
                {filas_podio}
            </tbody>
        </table>
        
        <div id="scroll-box" class="scroll-container">
            <table id="tabla-movil">
                <tbody>
                    {filas_resto}
                </tbody>
            </table>
        </div>

        <script>
            const box = document.getElementById('scroll-box');
            let speed = 1;
            let paused = false;
            
            function doScroll() {{
                if(!paused) {{
                    box.scrollTop += speed;
                    if(box.scrollTop >= box.scrollHeight - box.clientHeight) {{
                        box.scrollTop = 0;
                    }}
                }}
            }}
            let interval = setInterval(doScroll, 40);
            
            box.onmouseover = () => {{ paused = true; }};
            box.onmouseout = () => {{ paused = false; }};
        </script>
        """

    # Renderizar la tabla personalizada
    components.html(generar_html_tabla(podio, resto), height=600)

except Exception as e:
    st.error(f"Error: {e}")
