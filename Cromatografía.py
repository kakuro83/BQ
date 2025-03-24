# 📥 Cromatografía.py - Bloque 1: Carga de datos desde Google Sheets (sin API externa), TXT y Excel (todo público)

import pandas as pd
import requests
import io

# --- 1. Google Sheets (sin API externa, desde CSV export) ---
# Exportar cada hoja como CSV directamente desde el enlace público

def cargar_csv_desde_google(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza error si falla
        return pd.read_csv(io.StringIO(response.text)).dropna()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al cargar CSV desde: {url}\n{e}")
        return pd.DataFrame()

# Enlaces actualizados a las hojas en formato CSV (usar enlaces confirmados públicamente)
url_proteinas = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRcf1jOr-2yFpsVoAv2XD_qPMu2qjchHZnGgYZd1EEl2B8uK8ycoBa5q9oQlsJxAaO8_d1xydYrGQ3S/pub?gid=0&single=true&output=csv"
url_columnas = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRcf1jOr-2yFpsVoAv2XD_qPMu2qjchHZnGgYZd1EEl2B8uK8ycoBa5q9oQlsJxAaO8_d1xydYrGQ3S/pub?gid=830674505&single=true&output=csv"
url_fijos = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRcf1jOr-2yFpsVoAv2XD_qPMu2qjchHZnGgYZd1EEl2B8uK8ycoBa5q9oQlsJxAaO8_d1xydYrGQ3S/pub?gid=1578172910&single=true&output=csv"

hoja_proteinas = cargar_csv_desde_google(url_proteinas)
hoja_columnas = cargar_csv_desde_google(url_columnas)
hoja_fijos = cargar_csv_desde_google(url_fijos)

# Convertir a diccionario de parámetros
parametros_fijos = dict(zip(hoja_fijos["Parámetro"], hoja_fijos["Valor"])) if not hoja_fijos.empty else {}

# --- 2. TXT de Estudiantes desde GitHub (público raw) ---
estudiantes_url = "https://raw.githubusercontent.com/kakuro83/BQ/3698fd9da17043e75779d8897fd0fe622229dfba/Estudiantes.txt"
lista_estudiantes = pd.read_csv(estudiantes_url, header=None)[0].dropna().tolist()

# --- 3. Excel para registro de respuestas desde GitHub (público raw) ---
url_excel = "https://raw.githubusercontent.com/kakuro83/BQ/3698fd9da17043e75779d8897fd0fe622229dfba/Respuestas.xlsx"
try:
    import openpyxl  # asegúrate de que esté disponible
    response = requests.get(url_excel)
    df_respuestas = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
except ImportError:
    print("⚠️ Falta el paquete 'openpyxl'. Agrega 'openpyxl' en requirements.txt para leer archivos Excel.")
    df_respuestas = pd.DataFrame()

# Verificación (opcional)
print("✅ Datos cargados correctamente (sin APIs externas):")
print(f"- Proteínas: {len(hoja_proteinas)} entradas")
print(f"- Columnas: {len(hoja_columnas)} técnicas")
print(f"- Parámetros fijos: {len(parametros_fijos)}")
print(f"- Estudiantes: {len(lista_estudiantes)}")
print(f"- Respuestas cargadas: {df_respuestas.shape[0]} filas")
