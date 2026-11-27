# Lesson 06 - Ethernet configuration

## Overview

Connect BBB to your LAN, find which daemon owns Ethernet, and configure DHCP or
a reversible static address through that daemon.

## Learning Objectives

- Identify interface, MAC, prefix, gateway, resolver, and network manager.
- Configure DHCP or static IPv4 without competing managers.
- Diagnose link, routing, and DNS separately and recover via UART.

## Prerequisites

Running Linux from [Lesson 02](02-first-boot.md) or [Lesson 03](03-microsd-boot.md),
an Ethernet cable, a DHCP router, `iproute2`, `ping`, and `sudo`.

!!! warning "Keep recovery access"
    Make changes from UART or a local console; an address change can drop SSH
    instantly. Back up the active configuration first. Never let two managers
    control one interface.

## Theory

| Layer | Provided by | Example |
| --- | --- | --- |
| Link | NIC/PHY, cable, switch | carrier (`LOWER_UP`), MAC |
| Address | DHCP server or static config | `192.168.50.20/24` |
| Route | Gateway for off-subnet traffic | `192.168.50.1` |
| Name | Resolver/DNS | `getent ahostsv4 host` |

**Example values only.** An unmanaged switch forwards frames but does not assign
addresses. For a fixed address prefer a router DHCP reservation; otherwise pick
an approved unused address outside the DHCP pool.

## Hands-on Lab

1. Connect Ethernet, boot, and check the link LEDs.
2. **BBB**, discover the wired interface (not `lo` or a USB gadget):

    ```bash
    ip -brief link; ip -brief addr; ip route
    IFACE='eth0'   # replace with the observed name
    cat "/sys/class/net/$IFACE/address"
    ```

3. **BBB**, find the owning manager:

    ```bash
    systemctl is-active NetworkManager systemd-networkd networking
    nmcli device status 2>/dev/null
    networkctl status "$IFACE" --no-pager 2>/dev/null
    ls -l /etc/resolv.conf
    ```

    For ifupdown, inspect `/etc/network/interfaces` and `ifquery "$IFACE"`.
    **Stop if ownership is unclear.** Apply only the matching branch below,
    starting with DHCP.

### NetworkManager

```bash
CONNECTION=$(nmcli -g GENERAL.CONNECTION device show "$IFACE")
sudo nmcli connection clone "$CONNECTION" bbb-before-lab
sudo nmcli connection modify bbb-before-lab connection.autoconnect no
```

DHCP:

```bash
sudo nmcli connection modify "$CONNECTION" ipv4.method auto \
  ipv4.addresses "" ipv4.gateway "" ipv4.dns ""
sudo nmcli connection up "$CONNECTION" ifname "$IFACE"
```

Static (**replace values**):

```bash
sudo nmcli connection modify "$CONNECTION" ipv4.method manual \
  ipv4.addresses 192.168.50.20/24 ipv4.gateway 192.168.50.1 ipv4.dns 192.168.50.1
sudo nmcli connection up "$CONNECTION" ifname "$IFACE"
```

Rollback: rerun the DHCP commands, or `sudo nmcli connection up bbb-before-lab`.

### systemd-networkd

`networkctl status "$IFACE"` shows the active **Network File**; back it up.
networkd uses the **first matching** file, so edit that one (or a correctly
ordered override in `/etc/systemd/network/`) with `sudoedit` rather than adding
a second file.

```ini
[Match]
Name=eth0

[Network]
DHCP=ipv4
# Static instead (replace values):
# DHCP=no
# Address=192.168.50.20/24
# Gateway=192.168.50.1
# DNS=192.168.50.1
```

```bash
sudo networkctl reload && sudo networkctl reconfigure "$IFACE"
```

`DNS=` takes effect only through systemd-resolved; check `resolvectl status`.
Rollback: restore the backup file and reload.

### ifupdown

Back up and `sudoedit` the **existing** stanza in `/etc/network/interfaces`:

```text
auto eth0
iface eth0 inet dhcp

# Static instead (replace values):
# iface eth0 inet static
#     address 192.168.50.20
#     netmask 255.255.255.0
#     gateway 192.168.50.1
#     dns-nameservers 192.168.50.1   # only with resolvconf installed
```

Apply from UART: `sudo ifdown "$IFACE" && sudo ifup "$IFACE"`.
Rollback: restore the backup and repeat.

### Verify connectivity

4. **BBB**, test each layer (replace addresses):

    ```bash
    ip -brief addr; ip route; cat /etc/resolv.conf
    ping -c 3 YOUR_ROUTER_IP
    getent ahostsv4 www.beagleboard.org
    ```

    ICMP may be blocked, so a failed ping alone is not conclusive.

5. Read-only diagnostics (sends no traffic unless you pass a DNS name):

    ```bash
    bash labs/00-getting-started/network-diagnostics/diagnose.sh
    ```

    ```bash
    --8<-- "labs/00-getting-started/network-diagnostics/diagnose.sh"
    ```

## How It Works

Each layer in the table depends on the one above it; fixing one does not fix
another. `ip addr add` is transient; persistent settings belong to the manager.

## Verification

Carrier present, intended address and prefix, correct default route, router
reachable, names resolve, and settings survive a reboot. Practice the UART
rollback once before relying on remote access.

## Troubleshooting

| Symptom | Likely layer / check |
| --- | --- |
| No carrier | Cable, switch port, power |
| Carrier but no IPv4 | DHCP pool, manager ownership, profile match |
| LAN works, internet fails | Default route, router upstream |
| IP works, names fail | Resolver ownership, DNS server |
| SSH lost | UART: restore backup or DHCP, check router leases |

## Exercises

1. Why is the unmanaged switch not your gateway?

    ??? success "Answer"
        It forwards Ethernet frames within the LAN and has no IP routing role.
        The router routes traffic off the subnet, so it is the gateway.

2. Compare a DHCP reservation with board-side static addressing.

    ??? success "Answer"
        A reservation keeps the board on DHCP, so gateway and DNS stay correct
        and the address is managed centrally. A static address works without
        DHCP but must avoid the pool and be updated by hand if the LAN changes.

## Key Takeaways

Find the owner before editing. Link, address, route, and DNS are separate
layers. Network changes need a recovery console.

## Further Reading

- [nmcli manual](https://networkmanager.dev/docs/api/latest/nmcli.html)
- [systemd.network manual](https://www.freedesktop.org/software/systemd/man/latest/systemd.network.html)
- [Debian network configuration](https://www.debian.org/doc/manuals/debian-reference/ch05.en.html)
- [ip(8)](https://man7.org/linux/man-pages/man8/ip.8.html)

## Lab Status

**Documented but not tested on physical BBB hardware.** The diagnostic script
passes ShellCheck on the host.
