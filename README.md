# IoT Sensor Stack – Docker (Raspbian i386)

**Command to start up the project:**
  - chmod +x set_docler_env.sh
  - ./set_docker_env.sh

___

This project spins up a full IoT pipeline using Docker:

- **Mosquitto** MQTT broker
- **Python publisher** that sends sensor data over MQTT
- **Python subscriber** that exports the data as **Prometheus metrics**
- **React-style web UI** served from a container
- Auto-generated `docker-compose.yml` and `prometheus.yml`
- A one-shot setup script that installs Docker, docker-compose, Python deps, generates YAML, and brings the whole stack up

Designed to work on **Raspberry Pi OS / Debian Bullseye i386** (e.g., Raspberry Pi Desktop on PC)

___


##  Layout

From the project root (`~/final_project`):

```text
final_project/
├── set_docker_env.sh        # Main setup + run script
├── docker-compose.yml       # GENERATED – do not edit by hand
├── prometheus.yml           # GENERATED – do not edit by hand
├── config/
│   └── stack_config.py      # Central config for images, ports, build contexts
├── docker/
│   └── generate_yaml.py     # Generates docker-compose.yml + prometheus.yml
├── mosquitto/
│   ├── config/              # Mosquitto configs (if you add them)
│   ├── data/
│   └── log/
├── grafana-data/            # Persistent Grafana storage (for later extension)
├── frontend/
│   ├── Dockerfile           # Static web UI container (Python HTTP server)
│   └── index.html           # React-from-CDN dashboard
└── backend/
    ├── publisher/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── publisher.py
    └── subscriber_stack/
        ├── Dockerfile
        ├── subscriber_requirements.txt
        └── subscriber.py
