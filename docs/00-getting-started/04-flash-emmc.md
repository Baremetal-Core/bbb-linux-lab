# Lesson 04 - Installing Linux into eMMC

## Overview

Install an image to eMMC using an officially supported BeagleBoard flasher.
Optional: the course works from microSD alone.

!!! danger "Destructive board operation"
    Flashing replaces all eMMC contents. **A flasher card may start writing as
    soon as it boots.** Finish backups, compatibility, and recovery checks
    before inserting it. This repository never writes disks automatically.

## Learning Objectives

- Distinguish running from SD from installing to eMMC.
- Identify storage by observation, not MMC numbering.
- Back up data, flash with an image-specific procedure, and verify the result.

## Prerequisites

[Lesson 03](03-microsd-boot.md), a proven **non-flasher** recovery card, stable
power, UART, and known eMMC capacity.

## Theory

A flasher boots from SD and runs image-specific logic that partitions eMMC,
installs boot stages, and copies the root filesystem. `/dev/mmcblk0`/`1` are
enumeration names, not fixed hardware. Never `dd` a generic image to a guessed
eMMC device.

## Hands-on Lab

1. **Back up.** Stop applications that modify data, then, if SSH works
   (**Host**, replace user/IP):

    ```bash
    mkdir -p backups/bbb-home
    rsync -av boarduser@BOARD_IP:/home/boarduser/ backups/bbb-home/
    ```

    This copies only one home directory. Without SSH, boot the recovery card and
    mount eMMC partitions read-only to copy files. Verify the backup; keep it
    off both eMMC and the flasher card.

2. **BBB on recovery SD**, identify eMMC:

    ```bash
    findmnt /
    lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
    for device in /sys/block/mmcblk*; do
        [ -r "$device/device/type" ] || continue
        printf '%s: %s %s\n' "${device##*/}" \
          "$(cat "$device/device/type")" "$(cat "$device/device/name")"
    done
    ```

    `SD` holds the running root; `MMC` is eMMC. **Stop** if unclear.

3. Pick a flasher documented for **BBB/AM335x and your eMMC size** from
   [official distributions](https://www.beagleboard.org/distros). Read its
   instructions fully: when writing starts, what success/failure looks like,
   and how to power off safely. Don't borrow `uEnv.txt` tweaks from other releases.
4. **Host:** verify and write the flasher card as in Lesson 03, keeping the
   recovery card separate.
5. **Checklist:** backups verified, eMMC identified, image compatible, supply
   stable, UART attached, completion signal known. Power off, insert the flasher,
   and boot **as the release instructs**.
6. **During writing, do not** cut power, remove the card, or press reset. Wait
   for the documented success signal or shutdown; save UART logs on failure.
7. Remove the flasher, power on normally, and log in with the **new** image's
   credentials.
8. **BBB:**

    ```bash
    cat /etc/os-release; uname -a
    findmnt /
    lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
    ```

    Root must be on the `MMC` device. Reboot once to confirm repeatable boot.

## How It Works

Supported installers handle boot-stage offsets, partition layout, and root
identifiers that differ between SD and eMMC. The release documentation is the
authority for its commands and completion signals.

## Verification

Installer success recorded, card removed, intended OS running, `/` on eMMC,
services working, and a second clean boot. An LED pattern alone is not proof.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| eMMC will not boot | Boot the recovery card; inspect UART and partitions before rewriting |
| Capacity/layout mismatch | Use an image built for your eMMC size; never force a larger image |
| Power lost mid-write | Recover from SD, fix the supply, repeat the supported install |
| SSH host key changed | Verify the new fingerprint over UART, then update `known_hosts` |

## Exercises

1. Write your pre-flash checklist.

    ??? success "Answer"
        Backups copied and opened; eMMC identified by type and size; image
        targets BBB and this eMMC size; checksum verified; recovery card tested;
        stable supply; UART logging; completion signal known.

2. How do you recover from a completely unbootable eMMC?

    ??? success "Answer"
        Power off, insert the non-flasher recovery card, and hold BOOT while
        reapplying power so ROM boots SD. Inspect eMMC from there, then reflash
        with a supported image.

3. Why is a backup on the flasher card unsafe?

    ??? success "Answer"
        The card is rewritten when you prepare it, may be modified during
        flashing, and is a single point of failure. Store backups on separate
        media.

## Key Takeaways

SD boot and eMMC installation are different operations. Every write needs
positive identification, a supported layout, and a tested recovery path.

## Further Reading

- [Official image selector and release notes](https://www.beagleboard.org/distros)
- [BeagleBoard getting started](https://docs.beagleboard.org/intro/support/getting-started.html)
- [BBB system reference manual](https://docs.beagleboard.org/boards/beaglebone/black/index.html)

## Lab Status

**Documented but not tested.** No eMMC installation or recovery has been
performed. No universal flasher command is claimed.
