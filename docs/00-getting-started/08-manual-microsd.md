# Lesson 08 - Manually assembling a microSD card

## Overview

Partition, format, and populate a card yourself instead of writing a whole-disk
image. Uses **Buildroot 2024.02.12 `beaglebone_defconfig`** artifacts, not a
BeagleBoard Debian image. Optional; does not touch eMMC.

## Learning Objectives

- Create an MBR with a bootable FAT partition and an ext4 root partition.
- Populate boot files and select root by PARTUUID instead of MMC number.
- Prove which device supplies `/` on the board.

## Prerequisites

- [Lesson 03](03-microsd-boot.md), a spare card (≥ 1 GiB, backed up), UART,
  and a separate known-good recovery card.
- `boot.vfat` and `rootfs.ext4` from one trusted build of the pinned
  configuration (`output/images/`), with recorded checksums. Do not mix boot
  files and root filesystems from different builds or distributions.
- **Linux host** with `sudo`, `lsblk`, `sfdisk`, `mkfs.fat`, `blkid`, `dd`.
- **macOS:** pass the whole USB reader through to a Linux VM and run everything
  there; macOS lacks the needed tooling. Identify the card again inside the VM.

## Theory

| Partition | Type | Content |
| --- | --- | --- |
| 1, active, 64 MiB | `c` FAT32 LBA | `MLO`, `u-boot.img`, `zImage`, DTBs, `uEnv.txt`, `extlinux/` |
| 2, 512 MiB | `83` Linux | `rootfs.ext4` written block-for-block |

ROM loads `MLO` (SPL) from the active FAT partition, SPL loads U-Boot, and
U-Boot loads the kernel and Device Tree. Linux mounts the `root=` partition.
Other images may use raw-sector bootloaders or other layouts; this recipe is
specific to this build.

## Hands-on Lab

!!! danger "Erases the selected card"
    Every write below destroys data. Identify the card by size, model, and
    transport; stop if ambiguous. Never guess `/dev/sdX` or `/dev/mmcblkN`.

1. **Identify the card.** Run before and after insertion and compare:

    ```bash
    lsblk -o NAME,PATH,SIZE,MODEL,TRAN,RM,TYPE,MOUNTPOINTS
    ```

    Unmount any mounted card partitions and disable automount for it.

2. **Set variables** (replace both values) and review:

    ```bash
    CARD='/dev/REPLACE-WITH-WHOLE-CARD'
    ARTIFACTS='/absolute/path/to/output/images'
    lsblk "$CARD"
    ls -lh "$ARTIFACTS/boot.vfat" "$ARTIFACTS/rootfs.ext4"
    ```

3. **Partition** (destructive). Starts are aligned to 1 MiB by default:

    ```bash
    printf 'label: dos\n,64M,c,*\n,512M,83\n' | sudo sfdisk "$CARD"
    sudo fdisk -l "$CARD"
    ```

    Expect partition 1 type `c` marked boot (`*`), partition 2 type `83`.
    Set the partition paths from `lsblk "$CARD"` (e.g. suffix `1`/`2` or `p1`/`p2`):

    ```bash
    BOOT='/dev/REPLACE-WITH-PARTITION-1'
    ROOT='/dev/REPLACE-WITH-PARTITION-2'
    ```

4. **Create filesystems** (destructive). Stop if the image exceeds the partition:

    ```bash
    stat -Lc %s "$ARTIFACTS/rootfs.ext4"; sudo blockdev --getsize64 "$ROOT"
    sudo mkfs.fat -F 32 -n BOOT "$BOOT"
    sudo dd if="$ARTIFACTS/rootfs.ext4" of="$ROOT" bs=4M conv=fsync
    ```

5. **Copy boot files**, `MLO` first:

    ```bash
    WORK="$(mktemp -d)"; mkdir "$WORK/src" "$WORK/card"
    sudo mount -o loop,ro "$ARTIFACTS/boot.vfat" "$WORK/src"
    sudo mount "$BOOT" "$WORK/card"
    sudo cp "$WORK/src/MLO" "$WORK/card/"
    sudo cp -rn "$WORK/src/." "$WORK/card/"
    ls "$WORK/card"
    ```

