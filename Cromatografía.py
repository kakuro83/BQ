# Cromatografía.py – App para Olimpiada de Bioquímica

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
st.title("🏆 Olimpiada de Bioquímica – Estrategia de Purificación de Proteínas")

url_hoja = "https://docs.google.com/spreadsheets/d/1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ/export?format=csv&gid="
sheets = {"Ejercicio": "0"}

# Función para cargar desde Google Sheets
def cargar_hoja(nombre, gid):
    try:
        enlace = url_hoja + gid
        df = pd.read_csv(enlace)
        st.success(f"✅ Hoja '{nombre}' cargada correctamente desde Google Sheets.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Función para cargar CSV desde GitHub
@st.cache_data
def cargar_csv_desde_github(url_raw, nombre, header='infer', names=None):
    try:
        df = pd.read_csv(url_raw, header=header, names=names)
        st.success(f"✅ Hoja '{nombre}' cargada correctamente desde GitHub.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()
# Función para ajustar la pureza considerando CIEX, AIEX y SEC
def ajustar_pureza_por_selectividad(tecnica, pureza_estim, df_bandas):
    objetivo = df_bandas[df_bandas["Propiedad estructural"].str.lower() == "objetivo"]
    if objetivo.empty:
        return pureza_estim

    try:
        abundancia_obj = float(objetivo["Abundancia (%)"].values[0])
    except:
        return pureza_estim

    if "CIEX" in tecnica:
        retenidas = df_bandas[df_bandas["Carga neta"].astype(int) >= 1]
    elif "AIEX" in tecnica:
        retenidas = df_bandas[df_bandas["Carga neta"].astype(int) <= -1]
    elif "SEC" in tecnica:
        def calcular_mr(recorrido):
            try:
                return 10 ** (2.2 - 0.015 * float(recorrido))
            except:
                return float('inf')
        df_bandas["Mr"] = df_bandas["Recorrido"].apply(calcular_mr)
        retenidas = df_bandas[df_bandas["Mr"] <= 60]
    else:
        return pureza_estim

    suma_abundancias = retenidas["Abundancia (%)"].astype(float).sum()
    if suma_abundancias == 0:
        return pureza_estim

    pureza_corr = (abundancia_obj / suma_abundancias) * pureza_estim
    return round(pureza_corr, 2)

# Carga de los archivos desde Google Sheets y GitHub
df_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])
url_purificacion = "https://raw.githubusercontent.com/kakuro83/BQ/main/Purificaci%C3%B3n.csv"
df_purificacion = cargar_csv_desde_github(url_purificacion, "Purificación")

url_datos = "https://raw.githubusercontent.com/kakuro83/BQ/main/Datos.csv"
df_datos = cargar_csv_desde_github(url_datos, "Datos")

url_estudiantes = "https://raw.githubusercontent.com/kakuro83/BQ/main/Estudiantes.txt"
df_estudiantes = cargar_csv_desde_github(url_estudiantes, "Estudiantes", header=None, names=["Estudiante"])

# Mostrar los datos fijos
st.header("📌 Datos Fijos")
st.dataframe(df_datos)

# Mostrar la información de columnas
st.header("🧪 Información de las Columnas de Purificación")
st.dataframe(df_purificacion)

# Selección de estudiante y proteína
lista_estudiantes = df_estudiantes["Estudiante"].dropna().tolist()
estudiante_seleccionado = st.selectbox("Selecciona tu nombre:", ["Seleccionar estudiante"] + lista_estudiantes)

proteinas_disponibles = df_ejercicio["Nombre"].dropna().unique().tolist()
proteina_seleccionada = st.selectbox("Selecciona la proteína objetivo:", ["Seleccionar proteína"] + proteinas_disponibles)

if proteina_seleccionada != "Seleccionar proteína":
    df_proteina = df_ejercicio[df_ejercicio["Nombre"] == proteina_seleccionada]
    st.subheader("🔬 Información de la proteína seleccionada")
    st.dataframe(df_proteina)

    # Procesamiento de bandas SDS-PAGE
    bandas = ["A", "B", "C", "D", "E"]
    columnas_bandas = ["Recorrido", "Abundancia (%)", "Carga neta", "Propiedad estructural"]
    data_bandas = {col: [] for col in columnas_bandas}

    for banda in bandas:
        valores = df_proteina[f"Banda {banda}"].values[0].split(";")
        for i, col in enumerate(columnas_bandas):
            data_bandas[col].append(valores[i].strip())

    df_bandas = pd.DataFrame(data_bandas)
    st.subheader("🧫 Bandas SDS-PAGE de la mezcla")
    st.dataframe(df_bandas)
