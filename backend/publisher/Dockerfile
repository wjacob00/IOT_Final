FROM python:3.9-bullseye

# Install required system packages for GPIO and DHt
RUN apt-get update && apt-get install -y python3-dev build-essential libgpiod-dev && rm -rf /var/lib/apt/lists/*
    
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
CMD ["python", "-u", "publisher.py"]
