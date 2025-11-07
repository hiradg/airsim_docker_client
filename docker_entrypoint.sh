#!/usr/bin/env bash
set -euo pipefail

# Derive the Windows host IP accessible from WSL2.
WSL_GATEWAY="$(ip route show | awk '/^default/ {print $3; exit}')"
WSL_HOST_IP=${WSL_HOST_IP:-$WSL_GATEWAY}

PORT_TOPICS=${PORT_TOPICS:-8989}
PORT_SERVICES=${PORT_SERVICES:-8990}

if [[ -n "${1-}" ]]; then
  echo "Overriding connection parameters with user-provided arguments: $*"
  exec python /opt/projectairsim/example_user_scripts/hello_drone.py "$@"
fi

echo "Connecting to Project AirSim services via ${WSL_HOST_IP}:${PORT_TOPICS}/${PORT_SERVICES}"

exec python /opt/projectairsim/example_user_scripts/hello_drone.py \
  --address "${WSL_HOST_IP}" \
  --port-topics "${PORT_TOPICS}" \
  --port-services "${PORT_SERVICES}"
