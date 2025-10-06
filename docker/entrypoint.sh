#!/usr/bin/env bash
set -euo pipefail

# Optionally re-install the project in editable mode so that local changes
# mounted into the container are picked up immediately.
if [[ "${PROJECTAIRSIM_EDITABLE_INSTALL:-1}" != "0" && -d /workspace/projectairsim ]]; then
    pip install --editable /workspace/projectairsim >/tmp/pip-projectairsim.log 2>&1 || {
        cat /tmp/pip-projectairsim.log >&2
        echo "Failed to install Project AirSim in editable mode" >&2
        exit 1
    }
fi

# Resolve the IP address of the Windows host when PROJECTAIRSIM_HOST is set
# to "auto" (the default). In WSL2 the Windows host is reachable through the
# first DNS entry listed in /etc/resolv.conf. Fallback to host.docker.internal
# when the lookup fails so the user can still override it manually.
if [[ "${PROJECTAIRSIM_HOST:-auto}" == "auto" ]]; then
    gateway_ip=$(awk '/nameserver/ {print $2; exit}' /etc/resolv.conf || true)
    if [[ -n "${gateway_ip}" ]]; then
        export PROJECTAIRSIM_HOST="${gateway_ip}"
    else
        export PROJECTAIRSIM_HOST="host.docker.internal"
    fi
fi

exec "$@"
