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

# Función para seleccionar el valor comercial según la pureza alcanzada
def obtener_valor_comercial(pureza_final, df_datos):
    niveles = {}
    for i in range(1, 5):
        pmin = df_datos[df_datos["Parametro"] == f"Pureza mínima nivel {i} (%)"]["Valor"].values[0]
        valor = df_datos[df_datos["Parametro"] == f"Valor comercial nivel {i} (USD)"]["Valor"].values[0]
        niveles[i] = {"min": pmin, "valor": valor}
    niveles_ordenados = sorted(niveles.items(), key=lambda x: x[1]["min"], reverse=True)
    for _, nivel in niveles_ordenados:
        if pureza_final >= nivel["min"]:
            return nivel["valor"]
    return 0

# Función para ajustar la pureza en columnas CIEX o AIEX considerando otras proteínas

def ajustar_pureza_por_selectividad(tecnica, pureza_estim, df_bandas):
    if tecnica not in ["CIEX", "AIEX"]:
        return pureza_estim

    objetivo = df_bandas[df_bandas["Propiedad estructural"].str.lower() == "objetivo"]
    if objetivo.empty:
        return pureza_estim

    carga_objetivo = int(objetivo["Carga neta"].values[0])
    abundancia_obj = float(objetivo["Abundancia (%)"].values[0])

    if tecnica == "CIEX":
        retenidas = df_bandas[df_bandas["Carga neta"].astype(int) >= 1]
    elif tecnica == "AIEX":
        retenidas = df_bandas[df_bandas["Carga neta"].astype(int) <= -1]
    else:
        return pureza_estim

    suma_abundancias = retenidas["Abundancia (%)"].astype(float).sum()
    if suma_abundancias == 0:
        return pureza_estim

    pureza_corr = (abundancia_obj / suma_abundancias) * pureza_estim
    return round(pureza_corr, 2)

# Resto del código sin cambios...

# Al final:
st.info("Esta es la vista base de los datos. A partir de aquí construiremos la lógica para diseñar la estrategia de purificación.")
