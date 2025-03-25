# CromatografÃ­a.py â€“ App para Olimpiada de BioquÃ­mica

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

st.set_page_config(page_title="Olimpiada de BioquÃ­mica â€“ PurificaciÃ³n de ProteÃ­nas")
st.title("ðŸ† Olimpiada de BioquÃ­mica â€“ Estrategia de PurificaciÃ³n de ProteÃ­nas")

url_hoja = "https://docs.google.com/spreadsheets/d/1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ/export?format=csv&gid="
sheets = {"Ejercicio": "0"}

# Funciones auxiliares de carga
def cargar_hoja(nombre, gid):
    try:
        enlace = url_hoja + gid
        df = pd.read_csv(enlace)
        st.success(f"âœ… Hoja '{nombre}' cargada correctamente desde Google Sheets.")
        return df
    except Exception as e:
        st.error(f"âŒ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_csv_desde_github(url_raw, nombre, header='infer', names=None):
    try:
        df = pd.read_csv(url_raw, header=header, names=names)
        st.success(f"âœ… Hoja '{nombre}' cargada correctamente desde GitHub.")
        return df
    except Exception as e:
        st.error(f"âŒ Error al cargar la hoja '{nombre}': {e}")
        return pd.DataFrame()

# FunciÃ³n para ajustar la pureza en columnas CIEX o AIEX considerando otras proteÃ­nas
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

# Carga de hojas desde GitHub
url_purificacion = "https://raw.githubusercontent.com/kakuro83/BQ/main/Purificaci%C3%B3n.csv"
url_datos = "https://raw.githubusercontent.com/kakuro83/BQ/main/Datos.csv"
url_estudiantes = "https://raw.githubusercontent.com/kakuro83/BQ/main/Estudiantes.txt"

hoja_ejercicio = cargar_hoja("Ejercicio", sheets["Ejercicio"])
df_purificacion = cargar_csv_desde_github(url_purificacion, "PurificaciÃ³n")
df_datos = cargar_csv_desde_github(url_datos, "Datos")
df_estudiantes = cargar_csv_desde_github(url_estudiantes, "Estudiantes", header=None, names=["Estudiante"])

# Mostrar datos fijos
if not df_datos.empty:
    st.subheader("ðŸ“Š Datos Fijos")
    st.dataframe(df_datos)

if not df_purificacion.empty:
    st.subheader("ðŸ§¬ InformaciÃ³n de las Columnas de PurificaciÃ³n")
    st.dataframe(df_purificacion)

if not df_estudiantes.empty:
    st.subheader("ðŸ‘¤ SelecciÃ³n de Estudiante")
    lista_estudiantes = df_estudiantes["Estudiante"].dropna().tolist()
    estudiante = st.selectbox("Seleccione su nombre:", lista_estudiantes)

if not hoja_ejercicio.empty:
    st.subheader("ðŸ§ª SelecciÃ³n de ProteÃ­na Objetivo")
    lista_proteinas = ["Seleccionar proteÃ­na"] + hoja_ejercicio["Nombre"].dropna().tolist()
    seleccion = st.selectbox("Seleccione una proteÃ­na para visualizar sus propiedades:", lista_proteinas)

    if seleccion != "Seleccionar proteÃ­na":
        df_proteina = hoja_ejercicio[hoja_ejercicio["Nombre"] == seleccion].copy()
        columnas_bandas = [col for col in df_proteina.columns if col.startswith("Banda")]
        df_info = df_proteina.drop(columns=columnas_bandas).T
        df_info.columns = ["Valor"]
        st.markdown("### ðŸ”¬ Propiedades Generales de la ProteÃ­na")
        st.dataframe(df_info)

        # Bandas SDS-PAGE
        st.markdown("### ðŸ§« AnÃ¡lisis SDS-PAGE (Bandas Detectadas)")
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

        # Bloque: Estrategia de PurificaciÃ³n por Etapas
        st.subheader("âš—ï¸ Estrategia de PurificaciÃ³n")
        tecnicas = df_purificacion["TÃ©cnica"].dropna().unique().tolist()

        objetivo = df_bandas[df_bandas["Propiedad estructural"].str.lower() == "objetivo"]
        abundancia_objetivo = float(objetivo["Abundancia (%)"].values[0]) if not objetivo.empty else 0
        recorrido_obj = float(objetivo["Recorrido"].values[0]) if not objetivo.empty else 0

        log_mr_obj = 2.2 - 0.015 * recorrido_obj
        mr_objetivo = 10 ** log_mr_obj
        cantidad_mezcla = float(df_proteina["Cantidad (mg)"].values[0])
        pureza_inicial = abundancia_objetivo
        etiquetas = str(df_proteina["Etiquetas"].values[0])
        carga_texto = str(df_proteina["Carga"].values[0]).strip().replace(',', '.')
        try:
            carga_proteina = int(carga_texto)
        except:
            carga_proteina = 0

        for i in range(1, 5):
            st.markdown(f"**Etapa {i}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                tecnica = st.selectbox(f"TÃ©cnica {i}", ["Seleccionar"] + tecnicas, key=f"tecnica_{i}")
            with col2:
                corridas = st.number_input(f"Corridas {i}", min_value=1, step=1, key=f"corridas_{i}")
            with col3:
                velocidad = st.number_input(f"Velocidad (mg/min) {i}", min_value=0.1, step=0.1, key=f"velocidad_{i}")

            if tecnica != "Seleccionar":
                mensaje_validacion = ""
                if tecnica == "Intercambio catiÃ³nico (CIEX)" and carga_proteina < 1:
                    mensaje_validacion = "âŒ La proteÃ­na no tiene carga positiva suficiente para CIEX."
                elif tecnica == "Intercambio aniÃ³nico (AIEX)" and carga_proteina > -1:
                    mensaje_validacion = "âŒ La proteÃ­na no tiene carga negativa suficiente para AIEX."
                elif "His-tag" in tecnica and "His-tag" not in etiquetas:
                    mensaje_validacion = "âŒ La proteÃ­na no tiene etiqueta His-tag requerida."
                elif "lectina" in tecnica.lower() and "GlicoproteÃ­na" not in etiquetas:
                    mensaje_validacion = "âŒ La proteÃ­na no es una glicoproteÃ­na, no puede usarse afinidad por lectina."
                elif tecnica == "CromatografÃ­a por tamaÃ±o (SEC)":
                    mr_estimado = 60  # valor lÃ­mite SEC
                    st.text(f"Mr objetivo calculado: {mr_objetivo:.1f} kDa")
                    st.text(f"LÃ­mite mÃ¡ximo SEC: {mr_estimado:.1f} kDa")
                    if mr_objetivo > mr_estimado:
                        mensaje_validacion = f"âŒ La proteÃ­na ({mr_objetivo:.1f} kDa) es demasiado grande para SEC (lÃ­mite â‰ˆ {mr_estimado:.1f} kDa)."
                if mensaje_validacion:
                    st.warning(mensaje_validacion)

                params = df_purificacion[df_purificacion["TÃ©cnica"] == tecnica].iloc[0]
                capacidad = float(params["Capacidad (mg)"])
                costo_columna = float(params["Costo (USD)"])
                recuperacion_pct = float(params["RecuperaciÃ³n (%)"])
                pureza_base = float(params["Pureza base (%)"])
                vmax = float(params["Velocidad media (mg/min)"])
                pmax = float(params["Pureza mÃ¡xima (%)"])

                carga = carga_por_corrida(cantidad_mezcla, corridas)
                fs = factor_saturacion(carga, capacidad)
                recuperacion = recuperacion_proteina(recuperacion_pct, fs, cantidad_mezcla, pureza_inicial)
                pureza_estim = calcular_pureza(velocidad, pureza_base, vmax, pmax, pureza_inicial)
                pureza_corr = ajustar_pureza_por_selectividad(tecnica, pureza_estim, df_bandas)
                tiempo_min = calcular_tiempo(carga, velocidad, corridas)
                tiempo_h = tiempo_min / 60
                costo_total = calcular_costo(costo_columna, corridas)

                st.markdown(f"âœ… **Resultados Etapa {i}:**")
                st.markdown(f"- Carga por corrida: `{carga:.1f}` mg")
                st.markdown(f"- Factor de saturaciÃ³n: `{fs:.2f}`")
                st.markdown(f"- RecuperaciÃ³n: `{recuperacion:.1f}` mg")
                st.markdown(f"- Pureza estimada: `{pureza_estim:.1f}` %, ajustada: `{pureza_corr:.1f}` %")
                st.markdown(f"- Tiempo: `{tiempo_h:.2f}` h")
                st.markdown(f"- Costo: `${costo_total:.2f}`")

                cantidad_mezcla = recuperacion
                pureza_inicial = pureza_corr

        # BLOQUE FINAL: GANANCIA Y RENTABILIDAD
        st.subheader("ðŸ’° Resultados Finales del Proceso")
        st.markdown("Estos valores consideran Ãºnicamente la Ãºltima etapa procesada:")

        # Obtener valor comercial desde df_datos segÃºn pureza alcanzada
        valor_comercial = 0
        try:
            niveles = [1, 2, 3, 4]
            for nivel in niveles:
                pureza_min = float(df_datos[df_datos["Parametro"] == f"Pureza mÃ­nima nivel {nivel} (%)"]["Valor"].values[0])
                precio = float(df_datos[df_datos["Parametro"] == f"Valor comercial nivel {nivel} (USD)"]["Valor"].values[0])
                if pureza_corr >= pureza_min:
                    valor_comercial = precio
        except:
            valor_comercial = 0

        # Costo fijo operativo
        try:
            costo_fijo_hora = float(df_datos[df_datos["Parametro"] == "Costos fijos operativos (USD/h)"].iloc[0]["Valor"])
        except:
            costo_fijo_hora = 0

        # Sumar tiempos y costos acumulados
        tiempo_total_h = sum([calcular_tiempo(carga_por_corrida(float(df_proteina["Cantidad (mg)"].values[0]) if i == 1 else 0, 1), velocidad, 1)/60 for i in range(1, 5)])
        costo_total_final = costos_acumulados  # DeberÃ­a acumular los costos reales si se ajusta etapa por etapa

        # Ganancia y rentabilidad
        ganancia_neta = calcular_ganancia_neta(recuperacion, valor_comercial, costo_total_final, costo_fijo_hora, tiempo_total_h)
        rentabilidad = calcular_rentabilidad(ganancia_neta, tiempo_h)

        st.markdown("---")
        st.markdown("### ðŸ’¼ Resumen Final")
        st.markdown(f"- ðŸ§ª RecuperaciÃ³n final: `{recuperacion:.1f}` mg")
        st.markdown(f"- ðŸŽ¯ Pureza final alcanzada: `{pureza_corr:.1f}` %")
        st.markdown(f"- â±ï¸ Tiempo total: `{tiempo_total_h:.2f}` h")
        st.markdown(f"- ðŸ’² Costo total (USD): `{costos_acumulados:.2f}`")
        st.markdown(f"- ðŸ’µ Valor comercial aplicado: `${valor_comercial:.2f}` por mg")
        st.markdown(f"- ðŸ“ˆ Ganancia neta: `${ganancia_neta:.2f}`")
        st.markdown(f"- ðŸ“Š Rentabilidad: `{rentabilidad:.2f} USD/h`")
