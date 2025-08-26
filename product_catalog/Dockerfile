FROM python:3.10-slim

WORKDIR /app
RUN mkdir -p /logs/product_catalog

COPY ./src ./src
COPY ./sample_data ./sample_data
COPY requirements.txt .
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT