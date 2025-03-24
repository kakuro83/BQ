# Cromatografía.py – App para Olimpiada de Bioquímica

import streamlit as st
import pandas as pd

# --- Título de la app ---
st.set_page_config(page_title="Olimpiada de Bioquímica – Purificación de Proteínas")
st.title("🏆 Olimpiada de Bioquímica – Estrategia de Purificación de Proteínas")

# --- Enlace base para exportar como CSV desde Google Sheets ---
url_hoja = "https://docs.google.com/spreadsheets/d/1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ/export?format=csv&gid="

# Diccionario de pestañas (hojas) y sus IDs (gid)
sheets = {
    "Ejercicio": "0"
}

# Función para cargar una hoja de Google Sheets con manejo de errores
def cargar_hoja(nombre, gid):
    try:
        enlace = url_hoja + gid
        df = pd.read_csv(enlace)
        st.success(f"✅ Hoja '{nombre}' cargada correctamente desde Google Sheets.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Función para cargar una hoja de un archivo Excel en GitHub
@st.cache_data
def cargar_excel_desde_github(url_raw, hoja):
    try:
        df = pd.read_excel(url_raw, sheet_name=hoja)
        st.success(f"✅ Hoja '{hoja}' cargada correctamente desde GitHub.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{hoja}': {e}")
        return pd.DataFrame()

# --- Cargar hoja 'Ejercicio' desde Google Sheets ---
df_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])

# --- Cargar hojas 'Purificación' y 'Datos' desde Excel en GitHub ---
url_excel_raw = "https://raw.githubusercontent.com/kakuro83/BQ/58aa1d98fda8f2871d81223c74f8d3dcdbbea9e1/Fijos.xlsx"
df_purificacion = cargar_excel_desde_github(url_excel_raw, "Purificación")
df_datos = cargar_excel_desde_github(url_excel_raw, "Datos")

# --- Mostrar vista previa si se cargaron correctamente ---
if not df_ejercicio.empty:
    st.subheader("🧪 Proteína Objetivo y Condiciones Iniciales")
    st.dataframe(df_ejercicio)

if not df_purificacion.empty:
    st.subheader("🧬 Columnas de Purificación Disponibles")
    st.dataframe(df_purificacion)

if not df_datos.empty:
    st.subheader("📊 Parámetros Globales del Sistema")
    st.dataframe(df_datos)

st.info("Esta es la vista base de los datos. A partir de aquí construiremos la lógica para diseñar la estrategia de purificación.")
