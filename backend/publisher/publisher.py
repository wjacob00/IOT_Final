import os
import time
import random
import paho.mqtt.client as mqtt
import json
import sys

# --------------------------- 
# REMAP PROC ND SYS FOR DOCKER
# ---------------------------

PROCFS = os.getenv("PROCFS_MOUNT", "/proc")
SYSFS = os.getenv("SYSFS_MOUNT", "/sys")

# Override paths so hardware detection libraries work
os.environ["BLINKA_FIRMWARE_DETECT"] = "1"
os.environ["BLINKA_PROC"] = PROCFS
os.environ["BLINKA_SYS"] = SYSFS

# Force Adafruit PlatformDetect to use our remapped paths
sys.path.insert(0, "/usr/local/lib/python3.9/site-packages")

# ---------------------------
# NORMAL PROGRAM IMPORTS
# ---------------------------
import RPi.GPIO as GPIO
import dht11

# ---------------------------
# INIT
# ---------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
DHT_PIN = 4  # or whatever you would use on a real Pi
dht11sensor = dht11.DHT11(pin=DHT_PIN)

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

client = mqtt.Client()

def connect():
    client.connect(MQTT_HOST, MQTT_PORT, 60)
# 30C - 50C at idle to 60C - 75°C under load
# cooling fan 23-45C

def read_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_str = f.readline().strip()
            # millidegrees Celsius
            celsius = float(temp_str) / 1000.0
            
            return celsius
    except FileNotFoundError:
        return None
        
def celsius_to_farenheight(celsius):
	farenheight = float((9 * celsius/5) + 32)
	return farenheight
	
def read_sensors():
	result = dht11sensor.read()
	if result.is_valid():
		humidity = result.humidity
		temperature = result.temperature
	else:
		# running on PC / no Adafruit_DHT -> fake data
		# fallback if sensor read fails
		humidity = random.uniform(30, 60)
		temperature = random.uniform(20, 30)

	cpu_temp = read_cpu_temp()
	if cpu_temp == None:
		random.uniform(40, 60)  # TODO: fall back
	return temperature, humidity, cpu_temp

def main():
    time.sleep(5)
    connect()
    while True:
        temp, hum, cpu = read_sensors()
        temp = round(temp,2)
        hum = round(hum,2)
        cpu = round(cpu,2)
        msg = f"{temp},{hum},{cpu}"
        client.publish("sensors/data", msg)
        time.sleep(5)

if __name__ == "__main__":
    main()
