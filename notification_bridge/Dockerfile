FROM python:3.11-slim

WORKDIR /app
RUN mkdir -p /logs/notification_bridge

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .

COPY src/ ./src/

CMD ["python", "-m", "src.main"]
