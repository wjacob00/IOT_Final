#!/usr/bin/env python3
from prometheus_client import Gauge, start_http_server
import time
import re
import os

data_file = os.path.join("/app/sensor_data.txt")

# Prometheus metrics
temperature_gauge = Gauge("sensor_temperature_celsius", "Temperature in Celsius")
humidity_gauge = Gauge("sensor_humidity_percent", "Humidity percentage")
cpu_gauge = Gauge("cpu_temperature_percent", "CPU Temperature percentage")

def extract_last_value(filename):
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            last_line = lines[-1] if lines else None
            return last_line
    except Exception:
        pass
    return None

def update_metrics():
    message = extract_last_value(data_file)
    metrics = message.split(",")
    t = metrics[0]
    h = metrics[1]
    cpu = metrics[2]

    t = extract_last_value(temp_file, temp_pattern)
    h = extract_last_value(hum_file, hum_pattern)
    if t is not None:
        temperature_gauge.set(t)
    if h is not None:
        humidity_gauge.set(h)
    if cpu is not None:
        cpu_gauge.set(cpu)

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8000)
    print("Serving metrics on http://localhost:8000/metrics")
    while True:
        update_metrics()
        time.sleep(5)  # update every 5 seconds
