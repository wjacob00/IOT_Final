FROM python:3.9-slim

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
