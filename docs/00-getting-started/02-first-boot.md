# Lesson 02 - First boot from existing eMMC

## Overview

Boot an existing operating system, collect a read-only inventory, and shut down
without corrupting storage.

## Learning Objectives

- Identify distribution, kernel, architecture, memory, mounts, and storage.
- Prove which block device supplies `/` and distinguish SD from eMMC.
- Collect boot errors and perform a clean shutdown.

## Prerequisites

[Lesson 01](01-board-overview.md), a known-safe supply, and bootable eMMC.
Remove microSD **while powered off** to make this experiment unambiguous.
Use a UART console, local display/keyboard, or an already configured SSH path.
If no login credentials are known, consult the installed image's release notes
or the previous owner; use microSD recovery rather than guess passwords.

## Theory

Boot activity includes ROM/U-Boot, kernel startup, filesystem mounting, and
services. User LEDs may indicate heartbeat/storage/CPU activity, but their
triggers depend on the image and are not a universal boot-success code.
Serial output is more informative than an LED pattern.

Distribution and kernel are independently versioned. CPU architecture reported
by `uname -m` is the kernel's architecture, not proof that an arbitrary binary
matches the target's libc or ABI.

## Hands-on Lab

1. **Powered off:** disconnect unnecessary peripherals/capes. Connect recovery
   UART correctly if available. Connect Ethernet to the home router/switch.
2. Apply power. Look for the power indicator and boot activity; wait for a login
   prompt or services. Do not assume every image exposes USB networking or boots
   in a fixed number of seconds.
3. Log in using the configured account. Run on **BBB**:

   ```bash
   cat /etc/os-release
   uname -a
   uname -m
   free -h
   ```

   `/etc/os-release` names the distribution; `uname -a` records kernel release
   and build metadata; `uname -m` commonly reports `armv7l` on BBB Linux.
   `free -h` distinguishes total/used/available RAM and swap. Available memory
   includes reclaimable cache; nominal 512 MB is not all available to applications.
4. **BBB**, inspect devices and mounts:

   ```bash
   lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
   findmnt /
   df -h
   cat /proc/cmdline
   ```

   `lsblk` shows disks and partitions; older util-linux may require `MOUNTPOINT`
   instead of `MOUNTPOINTS`. `findmnt /` identifies the actual root mount.
   `df -h` reports filesystem capacity, not raw disk capacity. The kernel command
   line may use a UUID or PARTUUID rather than a literal device name.
5. **BBB**, identify MMC devices without assuming numbering:

   ```bash
   for device in /sys/block/mmcblk*; do
       [ -r "$device/device/type" ] || continue
       printf '%s: ' "${device##*/}"
       cat "$device/device/type"
       cat "$device/device/name"
   done
   ```

   The card `type` normally reports `MMC` for eMMC and `SD` for microSD.
   Correlate these results with size, `lsblk`, and `findmnt`; `mmcblkNboot0/1`
   are eMMC boot areas, not the main user-area partitions. Stop if observations
   disagree.
6. **BBB**, inspect logs:

   ```bash
   dmesg
   journalctl -b -p warning --no-pager
   ```

   `dmesg` is the kernel ring buffer; `journalctl -b` selects this boot on systemd
   images. Permission restrictions may require `sudo dmesg` or authorized journal
   group membership. On non-systemd images, inspect their configured logs.
   A warning is a clue, not automatically a fatal error.
7. Optionally run the repository's read-only inventory utility from its root:

   ```bash
   bash scripts/target/board-info.sh
   ```

8. **BBB**, after saving work:

   ```bash
   sudo shutdown -h now
   ```

   Wait for the console's halt/power-down message and storage activity to stop
   before disconnecting power. Network disappearance alone does not prove halt.

## How It Works

The kernel exposes device topology through sysfs, mounts through the VFS, and
memory/process state through procfs. A clean shutdown stops services, flushes
pending writes, and unmounts filesystems. Removing power during writes can damage
the filesystem even when applications appeared finished.

## Verification

Save actual distribution/kernel information, observed MMC `type` and size,
`findmnt /`, and important warnings. With no microSD inserted and a normal
block-backed root mount, correlate the root source with the MMC device; do not
claim eMMC boot solely from an LED. UART should show orderly shutdown.

## Troubleshooting

- **No LEDs or repeated resets:** inspect supply, cable, connector, and power
  budget before replacing software.
- **No login or SSH address:** use UART/local console. DHCP lease information
  comes from your router; no fixed IP is assumed.
- **eMMC does not boot:** follow [microSD recovery](03-microsd-boot.md), not an
  unverified disk-writing command.
- **Root appears as overlay or mapper device:** inspect `findmnt`, `lsblk`, and
  the backing mounts before deciding which storage holds the root filesystem.

## Exercises

Explain why `df` and `lsblk` show different capacities. Identify one kernel
warning and determine whether the related device is actually needed in this lab.

## Key Takeaways

Observe running software and root media rather than infer them from defaults.
Read-only inventory is the baseline for every later experiment.

## Further Reading

- [BeagleBoard getting started](https://www.beagleboard.org/getting-started)
- [util-linux upstream](https://github.com/util-linux/util-linux)
- [systemd journalctl manual](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

## Lab Status

**Documented but not tested.** No actual eMMC boot, inventory output, or shutdown
has been verified on physical BBB hardware.
