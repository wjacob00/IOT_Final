#!/usr/bin/env bash
# Setup for Raspberry Pi OS / Debian
# - Installs Docker & Docker Compose (handles i386 specially)
# - Installs Python3 + pip + PyYAML
# - Runs docker/generate_yaml.py to create docker-compose.yml + prometheus.yml
# - Builds and starts containers

set -euo pipefail

# Always run from the folder this script is in (project root)
cd "$(dirname "${BASH_SOURCE[0]}")"

# ---------- helpers ----------

need_cmd() { command -v "$1" >/dev/null 2>&1; }

require_root_or_sudo() {
    if [ "$EUID" -ne 0 ]; then
        if ! need_cmd sudo; then
            echo "This script needs root or sudo. Please install sudo or run as root." >&2
            exit 1
        fi
    fi
}

run_root() {
    if [ "$EUID" -ne 0 ]; then
        sudo "$@"
    else
        "$@"
    fi
}

# ---------- sanity checks ----------

if ! need_cmd apt-get; then
    echo "This script is for Debian / Raspberry Pi OS (apt-get). Aborting." >&2
    exit 1
fi

require_root_or_sudo

ARCH=$(dpkg --print-architecture)
CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")

echo "Detected architecture: $ARCH, codename: $CODENAME"

# ---------- Docker install ----------

if need_cmd docker; then
    echo "Docker already installed: $(docker --version)"
else
    if [ "$ARCH" = "i386" ]; then
        echo "32-bit x86 (i386) detected."
        echo "Using Debian docker.io + docker-compose (Docker upstream does not support i386)."

        # Remove incompatible Docker upstream repo if it exists
        if [ -f /etc/apt/sources.list.d/docker.list ]; then
            echo "Removing incompatible /etc/apt/sources.list.d/docker.list ..."
            run_root rm -f /etc/apt/sources.list.d/docker.list
        fi

        run_root apt-get update -y
        run_root apt-get install -y docker.io docker-compose

        run_root systemctl enable docker
        run_root systemctl start docker
    else
        echo "Non-i386 architecture: using official Docker repo."
        run_root apt-get update -y
        run_root apt-get install -y ca-certificates curl gnupg lsb-release

        run_root install -m 0755 -d /etc/apt/keyrings
        if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
            curl -fsSL https://download.docker.com/linux/debian/gpg \
                | run_root gpg --batch --yes --dearmor -o /etc/apt/keyrings/docker.gpg
        fi

        echo \
"deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
 ${CODENAME} stable" \
            | run_root tee /etc/apt/sources.list.d/docker.list >/dev/null

        run_root apt-get update -y
        run_root apt-get install -y \
            docker-ce docker-ce-cli containerd.io \
            docker-buildx-plugin docker-compose-plugin

        run_root systemctl enable docker
        run_root systemctl start docker
    fi

    echo "Docker installed: $(docker --version)"
fi

# ---------- docker compose / docker-compose detection ----------

COMPOSE_CMD=""

if docker compose version >/dev/null 2>&1; then
    echo "docker compose plugin available: $(docker compose version)"
    COMPOSE_CMD="docker compose"
elif need_cmd docker-compose; then
    echo "docker-compose (v1) available: $(docker-compose --version)"
    COMPOSE_CMD="docker-compose"
else
    echo "Installing docker-compose package from Debian..."
    run_root apt-get update -y
    run_root apt-get install -y docker-compose || true

    if need_cmd docker-compose; then
        echo "docker-compose installed: $(docker-compose --version)"
        COMPOSE_CMD="docker-compose"
    else
        echo "WARNING: docker-compose still not found. You will need to install it manually." >&2
    fi
fi

# ---------- add current user to docker group ----------

if getent group docker >/dev/null 2>&1; then
    if id -nG "$USER" | grep -qw docker; then
        echo "User '$USER' is already in the docker group."
    else
        echo "Adding user '$USER' to docker group..."
        run_root usermod -aG docker "$USER"
        echo "You must log out and log back in for group changes to take effect."
    fi
else
    echo "Creating docker group and adding user..."
    run_root groupadd docker || true
    run_root usermod -aG docker "$USER"
    echo "You must log out and log back in for group changes to take effect."
fi

# ---------- Python + PyYAML ----------

if need_cmd python3; then
    echo "Python3 already installed: $(python3 --version)"
else
    echo "Installing Python3..."
    run_root apt-get update -y
    run_root apt-get install -y python3 python3-pip python3-venv
fi

if need_cmd pip3; then
    echo "pip3 already installed."
else
    echo "Installing pip3..."
    run_root apt-get install -y python3-pip
fi

# Install PyYAML for current user
if python3 -c "import yaml" >/dev/null 2>&1; then
    echo "PyYAML already installed."
else
    echo "Installing PyYAML (needed for YAML generation)..."
    pip3 install --user pyyaml
fi

# ---------- run the generator ----------

GENERATOR="./docker/generate_yaml.py"

if [ -f "$GENERATOR" ]; then
    echo "Running Python generator: $GENERATOR"
    python3 "$GENERATOR"
    echo "Generator finished. docker-compose.yml and prometheus.yml should be in $(pwd)."
else
    echo "WARNING: $GENERATOR not found in $(pwd)."
    echo "Expected layout:"
    echo "  $(pwd)/set_docker_env.sh"
    echo "  $(pwd)/docker/generate_yaml.py"
    echo "  $(pwd)/config/stack_config.py"
    exit 1
fi

# ---------- build & start containers ----------

if [ -n "$COMPOSE_CMD" ]; then
    echo "Building and starting containers with: $COMPOSE_CMD up -d --build"
    run_root $COMPOSE_CMD up -d --build
else
    echo "WARNING: docker-compose / docker compose not available; stack not started." >&2
fi

echo
echo "✅ Setup script complete."
echo "If you were just added to the docker group, log out and back in for future non-sudo docker commands."
