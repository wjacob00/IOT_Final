import os
import time
import random
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

try:
    import Adafruit_DHT
    HAS_DHT = True
except ImportError:
    Adafruit_DHT = None
    HAS_DHT = False

DHT_PIN = 4  # or whatever you would use on a real Pi

client = mqtt.Client()

def connect():
    client.connect(MQTT_HOST, MQTT_PORT, 60)

def read_sensors():
    if HAS_DHT:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT_PIN)
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
    connect()
    while True:
        temp, hum, cpu = read_sensors()
        client.publish("sensors/temperature", temp)
        client.publish("sensors/humidity", hum)
        client.publish("sensors/cpu_temp", cpu)
        time.sleep(5)

if __name__ == "__main__":
    main()
