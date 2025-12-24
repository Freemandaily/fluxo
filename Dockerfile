FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120  -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "maun:app", "--host", "0.0.0.0", "--port", "8000"]
