FROM python:3.12-slim

WORKDIR /app

COPY generador_trafico.py .

RUN pip install --no-cache-dir pymongo numpy matplotlib scipy requests

CMD ["python", "generador_trafico.py", "poisson"]
