# Project AirSim Docker Client

This directory contains a Docker based workflow for running the Project AirSim
Python client inside WSL2 while the AirSim simulation continues to run on the
Windows host. The container talks to the host through TCP which allows the
client to publish and subscribe to the AirSim simulation topics.

## Prerequisites

* Windows 11 with WSL2 and Docker Desktop installed.
* The AirSim fork [`iamaisim/ProjectAirSim`](https://github.com/iamaisim/ProjectAirSim)
  running on the Windows host.
* This repository checked out inside WSL2 (for example at
  `/home/<user>/projects/airsim_docker_client`).

## Build the client image

```bash
cd docker
docker compose build
```

The build installs all Python dependencies declared by the `projectairsim`
package, including `pynng`, `opencv-python`, and other scientific libraries.

## Start an interactive client shell

```bash
docker compose run --rm projectairsim-client
```

The service mounts the repository into `/workspace` and drops you into an
interactive Bash shell where you can execute any of the example scripts, e.g.

```bash
python example_user_scripts/hello_drone.py
```

### Host connectivity

The `entrypoint.sh` script resolves the Windows host IP automatically using the
default gateway exposed by `ip route` (with fallbacks to `/etc/resolv.conf` and
`host.docker.internal`). When necessary you can override the host IP and ports
in the shell before launching the container:

```bash
export PROJECTAIRSIM_HOST=192.168.0.10
export PROJECTAIRSIM_PORT_TOPICS=8989
export PROJECTAIRSIM_PORT_SERVICES=8990
docker compose run --rm projectairsim-client
```

Inside the container these values are exposed to the Python client through
environment variables, enabling TCP communication with the AirSim instance
running on Windows.

### Disable the editable install

By default the container runs `pip install --editable /workspace/projectairsim`
on startup so that code changes made on the host are reflected immediately.
When you prefer using the immutable package baked into the image, disable the
step via:

```bash
PROJECTAIRSIM_EDITABLE_INSTALL=0 docker compose run --rm projectairsim-client
```

## Stop and clean up

```bash
docker compose down --rmi local --volumes --remove-orphans
```

This removes containers created for the client, any anonymous volumes, and the
locally built image.
