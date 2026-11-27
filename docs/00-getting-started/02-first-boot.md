# Lesson 02 - First boot from existing eMMC

## Overview

Boot the installed OS, collect a read-only inventory, and shut down cleanly.

## Learning Objectives

- Record distribution, kernel, architecture, memory, mounts, and storage.
- Prove which device supplies `/` and distinguish SD from eMMC.
- Find boot warnings and shut down without corrupting storage.

## Prerequisites

[Lesson 01](01-board-overview.md), a safe supply, and bootable eMMC. Remove
microSD **while powered off**. You need UART, a local console, or working SSH.
If credentials are unknown, use the image's release notes or
[microSD recovery](03-microsd-boot.md); do not guess passwords.

## Theory

LED patterns depend on the image's triggers and are not a universal boot code;
UART output is more informative. Distribution and kernel are versioned
independently. `uname -m` (commonly `armv7l`) reports the kernel's architecture,
not whether a given binary matches the target's libc/ABI.

## Hands-on Lab

1. **Powered off:** remove unnecessary peripherals, attach UART and Ethernet.
2. Power on and wait for a login prompt.
3. **BBB**, software and memory:

    ```bash
    cat /etc/os-release
    uname -a
    free -h
    ```

    Expect less than 512 MB total; the kernel reserves some memory.

4. **BBB**, storage and root:

    ```bash
    lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
    findmnt /
    df -h
    cat /proc/cmdline
    ```

    Older util-linux may need `MOUNTPOINT`. `root=` may be a UUID or PARTUUID.

5. **BBB**, identify MMC devices without trusting numbering:

    ```bash
    for device in /sys/block/mmcblk*; do
        [ -r "$device/device/type" ] || continue
        printf '%s: %s %s\n' "${device##*/}" \
          "$(cat "$device/device/type")" "$(cat "$device/device/name")"
    done
    ```

    `MMC` is eMMC, `SD` is microSD. `mmcblkNboot0/1` are eMMC boot areas.

6. **BBB**, warnings (may need `sudo`; `journalctl` requires systemd):

    ```bash
    dmesg --level=err,warn
    journalctl -b -p warning --no-pager
    ```

7. Optional, from the repository root: `bash scripts/target/board-info.sh`.
8. **BBB**, shut down and wait for the halt message before removing power:

    ```bash
    sudo shutdown -h now
    ```

## How It Works

sysfs exposes device topology, the VFS tracks mounts, and procfs exposes memory
and process state. Shutdown stops services, flushes writes, and unmounts
filesystems; cutting power mid-write can corrupt them.

## Verification

Save the actual OS/kernel strings, MMC types and sizes, `findmnt /`, and notable
warnings. With no card inserted, `/` resolves to the `MMC` device. UART shows an
orderly halt.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No LEDs or repeated resets | Supply, cable, connector, power budget |
| No login or unknown IP | Use UART; find the DHCP lease on the router |
| eMMC does not boot | [microSD recovery](03-microsd-boot.md) |
| Root is overlay/mapper | Inspect `findmnt` and `lsblk` for the backing device |

## Exercises

1. Why do `df` and `lsblk` report different sizes?

    ??? success "Answer"
        `lsblk` shows raw disk/partition size; `df` shows the filesystem's
        usable capacity after metadata, journal, and reserved blocks.

2. Pick one kernel warning. Does it matter for this lab?

    ??? success "Answer"
        It depends on the device. A warning about an unused peripheral (for
        example an absent cape or HDMI sink) is usually harmless here; storage
        or power warnings are not. Trace the message to its driver before
        deciding.

## Key Takeaways

Observe the running software and root media rather than infer them. This
read-only inventory is the baseline for every later experiment.

## Further Reading

- [BeagleBoard getting started](https://www.beagleboard.org/getting-started)
- [util-linux upstream](https://github.com/util-linux/util-linux)
- [journalctl manual](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

## Lab Status

**Documented but not tested.** No eMMC boot or inventory has been verified on
physical hardware.
