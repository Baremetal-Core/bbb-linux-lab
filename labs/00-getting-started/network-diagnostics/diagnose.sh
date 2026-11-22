#!/usr/bin/env bash
set -uo pipefail

if [[ $# -gt 1 || ${1:-} == -* ]]; then
    echo "Usage: $0 [DNS_NAME] (optional DNS lookup; no configuration changes)" >&2
    exit 2
fi
run() {
    printf '\n== %s ==\n' "$*"
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Unavailable: $1"
        return
    fi
    "$@" || echo "Command failed or not supported on this image."
}
run ip -brief link
run ip -brief addr
run ip route
run ip neigh
run cat /etc/resolv.conf
run systemctl is-active NetworkManager systemd-networkd networking
if [[ $# -eq 1 ]]; then
    run getent ahostsv4 "$1"
fi
