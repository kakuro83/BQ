# ecuaciones.py – Funciones para cálculos de purificación

def carga_por_corrida(mmg, corridas):
    if corridas == 0:
        return 0
    return mmg / corridas

def factor_saturacion(carga, capacidad_columna):
    if capacidad_columna == 0:
        return 0
    return carga / capacidad_columna

def recuperacion_proteina(recuperacion_pct, fs, mezcla_mg, pureza_in):
    """
    Calcula la recuperación de la proteína objetivo (en mg) después de una etapa.
    - Si Fs > 1 → penalización por sobrecarga.
    - Si Fs <= 1 → beneficio hasta un máximo del 95 % de la proteína presente.
    """
    rb = recuperacion_pct / 100
    pi = pureza_in / 100
    proteina_total = mezcla_mg * pi
    if fs > 1:
        r = (rb / fs) * mezcla_mg * pi
    else:
        mejora = rb + (1.1 * rb - rb) * (1 - fs)  # tiende suavemente a 0.95
        r = mejora * mezcla_mg * pi
    return r

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
