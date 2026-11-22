# Lesson 06 - Ethernet configuration

## Overview

Connect BBB to your home LAN, identify the daemon that owns Ethernet, and configure
DHCP or a reversible static address using that daemon.

## Learning Objectives

- Identify interface, MAC, IPv4 prefix, gateway, resolver, and network manager.
- Configure DHCP/static addressing without competing network daemons.
- Diagnose link, routing, and DNS separately and recover via UART.

## Prerequisites

Running BBB Linux from [Lesson 02](02-first-boot.md) or
[Lesson 03](03-microsd-boot.md); Ethernet cable, ISP/home router with DHCP, and
optionally an unmanaged switch. `ip` requires iproute2; `ping` requires the image's
ping package. Configuration requires administrative permission.

!!! warning "Keep recovery access"
    Use UART/local console for configuration changes. An address/route change can
    terminate SSH immediately. Back up the active configuration and know the DHCP
    recovery procedure before applying a static address. Never configure two
    managers for the same interface.

## Theory

An unmanaged switch forwards local Ethernet frames; it does not normally assign
IP addresses. The router's DHCP server leases addresses and supplies gateway/DNS.
Ethernet's MAC identifies the link-layer interface; it is distinct from IPv4.

An example LAN is `192.168.50.0/24`, where `/24` means mask `255.255.255.0`.
The router might be `.1`; a board might use `.20`. **These are examples, not your
network's values.** A gateway routes off-subnet traffic; DNS resolves names.
Choose a router reservation when possible, or an approved unused static address
outside the router's dynamic pool. Do not use network/broadcast addresses.

## Hands-on Lab

1. **Powered-off board if wiring peripherals:** connect RJ45 to the router or
   switch. Boot normally and inspect link LEDs.
2. **BBB**, discover interfaces:

   ```bash
   ip -brief link
   ip -brief addr
   ip route
   ip neigh
   ```

   Identify the **wired Ethernet** interface, not loopback or a USB gadget.
   `LOWER_UP` indicates carrier; an administrative `UP` alone does not.
   `ip neigh` shows learned neighbors, not a complete list of LAN devices.
   Replace `eth0` below if your observed name differs:

   ```bash
   IFACE='eth0'
   ip link show dev "$IFACE"
   cat "/sys/class/net/$IFACE/address"
   ```

3. **BBB**, discover manager and ownership:

   ```bash
   systemctl is-active NetworkManager systemd-networkd networking
   command -v nmcli
   command -v networkctl
   ls -l /etc/resolv.conf
   ```

   An active service is not proof it owns this interface. If available, inspect
   `nmcli device status` and `networkctl status "$IFACE" --no-pager`.
   For ifupdown, inspect `/etc/network/interfaces`, included files, and
   `ifquery "$IFACE"`. On other images identify ConnMan or the actual manager and
   follow its documentation. **Stop if ownership is ambiguous.**
4. Apply **only the matching manager branch** below, using UART. Start with DHCP
   unless there is a reason to use static configuration.

### NetworkManager

Discover the active profile instead of guessing its name:

```bash
nmcli -f NAME,UUID,TYPE,DEVICE connection show
nmcli -g GENERAL.CONNECTION device show "$IFACE"
```

Set `CONNECTION` to that observed profile. Record its settings with
`nmcli connection show "$CONNECTION"`. For rollback, clone it to an unused backup
name and disable backup autoconnect:

```bash
CONNECTION='your-active-profile'
sudo nmcli connection clone "$CONNECTION" bbb-before-lab
sudo nmcli connection modify bbb-before-lab connection.autoconnect no
```

To use DHCP, clear previous manual IPv4 overrides and reapply the profile:

```bash
sudo nmcli connection modify "$CONNECTION" ipv4.method auto \
  ipv4.addresses "" ipv4.gateway "" ipv4.dns "" \
  ipv4.ignore-auto-dns no ipv4.ignore-auto-routes no
sudo nmcli connection up "$CONNECTION" ifname "$IFACE"
```

For static IPv4, **replace every example with your LAN's approved values first**:

```bash
sudo nmcli connection modify "$CONNECTION" ipv4.method manual \
  ipv4.addresses "192.168.50.20/24" ipv4.gateway "192.168.50.1" \
  ipv4.dns "192.168.50.1"
sudo nmcli connection up "$CONNECTION" ifname "$IFACE"
```

This changes IPv4 only; preserve existing IPv6 policy. `nmcli device show "$IFACE"`
reports assigned addresses and DNS. To recover over UART, re-enable DHCP with the
commands above, or activate `bbb-before-lab` on the interface to restore its prior
settings. Avoid leaving multiple autoconnect profiles competing afterward.

### systemd-networkd

`networkctl status "$IFACE" --no-pager` reports the effective **Network File**.
Back it up. Files can originate in `/usr/lib`, `/run`, or `/etc`; vendor/generated
files may be replaced, so make an appropriate persistent override in `/etc`
rather than edit them blindly. networkd uses the **first matching** `.network`
file; a new later file does not necessarily win.

For this simple lab, use a single reviewed file matched to the discovered
interface, preserving unrelated settings. Replace `eth0` as needed.
DHCP example:

