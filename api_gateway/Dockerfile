FROM python:3.10-slim

WORKDIR /app


COPY ./src ./src
COPY requirements.txt .
COPY .env .


RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
