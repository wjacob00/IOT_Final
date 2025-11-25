import os
import time
import random
import paho.mqtt.client as mqtt
import adafruit_dht
import board

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

try:
    import adafruit_dht
    HAS_DHT = True
except ImportError:
    adafruit_dht = None
    HAS_DHT = False

DHT_PIN = 4  # or whatever you would use on a real Pi

client = mqtt.Client()

def connect():
    client.connect(MQTT_HOST, MQTT_PORT, 60)

def read_sensors():
    if HAS_DHT:
        sensor = adafruit_dht.DHT11(board.D22)
        humidity, temperature =sensor.humidity, sensor.temperature
        if humidity is None or temperature is None:
            # fallback if sensor read fails
            humidity = random.uniform(30, 60)
            temperature = random.uniform(20, 30)
    else:
        # running on PC / no Adafruit_DHT -> fake data
        humidity = random.uniform(30, 60)
        temperature = random.uniform(20, 30)

    cpu_temp = random.uniform(40, 60)  # TODO: replace with real CPU temp read if you want
    return temperature, humidity, cpu_temp

def main():
    time.sleep(5)
    connect()
    while True:
        temp, hum, cpu = read_sensors()
        msg - f"{temp},{hum},{cpu}"
        client.publish("sensors/data", msg)
        time.sleep(5)

if __name__ == "__main__":
    main()
