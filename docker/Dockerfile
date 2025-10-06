FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install build prerequisites and runtime libraries required by the
# Project AirSim Python client dependencies.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the client sources into the image so we can install the package and
# provide an immutable fallback even when the repository is mounted as a
# volume at runtime.
COPY projectairsim /opt/projectairsim
COPY docker/entrypoint.sh /opt/entrypoint.sh

WORKDIR /opt/projectairsim

# Install the Project AirSim package and its Python dependencies.
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && chmod +x /opt/entrypoint.sh

# Working directory used when the container starts. When docker compose is
# used, the repository is mounted at /workspace so that local changes are
# visible inside the container.
RUN mkdir -p /workspace

WORKDIR /workspace

ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["bash"]
