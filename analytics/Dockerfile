FROM python:3.10-slim

WORKDIR /app
RUN mkdir -p /logs/analytics_service

COPY ./src ./src
COPY ./sample_data ./sample_data
COPY requirements.txt .
COPY .env .


RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/analytics_job.py"]
