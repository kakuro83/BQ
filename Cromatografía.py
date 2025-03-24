# 📥 Cromatografía.py - Bloque 1: Carga de datos desde Google Sheets (sin API externa), TXT y Excel (todo público)

import pandas as pd
import requests
import io

# --- 1. Google Sheets (sin API externa, desde CSV export) ---
def cargar_csv_desde_google(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(io.StringIO(response.text)).dropna()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al cargar CSV desde: {url}\n{e}")
        return pd.DataFrame()

# ID real del documento compartido y GID de las hojas
sheet_id = "1Rqk1GZ3Y5KKNT5VjTXI-pbFhlVZ-c-XcCCjmXAM6DiQ"
url_proteinas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
url_columnas = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=830674505"
url_fijos = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1578172910"

hoja_proteinas = cargar_csv_desde_google(url_proteinas)
hoja_columnas = cargar_csv_desde_google(url_columnas)
hoja_fijos = cargar_csv_desde_google(url_fijos)

parametros_fijos = dict(zip(hoja_fijos["Parámetro"], hoja_fijos["Valor"])) if not hoja_fijos.empty else {}

# --- 2. TXT de Estudiantes desde GitHub ---
estudiantes_url = "https://raw.githubusercontent.com/kakuro83/BQ/3698fd9da17043e75779d8897fd0fe622229dfba/Estudiantes.txt"
lista_estudiantes = pd.read_csv(estudiantes_url, header=None)[0].dropna().tolist()

# --- 3. Excel para registro de respuestas desde GitHub ---
url_excel = "https://raw.githubusercontent.com/kakuro83/BQ/3698fd9da17043e75779d8897fd0fe622229dfba/Respuestas.xlsx"
try:
    import openpyxl
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
