import requests
import json
import time
from datetime import datetime

# rm
BOTTOM = -34.2
TOP = -33.0
LEFT = -71.2
RIGHT = -70.2


URL = f"https://www.waze.com/live-map/api/georss?top={TOP}&bottom={BOTTOM}&left={LEFT}&right={RIGHT}&env=row&types=alerts,traffic,users"


headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'es-419,es;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.waze.com/es-419/live-map/',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Opera GX";v="118", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0',
}
cookies = {
    '_web_visitorid': '6407009f-2359-4f99-a3df-f0948a5b27de',
    '_gcl_au': '1.1.277364801.1745609453',
    'SLO_G_WPT_TO': 'es',
    '_gid': 'GA1.2.779936831.1745609453',
    '_csrf_token': 'OxWPjQ23708kgVqP3kidabKr36uYepZZia3lo7RFX2I',
    'SLO_GWPT_Show_Hide_tmp': '1',
    'SLO_wptGlobTipTmp': '1',
    '_ga_2848KND9CX': 'GS1.1.1745609452.1.1.1745612247.0.0.0',
    '_ga': 'GA1.2.882951688.1745609453',
    '_ga_NNCFE4W9M4': 'GS1.2.1745609453.1.1.1745612248.0.0.0',
    '_ga_T2C59N2WYS': 'GS1.2.1745609453.1.1.1745612248.0.0.0',
    '_web_session': 'dlk1ck1xQm91KzFLR1dGVHFzeE9XU2Jta0pZMC9wL3dnKzNkRy8xcDNxV1Aydk02aXBaaTJVNFBZRVZVT1VPTi0tWlNNcEJLb0FSeHVlQ29pV2NrZEtEZz09--618cc9b0a54bb21f874264f70841d0296e0a3f01',
    'recaptcha-ca-t': 'AbEMS0uJ3GE9qxHvu20v4T-B0U2SuPigtOCJI7xgipRBH8AOveyQSc6ZoLx-q1-0nZhvvn5PsOPvP2mwreFkyGrjZkRMC4uNyxRPpWXf4FMsMu8O5q33Ug0TCbP7O_gvjhGMra1RBGOG75otT06IAQSXCiZ1X-v0mJrAXg:U=c1f28c49be000000',
}

OUTPUT_FILE = "eventos_wazeT2.json"
MAX_EVENTOS = 11500
DELAY = 20

def obtenerEventoos():
    try:
        response = requests.get(URL, headers=headers, cookies=cookies)
        if response.status_code == 403:
            print("error 403")
            return None
        data = response.json()
        if not isinstance(data, dict):
            print("respuesta no sirve, es un JSON no válido")
            return None
        return data
    except Exception as e:
        print(f"error al solicitar datos: {e}")
        return None

def clasificarJams(speed):
    if speed is None:
        return "UNKNOWN_TRAFFIC"
    if speed < 10:
        return "STAND_STILL_TRAFFIC"
    elif speed < 30:
        return "HEAVY_TRAFFIC"
    elif speed < 50:
        return "MODERATE_TRAFFIC"
    else:
        return "LIGHT_TRAFFIC"

def extraerDatos(data):
    eventos = []
    for tipoPrinci in data.keys():
        if isinstance(data.get(tipoPrinci), list):
            for evento in data.get(tipoPrinci, []):
                if tipoPrinci == "traffic":
                    speed = evento.get("speed")
                    subtype = clasificarJams(speed)
                    tipo_final = "jams"
                else:
                    subtype = evento.get("subtype", "")
                    tipo_final = tipoPrinci
                eventos.append({
                    "id": evento.get("uuid", ""),
                    "type": tipo_final,
                    "subtype": subtype,
                    "description": evento.get("description", ""),
                    "location": evento.get("location", {}),
                    "pub_time": datetime.fromtimestamp(evento.get("pubMillis", 0)/1000).isoformat(),
                })
    return eventos

def main():
    eventosTotales = {}
    iteracion = 1

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            eGuardados = json.load(f)
            eventosTotales = {e["id"]: e for e in eGuardados}
            print(f"{len(eventosTotales)} eventos anteriores")
    except FileNotFoundError:
        pass

    while len(eventosTotales) < MAX_EVENTOS:
        print(f"vuelta {iteracion} y eventos ya guardados: {len(eventosTotales)}")
        data = obtenerEventoos()
        if data is None:
            print("saltando pq no se pudo extraer")
            time.sleep(DELAY)
            continue

        nuevos = extraerDatos(data)
        nuevos_count = 0

        for evento in nuevos:
            if evento["id"] not in eventosTotales:
                eventosTotales[evento["id"]] = evento
                nuevos_count += 1

        print(f"se suman {nuevos_count} eventos")
        iteracion += 1

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(list(eventosTotales.values()), f, indent=2, ensure_ascii=False)

        if len(eventosTotales) >= MAX_EVENTOS:
            print(f"{len(eventosTotales)} eventos guardados finalmente")
            break

        time.sleep(DELAY)

if __name__ == "__main__":
    main()