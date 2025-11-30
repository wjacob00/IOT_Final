FROM python:3.9-bullseye

# Install required system packages for GPIO and DHt
#RUN apt-get update && apt-get install -y python3-dev build-essential libgpiod-dev && rm -rf /var/lib/apt/lists/*
  
RUN apt-get update && apt-get install -y \
    python3-rpi.gpio \
    && pip install paho-mqtt dht11  
WORKDIR /app

# Install dependencies
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt ! all installed above

# Copy publisher code
COPY . .

# Default MQTT values (override via environment in docker-compose)
ENV MQTT_HOST=mqtt-broker
ENV MQTT_PORT=1883

# Run the publisher script
CMD ["python", "-u", "publisher.py"]
