tecnica_lower = tecnica.lower()
if "his" in tecnica_lower:
    sigla = "His"
elif "lectina" in tecnica_lower:
    sigla = "Lec"
else:
    # Buscar en df_purificacion la sigla entre paréntesis
    fila_tec = df_purificacion[df_purificacion["Técnica"] == tecnica]
    if not fila_tec.empty:
        tecnica_texto = fila_tec["Técnica"].values[0]
        if "(" in tecnica_texto and ")" in tecnica_texto:
            sigla = tecnica_texto.split("(")[-1].split(")")[0].strip()
        else:
            sigla = tecnica.split()[0].upper()
    else:
        sigla = tecnica.split()[0].upper()
