FROM python:3.9-slim

WORKDIR /app

# --- system deps + supervisor + prometheus ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg supervisor prometheus \
  && rm -rf /var/lib/apt/lists/*

# --- install grafana ---
RUN mkdir -p /usr/share/keyrings \
  && curl -fsSL https://apt.grafana.com/gpg.key | gpg --dearmor > /usr/share/keyrings/grafana.gpg \
  && echo "deb [signed-by=/usr/share/keyrings/grafana.gpg] https://apt.grafana.com stable main" \
     > /etc/apt/sources.list.d/grafana.list \
  && apt-get update && apt-get install -y --no-install-recommends grafana \
  && rm -rf /var/lib/apt/lists/*

# --- python deps (subscriber + prometheus_client) ---
COPY subscriber_requirements.txt .
RUN pip install --no-cache-dir -r subscriber_requirements.txt

# --- app code ---
COPY . .

# --- required runtime files (you must add these in this folder) ---
# supervisord.conf: starts subscriber + prometheus + grafana
# grafana-datasource.yaml: auto-provisions Prometheus datasource
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY grafana-datasource.yaml /etc/grafana/provisioning/datasources/datasource.yaml

# data dirs
RUN mkdir -p /prometheus /var/lib/grafana \
  && chown -R 472:472 /var/lib/grafana

# Environment from docker-compose
ENV MQTT_HOST=mqtt-broker
ENV MQTT_PORT=1883
ENV METRICS_PORT=9100

# Expose: metrics, prometheus UI, grafana UI
EXPOSE 9100 9090 3000

CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
