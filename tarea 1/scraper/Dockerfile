FROM python:3.12-slim
WORKDIR /app
COPY scraper_collector.py .
RUN pip install requests
CMD [ "python", "scraper_collector.py" ]