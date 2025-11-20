import paho.mqtt.client as mqtt
from datetime import datetime

IP = "10.183.240.41" #change as needed

def on_message(client, any, msg):
	message = msg.payload.decode()
	with open("sensor_data.txt", "a") as f:
		f.write(f"{message}\n")
	print(f"Received: {message}")
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(IP, 1883, keepalive = 60)
client.subscribe("humidity/data")
client.loop_start()
try:
	while True:
		pass
except KeyboardInterrupt:
	print("Exited")
	client.loop_stop()
	client.disconnect()