6. **Select root by PARTUUID.** Upstream hardcodes MMC names, which can differ:

    ```bash
    sudo blkid -s PARTUUID -o value "$ROOT"
    ```

    As root, edit both `$WORK/card/uEnv.txt` (`root=/dev/${bootpartition}`) and
    `$WORK/card/extlinux/extlinux.conf` (`root=/dev/mmcblk0p2`), replacing the
    argument with `root=PARTUUID=<value>`. Leave everything else intact.

7. **Unmount and boot:**

    ```bash
    sync; sudo umount "$WORK/card" "$WORK/src"; rmdir "$WORK/card" "$WORK/src" "$WORK"
    ```

    Eject, insert into the powered-off BBB, and boot with UART attached using
    the BOOT-button procedure from [Lesson 03](03-microsd-boot.md).

## How It Works

The partition table defines the layout; the active FAT partition is where ROM
finds `MLO`. PARTUUID is derived from the MBR disk signature and partition
number, so Linux finds root regardless of how it numbers MMC controllers.

## Verification

**Host:** `sudo fdisk -l "$CARD"` and `sudo blkid "$BOOT" "$ROOT"` show an
active FAT type `c` partition and an ext4 type `83` partition.

**BBB:** `cat /proc/cmdline` shows your PARTUUID; `cat /proc/mounts` shows `/`
on a device whose `/sys/block/mmcblk*/device/type` is `SD`. Record board
revision, artifact checksums, U-Boot and kernel versions, and UART log.
SD root does not prove SPL/U-Boot also came from SD; check the UART banners.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Wrong disk selected | Stop writing immediately; re-identify before any further step |
| Old eMMC system boots | BOOT-button power-on, active flag, `MLO` present on FAT |
| No UART output | Partition 1 type/active flag, FAT32 format, matching build artifacts |
| `VFS: Unable to mount root fs` | `root=` value vs `blkid` PARTUUID, both config files edited |
| Unexpected login/network | Buildroot defaults differ from Debian; check the build configuration |

**Recovery:** boot the known-good card, or re-image this card with Lesson 03.

## Exercises

1. Compare this layout with the pinned `genimage.cfg`. What differs?

    ??? success "Answer"
        Same partition types (`0xC` bootable + `0x83`) and 512 MiB root.
        Upstream writes a prebuilt 16 MiB `boot.vfat` image to partition 1;
        here a 64 MiB FAT is freshly formatted and files are copied, leaving
        room for extra kernels or DTBs.

2. How does PARTUUID differ from the ext4 filesystem UUID, and what breaks
   when you clone the card?

    ??? success "Answer"
        PARTUUID lives in the partition table (MBR signature + partition
        number); the filesystem UUID lives in the ext4 superblock. Cloning a
        partition copies the filesystem UUID; cloning the whole disk copies
        both. With two clones attached, `root=` becomes ambiguous.

3. Why does the rootfs partition show its full size in `lsblk` but less space
   in `df` on the board?

    ??? success "Answer"
        `dd` copies the filesystem at its image size. Grow it with
        `resize2fs` on the unmounted partition to fill the 512 MiB.

## Key Takeaways

Disk layout, filesystems, boot files, and root selection are separate layers.
A layout is compatible with a specific boot chain, not universally.

## Further Reading

- [Buildroot BBB defconfig (2024.02.12)](https://github.com/buildroot/buildroot/blob/2024.02.12/configs/beaglebone_defconfig)
- [Buildroot BBB image layout](https://github.com/buildroot/buildroot/blob/2024.02.12/board/beaglebone/genimage.cfg)
- [Buildroot BBB readme](https://github.com/buildroot/buildroot/blob/2024.02.12/board/beaglebone/readme.txt)
- [U-Boot AM335x documentation](https://docs.u-boot.org/en/latest/board/ti/am335x_evm.html)
- [sfdisk(8)](https://man7.org/linux/man-pages/man8/sfdisk.8.html)

## Lab Status

**Documented but not tested.** No card was written; not verified on physical
BBB hardware.
