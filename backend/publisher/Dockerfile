FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install Adafruit_DHT --install-option="--force-pi"
    
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy publisher code
COPY . .

# Default MQTT values (override via environment in docker-compose)
ENV MQTT_HOST=mqtt-broker
ENV MQTT_PORT=1883

# Run the publisher script
CMD ["python", "publisher.py"]
