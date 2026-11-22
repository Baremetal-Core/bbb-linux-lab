# Module 00 - Getting started

Build confidence in a running BBB before replacing its operating system or
writing a driver. Finish with a documented hardware inventory, a reproducible
userspace LED experiment, Ethernet connectivity, and key-based SSH.

| Lesson | Outcome | Risk |
| --- | --- | --- |
| [01 - Board overview](01-board-overview.md) | Identify interfaces and the boot stack | Electrical wiring |
| [02 - First boot](02-first-boot.md) | Inspect existing Linux without changing storage | Low |
| [03 - microSD boot](03-microsd-boot.md) | Prepare recovery media and prove root location | Erases selected host card |
| [04 - Flash eMMC](04-flash-emmc.md) | Install a compatible image with verified recovery | **Erases board eMMC** |
| [05 - LED control](05-led-control.md) | Use LED sysfs from Bash and C | Changes LED indicators |
| [06 - Ethernet setup](06-ethernet-setup.md) | Discover and configure the active network stack | Can break SSH |
| [07 - SSH and remote development](07-ssh-remote-development.md) | Deploy code and collect logs remotely | Key/account configuration |

Read [prerequisites](../prerequisites.md) first. Lessons are sequential except
that **04 is optional**: working microSD or existing eMMC Linux is enough for
05-07. Keep known-good microSD recovery media and a serial console.

## Completion evidence

Explain which device supplies `/`, the difference between bootloader and root
media, the current LED trigger, which daemon owns Ethernet, and how you will
recover if SSH stops working. Save commands and observations, not just screenshots
of a successful prompt.

## Lab status

**Documented but not tested on physical BBB hardware.** Website and executable
examples can be checked on a host. Physical observations must be added by learners.
