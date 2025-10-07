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
# to "auto" (the default). Prefer the WSL gateway returned by `ip route` and
# fall back to the first DNS entry in /etc/resolv.conf or host.docker.internal
# when discovery fails so the user can still override it manually.
if [[ "${PROJECTAIRSIM_HOST:-auto}" == "auto" ]]; then
    gateway_ip=""

    if command -v ip >/dev/null 2>&1; then
        gateway_ip=$(ip route show | awk '/^default/ {print $3; exit}' || true)
    fi

    if [[ -z "${gateway_ip}" ]]; then
        gateway_ip=$(awk '/nameserver/ {print $2; exit}' /etc/resolv.conf || true)
    fi

    if [[ -z "${gateway_ip}" ]]; then
        gateway_ip="host.docker.internal"
    fi

    export PROJECTAIRSIM_HOST="${gateway_ip}"
fi

exec "$@"
