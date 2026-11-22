# Prerequisites and lab conventions

## Hardware checklist

- BeagleBone Black; record its printed revision and compare it to the
  [official hardware documentation](https://docs.beagleboard.org/boards/beaglebone/black/index.html).
- A regulated 5 V supply with the connector, polarity, and current capability
  specified in your board's system reference manual. USB power may be sufficient
  for a bare board; peripherals can exceed the available budget.
- A known-good microSD card and reader, large enough for the selected image.
- Ethernet cable, router with DHCP, and optionally an unmanaged switch.
- A **3.3 V TTL** USB-UART adapter for the debug header, plus correctly mapped
  ground/TX/RX wiring. Never use RS-232 voltage levels or a 5 V TX signal.
- Optional micro-HDMI display and USB keyboard.

!!! danger "Electrical limits"
    P8/P9 digital I/O is 3.3 V, not 5 V tolerant. Analog inputs have a 1.8 V limit.
    Not every header pin is GPIO, and eMMC/HDMI/pinmux may own pins. Leave headers
    disconnected for the introductory labs. Wire UART with power removed; do
    not connect the adapter's power wire. Consult the exact header diagram.

## Host tools

Ubuntu hosts need Git, OpenSSH client, rsync, image verification tools, and a
serial terminal such as picocom. Install only missing tools with the host's
package manager. Compiling C on BBB Debian needs `build-essential`; it is not
needed just to boot or inspect the board.

MacBook needs Git, SSH, a current Python 3, an image writer, and a serial terminal.
Use `shasum -a 256` when `sha256sum` is unavailable. Use the OptiPlex for Linux
network tools that macOS does not provide.

Documentation requires Python >= 3.11. In the repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
zensical serve
```

If Ubuntu reports missing `ensurepip`, install the matching `python3-venv`
package before recreating the environment. Do not install course packages into
system Python. A rendered static website needs no Python on the reader's device.

## Command locations

Each lesson labels **Host** or **BBB** commands. Replace example addresses,
usernames, connection names, and device paths with observed values. A variable
assignment is not discovery: review it before running subsequent commands.
`sudo` is limited to the operation that requires it.

SSH requires a reachable board address and an existing account. Obtain initial
credentials or account-creation instructions from the **selected image's release
notes**, not from an assumed default password.

## Keep a board inventory

Record privately: date, printed revision, image URL/checksum, `/etc/os-release`,
`uname -a`, `findmnt /`, `lsblk`, observed LED names/triggers, networking manager,
and UART boot log. Device Tree's model is useful but is not proof of the PCB
revision. Record U-Boot's banner from UART; a userspace package version does not
prove which bootloader booted.

Do not publish passwords, SSH private keys, LAN details, serial numbers, or
unredacted logs unnecessarily.

## Validation levels

| Label | Meaning |
| --- | --- |
| Documented but not tested | Instructions/references exist; target steps were not executed |
| Validated in a development environment | Named host checks or fixture tests ran; no claim about a physical LED |
| Verified on physical BBB hardware | Actual board/image/kernel and execution evidence are recorded |

Every lesson carries a status. The [contribution guide](contributing.md) explains
how to improve that status without overstating evidence.
