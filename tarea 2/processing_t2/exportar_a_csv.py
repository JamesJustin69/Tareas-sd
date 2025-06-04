# processing/exportar_a_csv.py
from pymongo import MongoClient
from geopy.geocoders import Nominatim
import csv
import os
import time

# Conexión a MongoDB
cliente = MongoClient('mongodb://mongodb_wazeT2:27017/')
db = cliente['trafico_waze']
coleccion = db['eventos_agrupados']

# Inicializar geolocalizador
geolocator = Nominatim(user_agent="geoapi")

# Función para obtener comuna desde coordenadas
def obtener_comuna(lat, lon):
    try:
        location = geolocator.reverse(f"{lat}, {lon}", language='es')
        for tag in ['suburb', 'town', 'city', 'village']:
            if tag in location.raw['address']:
                return location.raw['address'][tag]
    except:
        return "desconocido"

# Directorio compartido
os.makedirs("/scripts", exist_ok=True)

with open('/scripts/eventos_agrupados.csv', mode='w', newline='', encoding='utf-8') as archivo_csv:
    writer = csv.writer(archivo_csv)
    writer.writerow(['fusion_id', 'tipo', 'subtype', 'comuna', 'pub_time'])

    for evento in coleccion.find():
        location = evento.get('location', {})
        lat = location.get('y')
        lon = location.get('x')
        if lat is None or lon is None:
            comuna = "desconocido"
        else:
            comuna = obtener_comuna(lat, lon)
            time.sleep(1)  # evitar bloqueo por muchas consultas

        writer.writerow([
            evento.get('fusion_id', ''),
            evento.get('tipo', ''),
            evento.get('subtype', ''),
            comuna,
            evento.get('pub_time', '')
        ])

print("✅ Exportación completada con comunas: /scripts/eventos_agrupados.csv")
