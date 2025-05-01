from flask import Flask, request, jsonify
import redis
import os
import json

app = Flask(__name__)

# Obtener dirección de Redis desde variable de entorno
redis_host = os.environ.get("REDIS_URL", "localhost")
redis_port = 6379
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


@app.route("/cache", methods=["POST"])
def guardar_en_cache():
    data = request.get_json()
    key = data.get("key")
    value = data.get("value")

    if key and value:
        try:
            print(f"[POST] Guardando en caché: {key}")
            r.set(key, json.dumps(value))
            return jsonify({"mensaje": "Guardado en caché"}), 201
        except Exception as e:
            print(f"[ERROR] No se pudo guardar en Redis: {e}")
            return jsonify({"error": "Fallo en Redis"}), 500
    else:
        print("[ERROR] POST mal formado:", data)
        return jsonify({"error": "Faltan datos"}), 400




@app.route("/cache", methods=["GET"])
def obtener_de_cache():
    key = request.args.get("key")
    if not key:
        return jsonify({"error": "Falta la clave"}), 400
    value = r.get(key)
    if value:
        return jsonify(json.loads(value)), 200
    else:
        return jsonify({"error": "No encontrado"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
