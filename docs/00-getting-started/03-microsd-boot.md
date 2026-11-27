# Lesson 03 - Booting Linux from microSD

## Overview

Write an official Debian image to microSD and use it as non-destructive boot and
recovery media. Writing erases the selected **card**.

## Learning Objectives

- Select a BBB/AM335x image and verify its published checksum.
- Distinguish an ordinary image from an eMMC flasher.
- Prove the root filesystem is on SD without relying on MMC numbering.

## Prerequisites

[Lesson 01](01-board-overview.md), a known board revision, a card and reader,
safe power, and ideally UART. Back up the card first.

## Theory

A **flasher image** installs itself to eMMC, often automatically on boot. Never
boot one just to try Linux.

ROM boot order and U-Boot's media search are separate. A BBB may boot SD without
BOOT pressed, or may need BOOT held at power-on. Root location does not tell you
where earlier stages were loaded from.

## Hands-on Lab

1. From [BeagleBoard distributions](https://www.beagleboard.org/distros) or the
   [Imaging Utility](https://www.beagleboard.org/bb-imager), choose
   **BeagleBone Black / AM335x**, a **non-flasher** image. Read its release
   notes (account setup, card size, boot requirements).
2. **Host:** download it and record filename, URL, date, and checksum URL.
3. Verify against the publisher's checksum for the **same** (compressed or
   decompressed) file:

    ```bash
    IMAGE='your-downloaded-image.img.xz'
    EXPECTED_SHA256='paste-the-published-sha256-here'
    printf '%s  %s\n' "$EXPECTED_SHA256" "$IMAGE" | sha256sum -c -   # Linux
    shasum -a 256 "$IMAGE"                                           # macOS
    ```

    If no checksum is published, record that limitation.

4. **Host:** identify the card by comparing before/after insertion:
   `lsblk -o NAME,SIZE,MODEL,TRAN,TYPE,MOUNTPOINTS` (Linux) or `diskutil list`
   (macOS). It must not be the system or backup disk.
5. **Destructive to the card:** write the reviewed image with the Imaging Utility
   (or a writer named in the release notes), confirm the target, wait for
   validation, then eject. Do not copy `.img.xz` as a regular file.

    !!! danger "Disk selection"
        This overwrites the selected device. No auto-write script or guessed
        `/dev/sdX` is provided. Unplug other removable drives if it helps.

    For a manual partition-by-partition approach, see
    [Lesson 08](08-manual-microsd.md).

6. **Powered-off BBB:** insert the card, power on, and watch UART. If eMMC still
   boots, remove all power, hold BOOT, reapply power, then release.
7. **BBB:** confirm root media:

    ```bash
    cat /etc/os-release; uname -a
    findmnt /
    lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
    cat /proc/cmdline
    for device in /sys/block/mmcblk*; do
        [ -r "$device/device/type" ] || continue
        printf '%s: %s\n' "${device##*/}" "$(cat "$device/device/type")"
    done
    ```

    The root's parent disk must be type `SD`.

8. Save UART banners, shut down cleanly, and keep this card for recovery.

## How It Works

ROM finds a boot source, SPL initializes hardware and loads U-Boot, and U-Boot
loads the kernel and Device Tree, possibly from another device. Linux mounts the
`root=` filesystem. A disk image encodes the boot layout as well as file content.

## Verification

Record the checksum result (or its absence), image name, writer completion, UART
stages, and `/` on an `SD` device. "It booted with a card inserted" is not proof.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Old eMMC system boots | Root media, UART, BOOT held at **power-on** |
| No SD boot | Image family, checksum, writer validation, supply; try another card |
| Kernel starts but root fails | `root=`, partitions, UUIDs, image compatibility |
| Unexpected flashing progress | It is a flasher; do not cut power mid-write; read its docs |

## Exercises

1. How can U-Boot from eMMC boot a root filesystem on SD?

    ??? success "Answer"
        ROM loads SPL/U-Boot from eMMC, and U-Boot's environment then loads the
        kernel and passes `root=` pointing at an SD partition. The earlier
        stages and the root come from different devices.

2. Why is the card's raw capacity larger than the root filesystem in `df`?

    ??? success "Answer"
        The image's partitions may not fill the card, and filesystems reserve
        space for metadata. Some images grow the root partition on first boot.

## Key Takeaways

Image compatibility, integrity, and purpose are separate checks. Verify actual
root media and keep a non-flasher recovery card.

## Further Reading

- [Official distributions](https://www.beagleboard.org/distros)
- [Official Imaging Utility](https://www.beagleboard.org/bb-imager)
- [BBB hardware and BOOT switch](https://docs.beagleboard.org/boards/beaglebone/black/ch04.html)
- [BeagleBoard getting started](https://docs.beagleboard.org/intro/support/getting-started.html)

## Lab Status

**Documented but not tested.** No card was written and no SD boot was verified.
