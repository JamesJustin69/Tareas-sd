FROM python:3.12-slim
WORKDIR /app
COPY copiar_a_mongo.py .
COPY eventos_waze.json .
RUN pip install pymongo
CMD ["python", "copiar_a_mongo.py"]