import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Resultados Tiro al Plato", layout="wide")
st.title("🏆 Resultados en Directo - 1ª Tirada 2026")

try:
    # 1. LEER DATOS: Usamos header=2 porque los nombres están en la 3ª fila del Excel
    df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", header=2)
    
    # Limpiar nombres de columnas (quitar espacios raros)
    df.columns = df.columns.str.strip()

    # 2. LIMPIEZA: Solo tiradores con nombre y convertir puntos a números para poder ordenar
    df = df.dropna(subset=["NOMBRE Y APELLIDOS"])
    columnas_puntos = ["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"]
    for col in columnas_puntos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. LÓGICA DE DESEMPATE: 
    # Ordena por TOTAL(Desc), luego S-4(Desc), S-3(Desc), S-2(Desc), S-1(Desc)
    # Y finalmente DORSAL(Asc) para que el primero inscrito gane en empate total.
    df_sorted = df.sort_values(
        by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
        ascending=[False, False, False, False, False, True]
    )

    # 4. FILTRO DE CATEGORÍA
    # Convertimos a texto para que el filtro no falle con los números de categoría
    df_sorted["CAT. FU"] = df_sorted["CAT. FU"].astype(str).str.replace(".0", "", regex=False)
    categorias = ["TODAS"] + sorted(df_sorted["CAT. FU"].unique().tolist())
    
    filtro = st.sidebar.selectbox("Filtrar por Categoría:", categorias)

    if filtro != "TODAS":
        df_final = df_sorted[df_sorted["CAT. FU"] == filtro]
    else:
        df_final = df_sorted

    # 5. MOSTRAR RESULTADOS
    # Añadimos una columna de posición real basada en el orden
    df_final.insert(0, "RANK", range(1, len(df_final) + 1))
    
    columnas_web = ["RANK", "DORSAL", "NOMBRE Y APELLIDOS", "CAT. FU", "S-1", "S-2", "S-3", "S-4", "TOTAL"]
    st.dataframe(df_final[columnas_web], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error técnico: {e}")
    st.info("Asegúrate de que el archivo se llame exactamente '1ª Tirada Año2026.xlsm'")
