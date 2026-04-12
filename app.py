import streamlit as st
import pandas as pd

# 1. Configurar la web
st.set_page_config(page_title="Resultados Tiro al Plato", layout="wide")
st.title("🏆 Resultados en Directo")

# 2. Leer los datos del Excel (empezando en la fila 2 para evitar títulos raros)
df = pd.read_excel("1ª Tirada Año2026.xlsm", sheet_name="INSCRIPCIONES", skiprows=1)

# Limpiamos filas vacías
df = df.dropna(subset=["NOMBRE Y APELLIDOS"])

# 3. EL CORAZÓN: Ordenar según tus reglas exactas
# Ordena por TOTAL (mayor a menor), luego S-4, S-3, S-2, S-1 y finalmente DORSAL (menor a mayor)
df_ordenado = df.sort_values(
    by=["TOTAL", "S-4", "S-3", "S-2", "S-1", "DORSAL"],
    ascending=[False, False, False, False, False, True]
)

# 4. El Filtro de Categoría
categorias = ["TODAS"] + sorted(df["CAT. FU"].unique().tolist())
filtro = st.sidebar.selectbox("Selecciona Categoría", categorias)

if filtro != "TODAS":
    df_ordenado = df_ordenado[df_ordenado["CAT. FU"] == filtro]

# 5. Mostrar la tabla en la web
st.dataframe(df_ordenado[["DORSAL", "NOMBRE Y APELLIDOS", "CAT. FU", "S-1", "S-2", "S-3", "S-4", "TOTAL"]], 
             use_container_width=True, hide_index=True)
