from pymongo import MongoClient
import re
from datetime import datetime
from statistics import mean

# Conexión a MongoDB
cliente = MongoClient('mongodb://mongodb_wazeT2:27017/')
db = cliente['trafico_waze']
coleccion_origen = db['eventos']
coleccion_filtrada = db['eventos_filtrados']
coleccion_agrupada = db['eventos_agrupados']

# Limpieza previa
coleccion_filtrada.delete_many({})
coleccion_agrupada.delete_many({})

# Para evitar duplicados por ID
ids_vistos = set()

# Contadores
insertados = 0
descartados = 0

# --------------------------
# 1. FILTRADO Y NORMALIZACIÓN
# --------------------------
for evento in coleccion_origen.find():
    if not all([
        evento.get("id"),
        evento.get("location"),
        evento.get("type"),
        evento.get("pub_time")
    ]):
        descartados += 1
        continue

    if evento["id"] in ids_vistos:
        descartados += 1
        continue

    ids_vistos.add(evento["id"])

    # Normalización
    evento["type"] = evento["type"].strip().lower()

    if "city" in evento and evento["city"]:
        evento["city"] = re.sub(r'\s+', ' ', evento["city"].strip().lower())

    if "street" in evento and evento["street"]:
        evento["street"] = re.sub(r'\s+', ' ', evento["street"].strip().lower())

    coleccion_filtrada.insert_one(evento)
    insertados += 1

print(f"Limpieza completada.")
print(f"Insertados en eventos_filtrados: {insertados}")
print(f"Descartados: {descartados}")

# -----------------------------------------
# 2. AGRUPACIÓN POR CERCANÍA TEMPORAL Y CITY
# -----------------------------------------
print("Iniciando agrupación...")

AGRUPACION_MINUTOS = 30
AGRUPACION_MS = AGRUPACION_MINUTOS * 60 * 1000

eventos = list(coleccion_filtrada.find())

# ✅ Conversión correcta de pub_time tipo string a timestamp en ms
def pub_time_to_ms(pub_time_str):
    try:
        dt = datetime.strptime(pub_time_str, "%Y-%m-%dT%H:%M:%S")
        return int(dt.timestamp() * 1000)
    except Exception:
        return 0

eventos.sort(key=lambda e: pub_time_to_ms(e["pub_time"]))

grupos = []
grupo_actual = []

for evento in eventos:
    if not grupo_actual:
        grupo_actual.append(evento)
        continue

    ultimo = grupo_actual[-1]

    pub_time_evento = pub_time_to_ms(evento["pub_time"])
    pub_time_ultimo = pub_time_to_ms(ultimo["pub_time"])

    mismo_tipo = evento.get("type") == ultimo.get("type")
    misma_city = evento.get("city") == ultimo.get("city")
    cercano_en_tiempo = abs(pub_time_evento - pub_time_ultimo) <= AGRUPACION_MS

    if mismo_tipo and misma_city and cercano_en_tiempo:
        grupo_actual.append(evento)
    else:
        grupos.append(grupo_actual)
        grupo_actual = [evento]

if grupo_actual:
    grupos.append(grupo_actual)

# -----------------------------------------
# 3. FUSIÓN DENTRO DE LOS GRUPOS AGRUPADOS
# -----------------------------------------
def misma_fecha(ts1, ts2):
    return datetime.fromtimestamp(ts1 / 1000).date() == datetime.fromtimestamp(ts2 / 1000).date()

def coordenadas_similares(loc1, loc2, umbral=0.001):
    dx = abs(loc1.get("x", 0) - loc2.get("x", 0))
    dy = abs(loc1.get("y", 0) - loc2.get("y", 0))
    return dx <= umbral and dy <= umbral

fusionados_finales = []
for grupo in grupos:
    fusion_actual = [grupo[0]]
    for evento in grupo[1:]:
        ultimo = fusion_actual[-1]
        t1 = pub_time_to_ms(evento["pub_time"])
        t2 = pub_time_to_ms(ultimo["pub_time"])

        if (
            abs(t1 - t2) <= 2 * 60 * 1000
            and misma_fecha(t1, t2)
            and evento.get("subtype") == ultimo.get("subtype")
            and coordenadas_similares(evento.get("location", {}), ultimo.get("location", {}))
        ):
            fusion_actual.append(evento)
        else:
            fusionados_finales.append({
                "fusion_id": len(fusionados_finales) + 1,
                "tipo": ultimo.get("type"),
                "subtype": ultimo.get("subtype"),
                "city": ultimo.get("city"),
                "cantidad_original": len(fusion_actual),
                "location": {
                    "x": mean([e["location"]["x"] for e in fusion_actual if "location" in e]),
                    "y": mean([e["location"]["y"] for e in fusion_actual if "location" in e])
                },
                "pub_time": fusion_actual[0].get("pub_time"),
                "ids_originales": [e.get("id") for e in fusion_actual]
            })
            fusion_actual = [evento]

    if fusion_actual:
        ultimo = fusion_actual[-1]
        fusionados_finales.append({
            "fusion_id": len(fusionados_finales) + 1,
            "tipo": ultimo.get("type"),
            "subtype": ultimo.get("subtype"),
            "city": ultimo.get("city"),
            "cantidad_original": len(fusion_actual),
            "location": {
                "x": mean([e["location"]["x"] for e in fusion_actual if "location" in e]),
                "y": mean([e["location"]["y"] for e in fusion_actual if "location" in e])
            },
            "pub_time": fusion_actual[0].get("pub_time"),
            "ids_originales": [e.get("id") for e in fusion_actual]
        })

# Guardar eventos fusionados
coleccion_agrupada.delete_many({})
for fusion in fusionados_finales:
    coleccion_agrupada.insert_one(fusion)

print(f"Total de eventos fusionados: {len(fusionados_finales)}")
