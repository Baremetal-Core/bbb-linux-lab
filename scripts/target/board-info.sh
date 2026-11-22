#!/usr/bin/env bash
set -uo pipefail

show() {
    printf '\n== %s ==\n' "$*"
    "$@" || echo "Unavailable or unsupported; inspect this image manually."
}
if [[ -r /proc/device-tree/model ]]; then
    printf 'Device Tree model: '
    tr -d '\0' < /proc/device-tree/model
    printf '\n'
fi
show cat /etc/os-release
show uname -a
show uname -m
show free -h
show lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
show findmnt /
show df -h
for device in /sys/block/mmcblk*; do
    [[ -d $device/device ]] || continue
    printf '\n== %s ==\n' "${device##*/}"
    for attribute in type name cid; do
        [[ -r $device/device/$attribute ]] || continue
        printf '%s: ' "$attribute"
        cat "$device/device/$attribute"
    done
done
