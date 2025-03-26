import streamlit as st
import pandas as pd
from ecuaciones import (
    carga_por_corrida,
    factor_saturacion,
    recuperacion_proteina,
    calcular_pureza,
    calcular_tiempo,
    calcular_costo,
    calcular_ganancia_neta,
    calcular_rentabilidad
)

st.set_page_config(page_title="Olimpiada de Bioquímica – Purificación de Proteínas")
st.title("🏆 Estrategia de Purificación de Proteínas")

url_hoja = "https://docs.google.com/spreadsheets/d/1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ/export?format=csv&gid="
sheets = {"Ejercicio": "0"}

# Función para cargar desde Google Sheets
def cargar_hoja(nombre, gid):
    try:
        enlace = url_hoja + gid
        df = pd.read_csv(enlace)
        # st.success(f"✅ Hoja '{nombre}' cargada correctamente desde Google Sheets.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Función para cargar CSV desde GitHub
@st.cache_data
def cargar_csv_desde_github(url_raw, nombre, header='infer', names=None):
    try:
        df = pd.read_csv(url_raw, header=header, names=names)
        # st.success(f"✅ Hoja '{nombre}' cargada correctamente desde GitHub.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Cargar los datos desde Google Sheets y GitHub
df_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])

url_purificacion = "https://raw.githubusercontent.com/kakuro83/BQ/main/Purificaci%C3%B3n.csv"
df_purificacion = cargar_csv_desde_github(url_purificacion, "Purificación")

url_datos = "https://raw.githubusercontent.com/kakuro83/BQ/main/Datos.csv"
df_datos = cargar_csv_desde_github(url_datos, "Datos")

url_estudiantes = "https://raw.githubusercontent.com/kakuro83/BQ/main/Estudiantes.txt"
df_estudiantes = cargar_csv_desde_github(url_estudiantes, "Estudiantes", header=None, names=["Estudiante"])

# Mostrar los datos fijos con estilo
st.header("📌 Datos Fijos")
st.dataframe(df_datos.style.set_properties(**{"text-align": "center"}).set_table_styles(
    [{"selector": "th", "props": [("text-align", "center")]}]), use_container_width=True, hide_index=True)

# Mostrar la información de columnas
st.header("🧪 Información de las Columnas de Purificación")
st.dataframe(df_purificacion.style.set_properties(**{"text-align": "center"}).set_table_styles(
    [{"selector": "th", "props": [("text-align", "center")]}]), use_container_width=True, hide_index=True)
