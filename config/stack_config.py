# config/stack_config.py

# Project / Docker network
PROJECT_NAME = "final_project"
NETWORK_NAME = f"{PROJECT_NAME}_iot-net"

# ───── Mosquitto broker (pulled from Docker Hub) ─────
MQTT_IMAGE = "eclipse-mosquitto:2"
MQTT_HOST_PORT = 1883
MQTT_CONTAINER_PORT = 1883

MQTT_CONFIG_FILE = "./mosquitto/config/mosquitto.conf"
MQTT_CONFIG_DIR = "./mosquitto/config"
MQTT_DATA_DIR = "./mosquitto/data"
MQTT_LOG_DIR = "./mosquitto/log"

# ───── React frontend ─────
REACT_IMAGE = f"{PROJECT_NAME}_react-ui"
REACT_BUILD_CONTEXT = "./frontend"
REACT_HOST_PORT = 8081
REACT_CONTAINER_PORT = 80

# ───── Publisher (backend/publisher) ─────
PUBLISHER_IMAGE = f"{PROJECT_NAME}_publisher"
PUBLISHER_BUILD_CONTEXT = "./backend/publisher"
PUBLISHER_MQTT_HOST = "mqtt-broker"
PUBLISHER_MQTT_PORT = 1883

# ───── Subscriber + Prometheus metrics (backend/subscriber_stack) ─────
SUBSCRIBER_STACK_IMAGE = f"{PROJECT_NAME}_subscriber_stack"
SUBSCRIBER_STACK_BUILD_CONTEXT = "./backend/subscriber_stack"
SUBSCRIBER_MQTT_HOST = "mqtt-broker"
SUBSCRIBER_MQTT_PORT = 1883

SUBSCRIBER_METRICS_PORT = 9100

PROMETHEUS_PORT_HOST = 9090
PROMETHEUS_PORT_CONTAINER = 9090

GRAFANA_PORT_HOST = 3000
GRAFANA_PORT_CONTAINER = 3000

PROMETHEUS_CONFIG_MOUNT_PATH = "/etc/prometheus/prometheus.yml"
GRAFANA_DATA_DIR = "./grafana-data"
