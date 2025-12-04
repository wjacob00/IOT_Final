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

# ---- figure out project + config paths based on THIS file ----
THIS_FILE = Path(__file__).resolve()
DOCKER_DIR = THIS_FILE.parent
PROJECT_ROOT = DOCKER_DIR.parent
CONFIG_DIR = PROJECT_ROOT / "config"

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
            # Mount directories (more robust than file-to-file mounts)
            "volumes": [
                f"{cfg.MQTT_CONFIG_DIR}:/mosquitto/config",
                f"{cfg.MQTT_DATA_DIR}:/mosquitto/data",
                f"{cfg.MQTT_LOG_DIR}:/mosquitto/log",
            ],
            "restart": "unless-stopped",
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
            "privileged": True,
            "devices": [
                "/dev/gpiomem:/dev/gpiomem",
                "/dev/mem:/dev/mem",
            ],
            "volumes": [
                "/proc:/host_proc:ro",
                "/sys:/host_sys:ro",
                "/boot:/boot:ro",
                "/sys/firmware/devicetree/base:/device-tree:ro",
            ],
            "environment": {
                # ✅ Use Docker DNS name, not host IP
                "MQTT_HOST": getattr(cfg, "PUBLISHER_MQTT_HOST", "mqtt-broker"),
                "MQTT_PORT": str(getattr(cfg, "PUBLISHER_MQTT_PORT", cfg.MQTT_CONTAINER_PORT)),
                # ✅ Remove the stray ":" in env var names
                "PROCFS_MOUNT": "/host_proc",
                "SYSFS_MOUNT": "/host_sys",
            },
            "depends_on": ["mqtt-broker"],
            "restart": "unless-stopped",
        },

        "subscriber-stack": {
            "image": cfg.SUBSCRIBER_STACK_IMAGE,
            "build": cfg.SUBSCRIBER_STACK_BUILD_CONTEXT,
            "container_name": "subscriber-stack",
            "ports": [
                f"{cfg.GRAFANA_PORT_HOST}:{cfg.GRAFANA_PORT_CONTAINER}",
                f"{cfg.PROMETHEUS_PORT_HOST}:{cfg.PROMETHEUS_PORT_CONTAINER}",
            ],
            "environment": {
                # ✅ Use Docker DNS name, not host IP
                "MQTT_HOST": getattr(cfg, "SUBSCRIBER_MQTT_HOST", "mqtt-broker"),
                "MQTT_PORT": str(getattr(cfg, "SUBSCRIBER_MQTT_PORT", cfg.MQTT_CONTAINER_PORT)),
                "METRICS_PORT": str(cfg.SUBSCRIBER_METRICS_PORT),

                # Required to embed dashboards in iframe
                "GF_SECURITY_ALLOW_EMBEDDING": "true",

                # Required so browser can reach Grafana via host IP
                "GF_SERVER_HTTP_ADDR": "0.0.0.0",
                "GF_SERVER_DOMAIN": "10.183.244.90",
                "GF_SERVER_ROOT_URL": "http://10.183.244.90:3000",
                "GF_SERVER_SERVE_FROM_SUB_PATH": "true",

                # Required to bypass login on iframes
                "GF_AUTH_ANONYMOUS_ENABLED": "true",
                "GF_AUTH_ANONYMOUS_ORG_ROLE": "Viewer",
            },
            "volumes": [
                f"./prometheus.yml:{cfg.PROMETHEUS_CONFIG_MOUNT_PATH}:ro",
                f"{cfg.GRAFANA_DATA_DIR}:/var/lib/grafana",
                f"./backend/subscriber_stack/sensor_data.txt:/app/sensor_data.txt",
            ],
            "extra_hosts": {
                "host.docker.internal": "host-gateway"
            },
            "depends_on": ["mqtt-broker"],
            "restart": "unless-stopped",
        },
    }

    for svc in services.values():
        svc["networks"] = [cfg.NETWORK_NAME]

    # Compose v2 ignores "version", so omit it to avoid warnings.
    return {
        "services": services,
        "networks": {cfg.NETWORK_NAME: {"driver": "bridge"}},
    }


def build_prometheus_config() -> dict:
    return {
        "global": {"scrape_interval": "5s", "evaluation_interval": "5s"},
        "scrape_configs": [
            {
                "job_name": "subscriber",
                "static_configs": [
                    {"targets": [f"host.docker.internal:{cfg.SUBSCRIBER_METRICS_PORT}"]}
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
    write_yaml(PROJECT_ROOT / "docker-compose.yml", build_docker_compose())
    write_yaml(PROJECT_ROOT / "prometheus.yml", build_prometheus_config())


if __name__ == "__main__":
    main()
