# Cromatografía.py – App para Olimpiada de Bioquímica

import streamlit as st
import pandas as pd

# --- Título de la app ---
st.set_page_config(page_title="Olimpiada de Bioquímica – Purificación de Proteínas")
st.title("🏆 Olimpiada de Bioquímica – Estrategia de Purificación de Proteínas")

# --- Enlace a la hoja pública de Google Sheets ---
url_hoja = "https://docs.google.com/spreadsheets/d/1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ/export?format=csv&id=1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ&gid="

# Diccionario de pestañas (hojas) y sus IDs (gid)
sheets = {
    "Ejercicio": "0",
    "Purificación": "1798027090",
    "Datos": "1730716012"
}

# Función para cargar una hoja específica de la hoja de cálculo
def cargar_hoja(gid):
    enlace = url_hoja + gid
    df = pd.read_csv(enlace)
    return df

# Cargar todas las hojas necesarias
df_ejercicio = cargar_hoja(sheets["Ejercicio"])
df_purificacion = cargar_hoja(sheets["Purificación"])
df_datos = cargar_hoja(sheets["Datos"])

# Mostrar vista previa de los datos
st.subheader("🧪 Proteína Objetivo y Condiciones Iniciales")
st.dataframe(df_ejercicio)

st.subheader("🧬 Columnas de Purificación Disponibles")
st.dataframe(df_purificacion)

st.subheader("📊 Parámetros Globales del Sistema")
st.dataframe(df_datos)

st.info("Esta es la vista base de los datos. A partir de aquí construiremos la lógica para diseñar la estrategia de purificación.")
