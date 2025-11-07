FROM python:3.8-slim

# Install system dependencies required for building Python packages.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        git \
        iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for Project AirSim assets.
WORKDIR /opt/projectairsim

ENV PYTHONUNBUFFERED=1

# Upgrade packaging tools and install build prerequisites using the system interpreter.
RUN pip install --upgrade pip \
    && pip install setuptools wheel cmake

# Copy the Project AirSim Python client and supporting scripts.
COPY projectairsim ./projectairsim
COPY example_user_scripts ./example_user_scripts
COPY docker_entrypoint.sh ./entrypoint.sh

# Install the Project AirSim Python client in editable mode.
RUN pip install -e ./projectairsim

# Ensure the entrypoint script is executable.
RUN chmod +x /opt/projectairsim/entrypoint.sh

ENTRYPOINT ["/opt/projectairsim/entrypoint.sh"]
