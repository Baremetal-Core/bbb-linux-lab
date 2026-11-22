# Lesson 04 - Installing Linux into eMMC

## Overview

Use an explicitly supported BeagleBoard eMMC flasher workflow. This is optional:
you can continue the course from ordinary microSD Linux without installing eMMC.

!!! danger "Destructive board operation"
    Flashing replaces eMMC contents, including personal files, credentials,
    boot configuration, and possibly bootloader areas. **Booting a flasher card
    may start this automatically.** Do not insert/power it until backup,
    compatibility, destination identification, and recovery checks are complete.
    This repository never automatically performs disk writes.

## Learning Objectives

- Distinguish running from microSD from installing to eMMC.
- Identify storage by observations rather than MMC numbering.
- Back up needed data and execute only an image-specific supported procedure.
- Verify installation with the card removed and retain recovery access.

## Prerequisites

[Lesson 03](03-microsd-boot.md), a proven **non-flasher** recovery card, stable
power, UART, verified eMMC capacity, and an explicitly approved maintenance
window. Complete backups **before booting any automatic flasher**.

## Theory

An ordinary SD image runs its root filesystem from SD. A flasher boots a small
or normal SD environment and runs image-specific installation logic: it may
partition eMMC, install boot stages, copy a root filesystem, and adjust identifiers.
Layout and completion signals vary by image generation.

`/dev/mmcblk0` and `/dev/mmcblk1` are enumeration names, not promises about
physical media. eMMC boot areas (`mmcblkNboot0/1`) are also different from user
storage. Never copy a generic SD disk image blindly into a guessed eMMC device.

## Hands-on Lab

1. **Before flashing:** boot current eMMC or the known-good non-flasher SD card.
   Identify all data to preserve: application source/config, SSH authorized keys,
   service files, and other personal data. Stop applications that modify their
   data before backup. A live file copy is not an atomic database snapshot.
2. If SSH already works, **Host**, back up selected files (replace account/IP):

   ```bash
   mkdir -p backups/bbb-home
   rsync -av --progress boarduser@BOARD_IP:/home/boarduser/ backups/bbb-home/
   ```

   This backs up only that account's readable home, not all eMMC contents.
   For other files, use authorized access and an appropriate consistent backup
   method. If SSH is unavailable, mount eMMC from non-flasher SD and copy selected
   files to separate media; discover source partitions and mount them read-only.
   Open representative backed-up files and verify important checksums. Keep
   backups private and off both the destination eMMC and flasher card.
3. **BBB on non-flasher SD**, inspect storage:

   ```bash
   findmnt /
   lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
   for device in /sys/block/mmcblk*; do
       [ -r "$device/device/type" ] || continue
       printf '%s: ' "${device##*/}"
       cat "$device/device/type"
       cat "$device/device/name"
   done
   ```

   Correlate `SD` with the running SD root, and `MMC` with eMMC; record capacities.
   Inspect `findmnt`/`lsblk` for any eMMC partitions still mounted. Your chosen
   flasher's instructions must explain handling mounts before installation.
   **Stop** if media identity or required capacity is unclear.
4. Select a flasher explicitly documented for **BBB/AM335x and your eMMC size**
   from [official distributions](https://www.beagleboard.org/distros).
   Read its linked release instructions from start to finish. Confirm it is
   intended to install eMMC, which bootloader/layout it installs, when writes
   begin, what completion/failure looks like, and what power-off procedure is safe.
   If only an ordinary image is offered, follow that release's documented
   conversion/install procedure; do not guess a generic `/boot/uEnv.txt` line
   or script path from another release.
5. Verify the download and write the flasher card on the **Host** using the
   reviewed writer procedure from Lesson 03. This erases the selected card.
   Preserve the separate non-flasher recovery card.
6. **Final approval checkpoint:** backups checked; eMMC correctly identified;
   image compatible; supply stable; peripherals minimized; UART attached;
   completion procedure known. Shut down, remove power, insert flasher SD,
   and boot **exactly as that release instructs**.
7. Observe UART and documented progress. **Do not interrupt power, remove SD,
   press reset, or start another installer while writing.** LED animation is
   image-specific, not a universal success signal. Wait for the release's explicit
   success indication or completed shutdown; preserve failure logs if it fails.
8. After documented completion and safe power-off, remove the flasher card.
   Power on normally without BOOT override. Log in according to the new image's
   account instructions; the old password/account may no longer exist.
9. **BBB**, repeat:

   ```bash
   cat /etc/os-release
   uname -a
   findmnt /
   lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
   ```

   Correlate root with the recorded `MMC` device and confirm the intended image.
   Test needed services, reboot once after saving work, and confirm repeatable boot.

## How It Works

A supported installer handles more than copying files: boot-stage offsets,
partition layout, root identifiers, and image-specific services can differ
between SD and eMMC. The selected release is the authority for its flashing
commands, script paths, and completion semantics.

## Verification

Before writing: verified backups, identified eMMC capacity/type, compatible
image, known-good recovery media, reliable power, and known completion criteria.
After writing: recorded installer success, card removed, intended distribution,
root correlated with eMMC, needed services functional, and a second successful boot.
Do not mark this verified from a single LED pattern.

## Troubleshooting

- **eMMC will not boot:** power off safely and boot the non-flasher recovery
  card. Inspect UART, `lsblk`, partitions, and logs without immediately rewriting.
- **Installer reports capacity/layout mismatch:** select a compatible image or
  documented customization. Never force a larger raw image onto smaller eMMC.
- **Power failed mid-write:** eMMC may be incomplete. Recover from non-flasher SD,
  confirm backups and supply, then repeat the supported installation if appropriate.
- **SSH host key changed:** verify the new fingerprint via UART before updating
  the host's known-host entry; do not disable host-key checking.

## Exercises

Write a personal pre-flash checklist and describe recovery with totally
unbootable eMMC. Explain why a backup stored on the flasher card is unsafe.

## Key Takeaways

SD boot and eMMC installation are different operations. Every storage write needs
positive identification, explicit approval, a supported layout, and recovery.

## Further Reading

- [Official image selector and release notes](https://www.beagleboard.org/distros)
- [BeagleBoard getting started](https://docs.beagleboard.org/intro/support/getting-started.html)
- [BBB system reference manual](https://docs.beagleboard.org/boards/beaglebone/black/index.html)

## Lab Status

**Documented but not tested.** No eMMC installation, backup restoration, or
hardware recovery has been performed. No universal flasher command is claimed.
