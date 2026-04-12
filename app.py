import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Resultados Tiro al Plato", layout="wide")
st.title("🏆 Resultados en Directo")

# 2. Carga de datos con manejo de errores
try:
    # Leemos el archivo. El nombre debe ser EXACTO al que subiste a GitHub
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", skiprows=1)
    
    # Limpiamos nombres de columnas por si tienen espacios vacíos
    df.columns = df.columns.str.strip()

    # Quitamos filas donde no haya nombre de tirador
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

    # 3. Lógica de Ordenación (Total > S-4 > S-3 > S-2 > S-1 > Dorsal menor)
    df_ordenado = df.sort_values(
        by=["TOTAL", "S-1", "S-2", "S-3", "S-4", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    )

    # 4. Filtro por Categoría
    categorias = ["TODAS"] + sorted([str(c) for c in df["CAT. FU"].unique() if pd.notna(c)])
    filtro = st.sidebar.selectbox("Selecciona Categoría", categorias)

    if filtro != "TODAS":
        df_ordenado = df_ordenado[df_ordenado["CAT. FU"].astype(str) == filtro]

    # 5. Mostrar tabla
    # Seleccionamos solo las columnas importantes para que se vea limpio
    columnas_mostrar = ["DORSAL", "NOMBRE Y APELLIDOS", "CAT. FU", "S-1", "S-2", "S-3", "S-4", "TOTAL"]
    st.dataframe(df_ordenado[columnas_mostrar], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.info("Asegúrate de que el archivo '1ª Tirada Año2026.xlsm' esté en la misma carpeta que este código.")
