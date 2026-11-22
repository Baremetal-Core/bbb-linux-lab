#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 || ! $2 =~ ^[1-9][0-9]*$ ]]; then
    echo "Usage: $0 LED_DIRECTORY CYCLES (1..1000000)" >&2
    exit 2
fi
led=$1
cycles=$2
if [[ ${#cycles} -gt 7 ]] || ((cycles > 1000000)); then
    echo "CYCLES must be 1..1000000." >&2
    exit 2
fi
for attribute in trigger brightness max_brightness; do
    if [[ ! -r "$led/$attribute" ]]; then
        echo "Missing or unreadable LED attribute: $led/$attribute" >&2
        exit 1
    fi
done
if [[ ! -w "$led/trigger" || ! -w "$led/brightness" ]]; then
    echo "LED is not writable; run on the BBB with appropriate permission." >&2
    exit 1
fi
trigger=$(sed -n 's/.*\[\([^]]*\)\].*/\1/p' "$led/trigger")
brightness=$(< "$led/brightness")
maximum=$(< "$led/max_brightness")
if [[ -z $trigger || ! $brightness =~ ^[0-9]+$ || ! $maximum =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid LED attributes." >&2
    exit 1
fi
restore() {
    printf '%s\n' "$brightness" > "$led/brightness"
    printf '%s\n' "$trigger" > "$led/trigger"
}
trap restore EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
printf 'none\n' > "$led/trigger"
for ((i = 0; i < cycles; i++)); do
    printf '%s\n' "$maximum" > "$led/brightness"
    sleep 0.25
    printf '0\n' > "$led/brightness"
    sleep 0.25
done
