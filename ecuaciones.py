# ecuaciones.py – Funciones para cálculos de purificación

def carga_por_corrida(mmg, corridas):
    if corridas == 0:
        return 0
    return mmg / corridas

def factor_saturacion(carga, capacidad_columna):
    if capacidad_columna == 0:
        return 0
    return carga / capacidad_columna

def recuperacion_proteina(recuperacion_columna_pct, fs, mmg, abundancia_pct):
    if fs == 0:
        return 0
    return (recuperacion_columna_pct / fs) * mmg * (abundancia_pct / 100)

def calcular_pureza(v, pb, vmax, pmax, pin):
    if vmax == 0:
        return pb
    if v < vmax:
        p = pb + (pmax - pb) * (1 - v / vmax)
    else:
        p = pb - (pb - pin) * ((v - vmax) / vmax)
    return max(min(p, pmax), pin)

def calcular_tiempo(carga, velocidad, corridas):
    if velocidad == 0:
        return 0
    return (carga / velocidad) * corridas

def calcular_costo(costo_columna, corridas):
    return costo_columna * corridas

def calcular_ganancia_neta(recuperacion_final_mg, valor_unitario_usd_mg, costo_columnas_usd, costo_operativo_usd_h, tiempo_total_h):
    return (recuperacion_final_mg * valor_unitario_usd_mg) - costo_columnas_usd - (costo_operativo_usd_h * tiempo_total_h)

def calcular_rentabilidad(ganancia_neta, tiempo_total_h):
    if tiempo_total_h == 0:
        return 0
    return ganancia_neta / tiempo_total_h
