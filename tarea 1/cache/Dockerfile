FROM python:3.10-slim

WORKDIR /app

COPY cache_recibidor.py .

RUN pip install flask redis

EXPOSE 5000

CMD ["python", "cache_recibidor.py"]

