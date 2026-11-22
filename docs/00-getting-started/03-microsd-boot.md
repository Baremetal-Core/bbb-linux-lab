# Lesson 03 - Booting Linux from microSD

## Overview

Prepare a compatible Debian microSD image and use it as non-destructive board
boot/recovery media. Writing the card is destructive to the selected **host card**.

## Learning Objectives

- Select a BBB/AM335x image and verify an available published checksum.
- Distinguish an ordinary boot image from an eMMC flasher.
- Confirm root media after boot without relying on MMC numbering.

## Prerequisites

[Lesson 01](01-board-overview.md), known board revision, card/reader, safe power,
and ideally UART. [Lesson 02](02-first-boot.md) provides inventory commands but
a bootable eMMC is not required. Back up the card before overwriting it.

## Theory

A bootable microSD image contains a board-compatible layout and the required
bootloader/kernel/rootfs pieces. A **flasher image** additionally runs software
that installs to eMMC, often automatically at boot. Do not boot an image labeled
as a flasher merely to try Linux.

The ROM's power-on boot selection and U-Boot's later media search are separate.
A BBB may boot the desired SD image without holding BOOT. Other combinations
need the button to change ROM boot order at power-on. Do not assume the root
filesystem's location tells you where every earlier stage was loaded.

## Hands-on Lab

1. Record the printed BBB revision and current eMMC capacity, if observable.
   Open [BeagleBoard distributions](https://www.beagleboard.org/distros) or
   [BeagleBoard Imaging Utility](https://www.beagleboard.org/bb-imager).
   Select **BeagleBone Black / AM335x**, not AI-64, BeaglePlay, or another SoC.
   Read the specific Debian release notes: supported hardware, card size,
   initial account configuration, boot requirements, and **non-flasher** status.
2. **Host:** download the image using the official page's link. Record image
   filename, URL, date, and checksum URL. An image name is not a guarantee of
   compatibility; avoid a moving "latest" URL in your inventory.
3. If the publisher supplies a checksum, verify it before flashing. Example
   values below must be replaced with the publisher's actual values:

   ```bash
   IMAGE='your-downloaded-image.img.xz'
   EXPECTED_SHA256='paste-the-published-64-character-sha256-here'
   printf '%s  %s\n' "$EXPECTED_SHA256" "$IMAGE" | sha256sum -c -
   ```

   On **MacBook**:

   ```bash
   shasum -a 256 "$IMAGE"
   ```

   Compare the complete result to the published checksum of the **same artifact**.
   A compressed image's checksum differs from the decompressed image's checksum.
   If no checksum is available, record that verification limitation; do not invent
   one. A checksum detects corruption, not authenticity unless its source is trusted.
4. **Host**, identify the card by comparing before/after insertion:

   ```bash
   lsblk -o NAME,SIZE,MODEL,TRAN,TYPE,MOUNTPOINTS
   ```

   On **MacBook**, use `diskutil list` and inspect the removable device's size.
   Check that the selected target is not the host OS disk or a backup drive.
5. **Destructive to the selected card:** open the official Imaging Utility
   (or an image writer supported by the release notes), choose the reviewed
   ordinary image and the positively identified microSD target. Configure the
   initial account if the utility/release requires it. Review the target one last
   time, approve writing, wait for validation/completion, then safely eject.
   Do not copy the `.img.xz` file onto an existing filesystem as an ordinary file.

   !!! danger "Disk selection"
       This overwrites partitions on the selected device. No automatic disk-write
       script or guessed `/dev/sdX` command is provided. Unplug unrelated removable
       drives if that helps disambiguate the target.

6. **Powered-off BBB:** insert the prepared card. Apply power and watch UART.
   Try the selected image's documented normal boot procedure. If the board
   continues booting eMMC and the release/manual calls for BOOT: remove all power,
   hold BOOT while reapplying power, and release as directed by that guide.
   Merely pressing reset may not resample the ROM boot selection.
7. Log in using the selected image's account setup. **BBB**, verify:

   ```bash
   cat /etc/os-release
   uname -a
   findmnt /
   lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
   cat /proc/cmdline
   for device in /sys/block/mmcblk*; do
       [ -r "$device/device/type" ] || continue
       printf '%s: ' "${device##*/}"
       cat "$device/device/type"
   done
   ```

   Resolve the root mount to its parent disk and correlate the `SD` type.
   If it points to `MMC`, you may still be running eMMC. UUID/PARTUUID root
   arguments and overlays need further inspection.
8. Save UART boot banners to identify SPL/U-Boot where present. Shut down cleanly.
   Keep this known-good **non-flasher** card for recovery.

## How It Works

ROM finds a supported boot source; SPL initializes enough hardware to run U-Boot;
U-Boot loads the kernel and Device Tree, possibly from another device. Linux
mounts the root specified by boot configuration. A compatible disk image encodes
boot layout as well as file content.

## Verification

Record checksum comparison (or its absence), selected board/image, writer
completion, UART stages, and the actual root mount correlated with an `SD`
device. "It booted with a card inserted" is not sufficient proof of SD root.
Booting an ordinary image should not intentionally overwrite eMMC.

## Troubleshooting

- **Still boots old eMMC:** inspect root media and UART; check the image's boot
  policy and power-on BOOT procedure.
- **No SD boot:** recheck image family, checksum, card validation, supply, and
  UART errors; try a known-good card/reader.
- **Kernel starts but root mount fails:** inspect root arguments, partitions,
  UUIDs, image compatibility, and storage errors.
- **Flashing-looking progress appears unexpectedly:** consult that exact image's
  flasher documentation; do not power-cycle during an active write. This is why
  image purpose must be checked before boot.

## Exercises

Explain how U-Boot from eMMC could boot a root filesystem on SD. Compare the
image's published size with the card's raw and filesystem capacities.

## Key Takeaways

Image compatibility, integrity, and purpose are separate checks. Verify actual
root media; preserve a non-flasher recovery card.

## Further Reading

- [Official distributions](https://www.beagleboard.org/distros)
- [Official Imaging Utility](https://www.beagleboard.org/bb-imager)
- [BBB hardware and BOOT switch](https://docs.beagleboard.org/boards/beaglebone/black/ch04.html)
- [BeagleBoard getting-started documentation](https://docs.beagleboard.org/intro/support/getting-started.html)

## Lab Status

**Documented but not tested.** No card was written and no physical microSD boot
or checksum of a selected board image was executed for this project.
