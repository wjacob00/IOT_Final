import paho.mqtt.client as mqtt
import os
from datetime import datetime

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

def on_message(client, any, msg):
	message = msg.payload.decode()
	with open("sensor_data.txt", "a") as f:
		f.write(f"{message}\n")
	print(f"Received: {message}")
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.subscribe("sensors                          /data")
client.loop_start()
try:
	while True:
		pass
except KeyboardInterrupt:
	print("Exited")
	client.loop_stop()
	client.disconnect()

