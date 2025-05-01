import json
from pymongo import MongoClient, errors

cliente = MongoClient('mongodb://mongodb_waze:27017/')
db = cliente['trafico_waze']
coleccion = db['eventos']

try:
    coleccion.create_index('id', unique=True)
    print("Índice único creado en el campo 'id'.")
except errors.OperationFailure:
    print("El índice ya existe o ocurrió un error.")

try:
    with open('eventos_waze.json', 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)

    if isinstance(datos, dict):
        datos = [datos]

except FileNotFoundError:
    print("No se encontró el archivo 'eventos_waze.json'.")
    exit(1)
except json.JSONDecodeError:
    print("error al leer el .json")
    exit(1)

insertados = 0
for evento in datos:
    try:
        coleccion.insert_one(evento)
        insertados += 1
    except errors.DuplicateKeyError:
        continue

print(f"Se insertaron {insertados} nuevos eventos en mongoDB.")
