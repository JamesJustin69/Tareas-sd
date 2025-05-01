# Monitoreo de live-events de Waze

Este sistema permite simular, almacenar y gestionar eventos de tráfico vial en tiempo real utilizando datos de Waze. Incluye un generador de tráfico, un recolector de datos, almacenamiento en MongoDB, y un sistema de caché con Redis.

---

## Requisitos

- Docker y Docker Compose instalados y funcionandoo

---

##  Ejecución del sistema

1. **Levantamiento de todos los contenedores:**

```bash
docker-compose up --build
```

Esto construye y ejecuta los servicios, los cuales son el scraper, cargador, generador y el caché.

2. **Cambiar distribución de generación de tráfico:**

Por defecto se usa la distribución **normal**, Si se quiere cambiar de distribución a **Poisson**, se modifica el siguiente archivo `generador/Dockerfile`:

```dockerfile
CMD ["python", "generador_trafico.py", "poisson"]
```

## 🗃️ Estructura de directorios

```
.
├── docker-compose.yml
├── generador/
│   ├── Dockerfile
│   └── generador_trafico.py
├── recolector/
│   ├── scraper_collector.py
│   └── eventos_waze.json
├── mongo/
│   └── copiar_a_mongo.py
├── cache/
│   ├── cache_recibidor.py
│   └── Dockerfile
```


