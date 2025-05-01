import sys
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

import requests
import json
import os

# Construcción segura del endpoint de caché
CACHE_URL = os.environ.get("CACHE_URL", "http://localhost:5000")

CACHE_ENDPOINT = f"{CACHE_URL.rstrip('/')}/cache"

from scipy.stats import norm, poisson

# Conexión a MongoDB dentro del contenedor
mongooDOCKER = "mongodb://mongodb_waze:27017/"
dbMongo = "trafico_waze"
collection = "eventos"
tiempo_total = 180


def tiempo_espera(distribucion):
    if distribucion == "poisson":
        return max(0.05, np.random.poisson(lam=2))
    elif distribucion == "normal":
        tiempo = np.random.normal(loc=2, scale=1)
        return max(0.5, tiempo)  # tiempos negativos no existen
    else:
        raise ValueError("no es poisson ni normal")


def hacer_consulta(coleccion):
    total_eventos = coleccion.count_documents({})
    if total_eventos == 0:
        print("no hay eventos en la base de datos")
        return

    random_index = random.randint(0, total_eventos - 1)
    evento_cursor = coleccion.find().skip(random_index).limit(1)

    for doc in evento_cursor:
        evento_id = str(doc.get('id', 'N/A'))

        # 1. Buscar en caché
        try:
            res = requests.get(f"{CACHE_URL}/cache", params={"key": evento_id}, timeout=1)
            if res.status_code == 200:
                print(f"[CACHE HIT] ID={evento_id}")
                return
        except:
            print("Error accediendo al caché. Continuando sin caché...")

        # 2. Mostrar y almacenar en caché
        print(f"[CACHE MISS] el evento es -> ID={evento_id} | Type={doc.get('type', 'N/A')} | Subtype={doc.get('subtype', 'N/A')}")

        try:
            # Guardar en caché
            requests.post(f"{CACHE_URL}/cache", json={"key": evento_id, "value": doc}, timeout=1)
        except:
            print("No se pudo guardar en caché.")


def mostrar_grafico(tiempos, distribucion):
    plt.hist(tiempos, bins=30, color='skyblue', edgecolor='black', density=True)

    if distribucion == "normal":
        mu, sigma = np.mean(tiempos), np.std(tiempos)
        x = np.linspace(min(tiempos), max(tiempos), 100)
        plt.plot(x, norm.pdf(x, mu, sigma), 'hotpink', label=f"Normal esperada (μ≈{mu:.2f}, σ≈{sigma:.2f})")
    elif distribucion == "poisson":
        valores_discretos = [int(round(t)) for t in tiempos]
        lam = np.mean(valores_discretos)
        x = np.arange(0, max(valores_discretos) + 1)
        plt.plot(x, poisson.pmf(x, lam), 'hotpink', label=f"Poisson esperada (λ≈{lam:.2f})")

    plt.title(f"Distribución de tiempos de espera ({distribucion})")
    plt.xlabel("Tiempo (segundos)")
    plt.ylabel("Densidad")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("grafico_tiempos.png", dpi=300)
    print("se guardo el gráfico como 'grafico_tiempos.png'")


def main():
    if len(sys.argv) < 2:
        print("Uso: python generador_trafico.py [normal|poisson]")
        sys.exit(1)

    distribucion = sys.argv[1]
    print(f"Distribución seleccionada: {distribucion}")

    try:
        client = MongoClient(mongooDOCKER)
        print("conectando a Mongo")
        db = client[dbMongo]
        coleccion = db[collection]
        print("conexion establecida")
    except Exception as e:
        print(f"error en MongoDB {e}")
        sys.exit(1)

    print(f"generador con {distribucion}")

    tiempo_inicio = time.time()
    tiempos = []

    while (time.time() - tiempo_inicio) < tiempo_total:
        hacer_consulta(coleccion)

        espera = tiempo_espera(distribucion)
        tiempos.append(espera)
        print(f"------------------------------------------------------------------")
        time.sleep(espera)

    print("generador completado")
    mostrar_grafico(tiempos, distribucion)

if __name__ == "__main__":
    main()
