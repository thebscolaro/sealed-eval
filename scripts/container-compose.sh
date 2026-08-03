#!/usr/bin/env bash
# Run compose with Podman if present, else Docker. Same Dockerfile / compose file names.
set -euo pipefail
if command -v podman >/dev/null 2>&1; then
  if podman compose version >/dev/null 2>&1; then
    exec podman compose "$@"
  fi
  if command -v podman-compose >/dev/null 2>&1; then
    exec podman-compose "$@"
  fi
fi
if command -v docker >/dev/null 2>&1; then
  exec docker compose "$@"
fi
echo "container-compose: need podman (compose) or docker compose" >&2
exit 1
