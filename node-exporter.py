#!/usr/bin/env python3
from prometheus_client import Gauge, start_http_server
import time
import re
import os
base = os.path.expanduser("~/Test/IOY_Final/backend/subscriber_stack")
data_file = os.path.join(base, "sensor_data.txt")

# Prometheus metrics
temperature_gauge = Gauge("sensor_temperature_celsius", "Temperature in Celsius")
humidity_gauge = Gauge("sensor_humidity_percent", "Humidity percentage")
cpu_gauge = Gauge("cpu_temperature_percent", "CPU Temperature percentage")

def extract_last_value(filename):
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            if not lines:
                return None
            last_line = lines[-1] .strip()
            return last_line
    except Exception as e:
        print("Error reading file: ", e)
        return None

def update_metrics():
    message = extract_last_value(data_file)
    if message is None:
        print("No data found.")
        return

    metrics = message.split(",")
    t = float(metrics[0])
    h = float(metrics[1])
    cpu = float(metrics[2])

    temperature_gauge.set(t)
    humidity_gauge.set(h)
    cpu_gauge.set(cpu)

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8000)
    print("Serving metrics on http://localhost:8000/metrics")
    while True:
        update_metrics()
        time.sleep(5)  # update every 5 seconds
