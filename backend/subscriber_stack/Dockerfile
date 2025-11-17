FROM python:3.9-slim

WORKDIR /app

# Install dependencies for subscriber + Prometheus client
COPY subscriber_requirements.txt .
RUN pip install --no-cache-dir -r subscriber_requirements.txt

# Copy subscriber code
COPY . .

# Environment from docker-compose:
#   MQTT_HOST, MQTT_PORT, METRICS_PORT
ENV MQTT_HOST=mqtt-broker
ENV MQTT_PORT=1883
ENV METRICS_PORT=9100

# Expose the metrics HTTP port (Prometheus scrapes this)
EXPOSE 9100

# By default run subscriber; inside it you should:
# - connect to MQTT
# - expose /metrics via prometheus_client on METRICS_PORT
CMD ["python", "subscriber.py"]