```ini
[Match]
Name=eth0

[Network]
DHCP=ipv4
```

Static example, **with values replaced for your LAN**:

```ini
[Match]
Name=eth0

[Network]
DHCP=no
Address=192.168.50.20/24
Gateway=192.168.50.1
DNS=192.168.50.1
```

Use `sudoedit` on the reviewed `/etc/systemd/network/` file; do not paste either
configuration into a second competing file. Then, on versions supporting them:

```bash
sudo networkctl reload
sudo networkctl reconfigure "$IFACE"
networkctl status "$IFACE" --no-pager
```

On older versions, consult `networkctl --help`; restart networkd only from UART
and be aware it affects other managed interfaces. `DNS=` supplies resolver
information to systemd-resolved **when that integration is active**; networkd does
not itself implement a DNS resolver. Inspect `systemctl is-active systemd-resolved`,
`resolvectl status`, and the `/etc/resolv.conf` symlink before assuming DNS works.
If a different resolver owns that file, configure it through its supported method.
For rollback, restore the original file/override and reload/reconfigure via UART.

### ifupdown

Inspect `/etc/network/interfaces` and `source` includes. Back up the effective file
and use `sudoedit` to change the **existing** stanza, not duplicate it.
For DHCP, replace `eth0` with the actual interface:

```text
auto eth0
iface eth0 inet dhcp
```

For static IPv4, **replace the LAN values**:

```text
auto eth0
iface eth0 inet static
    address 192.168.50.20
    netmask 255.255.255.0
    gateway 192.168.50.1
```

DNS is resolver-specific: `dns-nameservers` requires compatible integration such
as resolvconf and is not guaranteed by ifupdown alone. Check the installed
resolver and DHCP hooks; never overwrite a managed `/etc/resolv.conf` blindly.
When resolvconf integration is installed, add `dns-nameservers 192.168.50.1`
with your actual resolver address to the static stanza.

From **UART/local console**, not the sole SSH session:

```bash
sudo ifdown "$IFACE"
sudo ifup "$IFACE"
```

If the interface is not tracked as configured, inspect ifupdown state rather than
force a command that might affect another manager. For recovery, restore the
original stanza or DHCP configuration and run the same down/up procedure.

### Verify connectivity

5. **BBB**, after your selected branch:

   ```bash
   ip -brief addr
   ip route
   ip neigh
   cat /etc/resolv.conf
   ```

6. Test in layers. Replace gateway and host names with reachable lab values:

   ```bash
   ping -c 3 YOUR_ROUTER_IP
   ping -c 3 YOUR_HOST_IP
   getent ahostsv4 www.beagleboard.org
   ```

   A numeric-IP test does not require DNS. ICMP may be blocked, so failed ping
   alone does not prove an unreachable system. `getent` checks the configured
   name-service path rather than assuming a particular resolver.
7. From the repository root **on BBB**, collect read-only diagnostics:

   ```bash
   bash labs/00-getting-started/network-diagnostics/diagnose.sh
   ```

   Pass an optional DNS name to request a lookup. The default sends no ping/probe
   traffic and does not edit configuration. Some managers/tools can be absent.

   ```bash
   --8<-- "labs/00-getting-started/network-diagnostics/diagnose.sh"
   ```

## How It Works

Link state comes from the NIC/PHY; address configuration from the manager;
routes select destinations/gateway; neighbor discovery maps local IPs to MACs;
the resolver maps names to addresses. Changing one layer does not fix another.
An `ip addr add` command alone is transient and does not replace persistent
manager configuration.

## Verification

The wired interface has carrier and an address with the intended prefix, the
router route is correct, an appropriate local host is reachable, and name lookup
works with your chosen resolver. Reboot after saving work and check persistence.
Demonstrate a UART rollback before depending on remote-only access.

## Troubleshooting

- **No carrier:** cable/switch port/power; an IP change cannot repair a physical link.
- **Carrier but no IPv4:** DHCP server/pool, manager ownership, and profile matching.
- **Local LAN works but internet fails:** default route/router upstream connectivity.
- **Numeric IP works but names fail:** resolver ownership, DNS server, and DHCP data.
- **SSH disappeared:** use UART, restore backup or DHCP, inspect the router's leases,
  and reconnect to the observed address. Do not reboot repeatedly hoping it returns.

## Exercises

Explain why the unmanaged switch does not appear as the gateway. Compare a DHCP
reservation with board-side static addressing and document the rollback you used.

## Key Takeaways

Discover ownership before editing. Link, address, route, and DNS are separate
diagnostic layers. Network changes need a recovery console.

## Further Reading

- [NetworkManager nmcli manual](https://networkmanager.dev/docs/api/latest/nmcli.html)
- [systemd.network manual](https://www.freedesktop.org/software/systemd/man/latest/systemd.network.html)
- [Debian network configuration reference](https://www.debian.org/doc/manuals/debian-reference/ch05.en.html)
- [ip(8) manual](https://man7.org/linux/man-pages/man8/ip.8.html)

## Lab Status

**Documented but not tested on physical BBB hardware.** The diagnostic script
has host-side syntax/ShellCheck validation. DHCP, static addresses, resolver
integration, and rollback depend on the actual image and LAN.
