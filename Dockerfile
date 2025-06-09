FROM python:3.12.9-slim

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

ENV MODEL_SERVICE_URL=http://localhost:8081

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "flask", "run", "-p", "5000", "-h", "0.0.0.0", "--no-debug"]
