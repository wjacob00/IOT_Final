#!/usr/bin/env python3
"""
Generate docker-compose.yml and prometheus.yml from config/stack_config.py.

Expected layout (relative to project root):
  set_docker_env.sh
  docker/generate_yaml.py
  config/stack_config.py
"""

from pathlib import Path
import sys
import yaml
import socket

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# ---- figure out project + config paths based on THIS file ----

THIS_FILE = Path(__file__).resolve()          # e.g. /home/student/final_project/docker/generate_yaml.py
DOCKER_DIR = THIS_FILE.parent                 # /home/student/final_project/docker
PROJECT_ROOT = DOCKER_DIR.parent              # /home/student/final_project
CONFIG_DIR = PROJECT_ROOT / "config"          # /home/student/final_project/config

if str(CONFIG_DIR) not in sys.path:
    sys.path.insert(0, str(CONFIG_DIR))

try:
    import stack_config as cfg
except ModuleNotFoundError as e:
    raise SystemExit(
        f"Could not import stack_config from {CONFIG_DIR}. "
        f"Make sure config/stack_config.py exists.\n"
        f"Original error: {e}"
    )


def build_docker_compose() -> dict:
    services = {
        "mqtt-broker": {
            "image": cfg.MQTT_IMAGE,
            "container_name": "mqtt-broker",
            "ports": [f"{cfg.MQTT_HOST_PORT}:{cfg.MQTT_CONTAINER_PORT}"],
            "volumes": [
                f"{cfg.MQTT_CONFIG_DIR}:/mosquitto/config",
                f"{cfg.MQTT_DATA_DIR}:/mosquitto/data",
                f"{cfg.MQTT_LOG_DIR}:/mosquitto/log",
            ],
            "restart": "unless-stopped",
           # f"command:" "sh -c /"chmod 700{cfg.MQTT_DATA_DIR} /mosquitto/data/"", 
            
        },
        "react-ui": {
            "image": cfg.REACT_IMAGE,
            "build": cfg.REACT_BUILD_CONTEXT,
            "container_name": "react-ui",
            "ports": [f"{cfg.REACT_HOST_PORT}:{cfg.REACT_CONTAINER_PORT}"],
            "depends_on": ["mqtt-broker", "subscriber-stack"],
            "restart": "unless-stopped",
        },
        "publisher": {
            "image": cfg.PUBLISHER_IMAGE,
            "build": cfg.PUBLISHER_BUILD_CONTEXT,
            "container_name": "publisher",
            "privileged": "true",
            "devices":[
			   "/dev/gpiomem:/dev/gpiomem",
			   "/dev/mem:/dev/mem",
			  ],
			"volumes":[
			   "/proc:/host_proc:ro",
			   "/sys:/host_sys:ro",
			   "/boot:/boot:ro",
			   "/sys/firmware/devicetree/base:/device-tree:ro",
			  ],
            "environment": {
                "MQTT_HOST": ip_address,
                "MQTT_PORT": str(cfg.PUBLISHER_MQTT_PORT),
                "PROCFS_MOUNT:": "/host_proc",
				"SYSFS_MOUNT:": "/host_sys",
            },
            "depends_on": ["mqtt-broker"],
            "restart": "unless-stopped",
        },
        "subscriber-stack": {
            # subscriber app + Prometheus metrics (and later Grafana if you want)
            "image": cfg.SUBSCRIBER_STACK_IMAGE,
            "build": cfg.SUBSCRIBER_STACK_BUILD_CONTEXT,
            "container_name": "subscriber-stack",
            "ports": [
                f"{cfg.GRAFANA_PORT_HOST}:{cfg.GRAFANA_PORT_CONTAINER}",
                f"{cfg.PROMETHEUS_PORT_HOST}:{cfg.PROMETHEUS_PORT_CONTAINER}",
            ],
            "environment": {
                "MQTT_HOST": ip_address,
                "MQTT_PORT": str(cfg.SUBSCRIBER_MQTT_PORT),
                "METRICS_PORT": str(cfg.SUBSCRIBER_METRICS_PORT),
            },
            "volumes": [
                f"./prometheus.yml:{cfg.PROMETHEUS_CONFIG_MOUNT_PATH}:ro",
                f"{cfg.GRAFANA_DATA_DIR}:/var/lib/grafana",
            ],
            "depends_on": ["mqtt-broker"],
            "restart": "unless-stopped",
        },
    }

    for svc in services.values():
        svc["networks"] = [cfg.NETWORK_NAME]

    return {
        "version": "3.3",   # compatible with docker-compose 1.25.0
        "services": services,
        "networks": {cfg.NETWORK_NAME: {"driver": "bridge"}},
    }


def build_prometheus_config() -> dict:
    return {
        "global": {
            "scrape_interval": "5s",
            "evaluation_interval": "5s",
        },
        "scrape_configs": [
            {
                "job_name": "subscriber",
                "static_configs": [
                    {
                        "targets": [
                            f"subscriber-stack:{cfg.SUBSCRIBER_METRICS_PORT}",
                        ],
                    }
                ],
            }
        ],
    }


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
    print(f"Wrote {path}")


def main():
    compose = build_docker_compose()
    prom_cfg = build_prometheus_config()

    write_yaml(PROJECT_ROOT / "docker-compose.yml", compose)
    write_yaml(PROJECT_ROOT / "prometheus.yml", prom_cfg)


if __name__ == "__main__":
    main()
