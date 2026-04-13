import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Marcador de Tiro Profesional", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fdfaf6; }
    .block-container { max-width: 1100px; padding: 1rem; margin: auto; }
    
    /* Centrar Botones */
    div.stButton > button {
        width: 100%;
        height: 45px;
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid #d1d5db;
    }
    h3, h4 { text-align: center; color: #1f4e78; margin-bottom: 10px; }
    
    /* Ajuste para que los botones se vean bien en fila */
    [data-testid="column"] { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
try:
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # Limpieza de datos
    cols_num = ["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL", "CAT. FU"]
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Ordenación oficial
    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    ).reset_index(drop=True)

    # 3. LÓGICA DE FILTROS (TOGGLE)
    if 'c_sel' not in st.session_state: st.session_state.c_sel = "GENERAL"
    if 's_sel' not in st.session_state: st.session_state.s_sel = None

    st.write("### 🏆 CATEGORÍAS")
    c_cols = st.columns(5)
    cats = {"GENERAL": "GENERAL", "1ª CATEGORÍA": 1, "2ª CATEGORÍA": 2, "3ª CATEGORÍA": 3, "4ª CATEGORÍA": 4}
    for i, (lab, val) in enumerate(cats.items()):
        with c_cols[i]:
            activo = (st.session_state.c_sel == val)
            if st.button(lab, key=f"c_{val}", type="primary" if activo else "secondary"):
                st.session_state.c_sel = "GENERAL" if activo else val

    st.write("#### 👥 SUBCATEGORÍAS")
    s_cols = st.columns(4)
    subs = {"SENIOR": "SR", "DAMAS": "DM", "JUNIOR": "JR", "VETERANO": "VET"}
    for i, (lab, val) in enumerate(subs.items()):
        with s_cols[i]:
            activo_s = (st.session_state.s_sel == val)
            if st.button(lab, key=f"s_{val}", type="primary" if activo_s else "secondary"):
                st.session_state.s_sel = None if activo_s else val

    # Filtrado
    df_f = df_sorted.copy()
    if st.session_state.c_sel != "GENERAL":
        df_f = df_f[df_f["CAT. FU"] == st.session_state.c_sel]
    if st.session_state.s_sel:
        df_f = df_f[df_f["SUBC"] == st.session_state.s_sel]

    # Resetear índices para que el podio sea 1, 2, 3 siempre
    df_f = df_f.reset_index(drop=True)
    podio = df_f.head(3)
    resto = df_f.iloc[3:]

    # 4. TABLA HTML PROFESIONAL
    def build_table(p, r):
        # USAMOS PORCENTAJES (%) PARA QUE NO SE DESCUADRE NADA
        style = """
        <style>
            .container { width: 100%; font-family: sans-serif; background: #fff; }
            table { width: 100%; border-collapse: collapse; table-layout: fixed; }
            th, td { padding: 10px 2px; text-align: center; font-size: 13px; border-bottom: 1px solid #eee; overflow: hidden; }
            
            /* ANCHURAS EXACTAS PARA AMBAS TABLAS */
            .w-pos { width: 8%; } .w-dor { width: 7%; } .w-nom { width: 25%; text-align: left; padding-left: 5px; }
            .w-prov { width: 12%; } .w-cat { width: 8%; } .w-sub { width: 8%; } .w-s { width: 5.5%; } .w-tot { width: 10%; }

            thead tr { background: #1f4e78; color: white; }
            .oro { background: #fff9c4; font-weight: bold; }
            .plata { background: #f5f5f5; font-weight: bold; }
            .bronce { background: #efebe9; font-weight: bold; }
            .z1 { background: #ffffff; } .z2 { background: #f9f9f9; }
            .red-tot { color: #d32f2f; font-weight: bold; font-size: 15px; }

            .scroll-box { height: 500px; overflow: hidden; border: 1px solid #ddd; border-top: none; }
            
            /* Ajuste móvil para que no se corte */
            @media (max-width: 600px) {
                th, td { font-size: 10px; padding: 8px 1px; }
                .red-tot { font-size: 11px; }
            }
        </style>
        """

        header = """
        <div class="container">
        <table>
            <thead>
                <tr>
                    <th class="w-pos">Pos</th><th class="w-dor">Dor</th><th class="w-nom">Nombre</th>
                    <th class="w-prov">Prov</th><th class="w-cat">Cat</th><th class="w-sub">Sub</th>
                    <th class="w-s">S1</th><th class="w-s">S2</th><th class="w-s">S3</th><th class="w-s">S4</th>
                    <th class="w-tot">Total</th>
                </tr>
            </thead>
            <tbody>"""
        
        # Filas Podio (Dinámicas según filtro)
        p_rows = ""
        colors = ["oro", "plata", "bronce"]
        for i, row in p.iterrows():
            c = colors[i] if i < 3 else ""
            p_rows += f"<tr class='{c}'>"
            p_rows += f"<td class='w-pos'>{i+1}º</td><td class='w-dor'>{row['DORSAL']}</td><td class='w-nom'>{row['NOMBRE Y APELLIDOS']}</td>"
            p_rows += f"<td class='w-prov'>{row['PROV']}</td><td class='w-cat'>{row['CAT. FU']}</td><td class='w-sub'>{row['SUBC']}</td>"
            p_rows += f"<td class='w-s'>{row['S-1']}</td><td class='w-s'>{row['S-2']}</td><td class='w-s'>{row['S-3']}</td><td class='w-s'>{row['S-4']}</td>"
            p_rows += f"<td class='w-tot red-tot'>{row['TOTAL']}</td></tr>"
        
        # Filas Resto
        r_rows = ""
        for i, row in enumerate(r.values):
            z = "z1" if i % 2 == 0 else "z2"
            r_rows += f"<tr class='{z}'>"
            r_rows += f"<td class='w-pos'>{i+4}º</td><td class='w-dor'>{row[2]}</td><td class='w-nom'>{row[4]}</td>"
            r_rows += f"<td class='w-prov'>{row[6]}</td><td class='w-cat'>{row[8]}</td><td class='w-sub'>{row[9]}</td>"
            r_rows += f"<td class='w-s'>{row[10]}</td><td class='w-s'>{row[11]}</td><td class='w-s'>{row[12]}</td><td class='w-s'>{row[13]}</td>"
            r_rows += f"<td class='w-tot' style='font-weight:bold;'>{row[14]}</td></tr>"

        footer = f"""
            </tbody>
        </table>
        <div class="scroll-box" id="scroller">
            <table><tbody>{r_rows}</tbody></table>
        </div>
        </div>
        <script>
            var s = document.getElementById('scroller');
            var pause = false;
            function step() {{
                if(!pause) {{
                    s.scrollTop += 1;
                    if(s.scrollTop >= (s.scrollHeight - s.clientHeight)) s.scrollTop = 0;
                }}
            }}
            setInterval(step, 80);
            s.onmouseover = () => pause = true;
            s.onmouseout = () => pause = false;
        </script>
        """
        return style + header + p_rows + footer

    components.html(build_table(podio, resto), height=850)

except Exception as e:
    st.error(f"Error técnico: {e}")
