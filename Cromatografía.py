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

# Funciones auxiliares de carga
def cargar_hoja(nombre, gid):
    try:
        enlace = url_hoja + gid
        df = pd.read_csv(enlace)
        st.success(f"✅ Hoja '{nombre}' cargada correctamente desde Google Sheets.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_csv_desde_github(url_raw, nombre, header='infer', names=None):
    try:
        df = pd.read_csv(url_raw, header=header, names=names)
        st.success(f"✅ Hoja '{nombre}' cargada correctamente desde GitHub.")
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# Función para ajustar la pureza en columnas CIEX o AIEX considerando otras proteínas
def ajustar_pureza_por_selectividad(tecnica, pureza_estim, df_bandas):
    if tecnica not in ["Intercambio catiónico (CIEX)", "Intercambio aniónico (AIEX)"]:
        return pureza_estim

    objetivo = df_bandas[df_bandas["Propiedad estructural"].str.lower() == "objetivo"]
    if objetivo.empty:
        return pureza_estim

    try:
        carga_objetivo = int(objetivo["Carga neta"].values[0])
        abundancia_obj = float(objetivo["Abundancia (%)"].values[0])
    except:
        return pureza_estim

    if "CIEX" in tecnica:
        retenidas = df_bandas[df_bandas["Carga neta"].astype(int) >= 1]
    elif "AIEX" in tecnica:
        retenidas = df_bandas[df_bandas["Carga neta"].astype(int) <= -1]
    else:
        return pureza_estim

    suma_abundancias = retenidas["Abundancia (%)"].astype(float).sum()
    if suma_abundancias == 0:
        return pureza_estim

    pureza_corr = (abundancia_obj / suma_abundancias) * pureza_estim
    return round(pureza_corr, 2)

# Carga de hojas desde GitHub
url_purificacion = "https://raw.githubusercontent.com/kakuro83/BQ/main/Purificaci%C3%B3n.csv"
url_datos = "https://raw.githubusercontent.com/kakuro83/BQ/main/Datos.csv"
url_estudiantes = "https://raw.githubusercontent.com/kakuro83/BQ/main/Estudiantes.txt"

hoja_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])
df_purificacion = cargar_csv_desde_github(url_purificacion, "Purificación")
df_datos = cargar_csv_desde_github(url_datos, "Datos")
df_estudiantes = cargar_csv_desde_github(url_estudiantes, "Estudiantes", header=None, names=["Estudiante"])

# Mostrar datos fijos
if not df_datos.empty:
    st.subheader("📊 Datos Fijos")
    st.dataframe(df_datos)

if not df_purificacion.empty:
    st.subheader("🧬 Información de las Columnas de Purificación")
    st.dataframe(df_purificacion)

if not df_estudiantes.empty:
    st.subheader("👤 Selección de Estudiante")
    lista_estudiantes = df_estudiantes["Estudiante"].dropna().tolist()
    estudiante = st.selectbox("Seleccione su nombre:", lista_estudiantes)

if not hoja_ejercicio.empty:
    st.subheader("🧪 Selección de Proteína Objetivo")
    lista_proteinas = ["Seleccionar proteína"] + hoja_ejercicio["Nombre"].dropna().tolist()
    seleccion = st.selectbox("Seleccione una proteína para visualizar sus propiedades:", lista_proteinas)

    if seleccion != "Seleccionar proteína":
        df_proteina = hoja_ejercicio[hoja_ejercicio["Nombre"] == seleccion].copy()
        columnas_bandas = [col for col in df_proteina.columns if col.startswith("Banda")]
        df_info = df_proteina.drop(columns=columnas_bandas).T
        df_info.columns = ["Valor"]
        st.markdown("### 🔬 Propiedades Generales de la Proteína")
        st.dataframe(df_info)

        # Bandas SDS-PAGE
        st.markdown("### 🧫 Análisis SDS-PAGE (Bandas Detectadas)")
        bandas = []
        for col in columnas_bandas:
            datos = df_proteina.iloc[0][col]
            if pd.notna(datos):
                valores = datos.split(";")
                if len(valores) == 4:
                    bandas.append({
                        "Banda": col.split()[-1],
                        "Recorrido": valores[0],
                        "Abundancia (%)": valores[1],
                        "Carga neta": valores[2],
                        "Propiedad estructural": valores[3]
                    })
        df_bandas = pd.DataFrame(bandas)
        st.dataframe(df_bandas)

        st.info("Esta es la vista base de los datos. A partir de aquí construiremos la lógica para diseñar la estrategia de purificación.")
