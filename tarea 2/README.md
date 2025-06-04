## Requisitos

- Docker y Docker Compose instalados y funcionandoo

---

##  Ejecución del sistema

1. **Levantamiento de todos los contenedores:**

```bash
docker-compose up --build
```

Esto construye y ejecuta los servicios, los cuales son el scraper, data storage, filtering y el processing.

## 🗃️ Estructura de directorios

```
.
├── docker-compose.yml
├── almacenamiento_t2/
│   ├── copiar_a_mongo2.py
│   ├── dockerfile
│   └── eventos_wazeT2.json
├── filtrado_t2/
│   ├── dockerfile
│   └── filtrado2.py
├── modulo_pig_t2/
│   ├── dockerfile
│   └── procesamiento.pig
├── processing_t2/
│   ├── dockerfile
│   └── exportar_a_csv.py
├── scraper_t2/
│   ├── dockerfile
│   └── scraperT2.py




