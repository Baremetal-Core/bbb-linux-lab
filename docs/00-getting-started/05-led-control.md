# Lesson 05 - Controlling onboard LEDs

## Overview

Control one onboard user LED through the Linux LED subsystem from Bash and C,
without touching GPIO registers or external wiring.

## Learning Objectives

- Discover actual LED names and triggers.
- Switch between manual brightness and the kernel `timer` trigger.
- Build a C program using `open()`, `write()`, and `close()`.
- Restore the original state afterward.

## Prerequisites

Running Linux from [Lesson 02](02-first-boot.md) or [Lesson 03](03-microsd-boot.md),
`sudo`, and for C a native compiler and Make (`build-essential`).

!!! warning "Observe before changing"
    Changing a trigger disables that LED's heartbeat/storage indicator until
    restored. Never run these commands against a development host's LEDs.

## Theory

LEDs appear in `/sys/class/leds/`; names vary by kernel and Device Tree, so do
not hardcode `beaglebone:green:usr0`.

| Attribute | Meaning |
| --- | --- |
| `brightness` | `0` to `max_brightness` |
| `trigger` | Available triggers; active one in `[brackets]` |
| `delay_on` / `delay_off` | Appear with `timer`; milliseconds |

`none` gives manual control. The LED class is separate from the GPIO character
device, which may refuse lines owned by the LED driver.

## Hands-on Lab

1. **BBB**, discover:

    ```bash
    for led in /sys/class/leds/*; do
        printf '%s: %s\n' "${led##*/}" "$(cat "$led/trigger")"
    done
    ```

2. Select one LED and save its state:

    ```bash
    LED='/sys/class/leds/ACTUAL_DISCOVERED_NAME'
    ORIGINAL_TRIGGER=$(sed -n 's/.*\[\([^]]*\)\].*/\1/p' "$LED/trigger")
    ORIGINAL_BRIGHTNESS=$(cat "$LED/brightness")
    MAXIMUM=$(cat "$LED/max_brightness")
    ```

    This saves the trigger name and brightness, not trigger-specific parameters.

3. **Manual on/off.** `sudo echo x > file` fails because your shell does the
   redirection; use `sudo tee`:

    ```bash
    echo none | sudo tee "$LED/trigger" >/dev/null
    echo "$MAXIMUM" | sudo tee "$LED/brightness" >/dev/null
    echo 0 | sudo tee "$LED/brightness" >/dev/null
    ```

4. **Bash blink** (6 cycles, ~250 ms, restores its entry state on exit/INT/TERM),
   from the repository root:

    ```bash
    sudo bash labs/00-getting-started/led-blink/blink.sh "$LED" 6
    ```

    ```bash
    --8<-- "labs/00-getting-started/led-blink/blink.sh"
    ```

5. **Kernel timer**, if `timer` is listed:

    ```bash
    echo timer | sudo tee "$LED/trigger" >/dev/null
    echo 250 | sudo tee "$LED/delay_on" >/dev/null
    echo 750 | sudo tee "$LED/delay_off" >/dev/null
    ```

    It blinks with no userspace loop. Writing `0` to `brightness` disables it.

6. **C version**, built natively on BBB:

    ```bash
    echo none | sudo tee "$LED/trigger" >/dev/null
    make -C labs/00-getting-started/led-blink
    sudo labs/00-getting-started/led-blink/led-blink "$LED" 6
    ```

    An x86 build on a host only validates the code; it will not run on BBB.

7. **Restore** brightness first, then trigger (a later `0` write would disable it):

    ```bash
    echo "$ORIGINAL_BRIGHTNESS" | sudo tee "$LED/brightness" >/dev/null
    echo "$ORIGINAL_TRIGGER" | sudo tee "$LED/trigger" >/dev/null
    cat "$LED/trigger"
    ```

## How It Works

`open()` returns a descriptor to a sysfs attribute, `write()` passes text to the
driver, and `close()` releases it. The C program validates input, checks every
I/O error, sets a `sig_atomic_t` flag on INT/TERM, and restores state outside
the handler. `nanosleep()` timing is approximate, not real-time.

```c
--8<-- "labs/00-getting-started/led-blink/led-blink.c"
```

```makefile
--8<-- "labs/00-getting-started/led-blink/Makefile"
```

## Verification

**BBB:** the LED follows on/off, blinks six times, keeps blinking under `timer`
after the shell returns, and `trigger` shows the original value after restore.

**Development host** (fixtures only, no real LEDs):

```bash
make -C labs/00-getting-started/led-blink
python -m unittest discover -s tests -v
```

Fixtures test writes, restoration, invalid input, and TERM handling; they don't
emulate kernel trigger behavior.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Permission denied | Path and `sudo tee` usage |
| Unexpected or missing LED names | Kernel/Device Tree of the booted image; don't use raw GPIO numbers |
| Brightness changes by itself | Trigger is not `none` |
| No `delay_on`/`delay_off` | Select `timer` first; it may not be built into the kernel |
| `Exec format error` | Host binary copied to BBB; rebuild on the target |

## Exercises

1. Change the cycle count. What happens with `0` or `-1`?

    ??? success "Answer"
        Both programs validate the count and exit with a usage error without
        writing to the LED.

2. Compare CPU use of the Bash loop and the `timer` trigger.

    ??? success "Answer"
        The Bash loop wakes a process and spawns writes every cycle, visible in
        `top`. The `timer` trigger runs inside the kernel with no userspace
        process, so its cost is negligible.

3. Why is no new kernel module needed for this experiment?

    ??? success "Answer"
        The existing LED driver already exposes brightness and triggers through
        sysfs. A module is only justified when no existing interface fits.

## Key Takeaways

Subsystem APIs hide board details. Discover attributes, save and restore state,
check errors, and separate host validation from hardware verification.

## Further Reading

- [Kernel LED class documentation](https://docs.kernel.org/leds/leds-class.html)
- [open(2)](https://man7.org/linux/man-pages/man2/open.2.html),
  [write(2)](https://man7.org/linux/man-pages/man2/write.2.html),
  [close(2)](https://man7.org/linux/man-pages/man2/close.2.html)

## Lab Status

**Validated in a development environment:** Bash/C fixture tests, native C
compilation, and ShellCheck pass in CI.
**Not verified on physical BBB hardware:** LED names, timer behavior, and
visible output require board evidence.
