# Lesson 05 - Controlling onboard LEDs

## Overview

Use Linux's LED subsystem to control one onboard user LED from the shell and C,
without manipulating GPIO registers or wiring external hardware.

## Learning Objectives

- Discover actual LED names and active triggers.
- Switch between manual brightness and kernel timer control.
- Build a C program using `open()`, `write()`, and `close()`.
- Restore the original trigger after the experiment.

## Prerequisites

[Lesson 02](02-first-boot.md) or working microSD Linux from
[Lesson 03](03-microsd-boot.md); Bash and standard utilities on BBB.
For C, a native compiler and Make (`build-essential` on Debian). No
cross-compiler is required yet. Appropriate permission is needed for sysfs writes.
eMMC installation is not required.

!!! warning "Observe before changing"
    Replacing a trigger temporarily removes that LED's heartbeat/storage indicator.
    Choose one onboard user LED, not an unrelated device's LED. Do not run these
    commands against a development host's real LEDs.

## Theory

Linux exposes LEDs in `/sys/class/leds/`. Names vary with kernel and Device Tree;
do not hardcode `beaglebone:green:usr0`. The four board user LEDs are USR0-USR3,
but map Linux names to physical LEDs through observation/manual.

`brightness` accepts zero through `max_brightness`. `trigger` lists available
event sources with the active one in brackets, such as `[heartbeat]`.
Common BBB images use heartbeat, CPU, and MMC activity, but assignments vary.
`none` disables automatic events; a `timer` trigger, when available, creates
`delay_on` and `delay_off` attributes in milliseconds.

The LED subsystem is a class API backed by a driver. General GPIO character
devices are a different API and may refuse lines already owned by the LED driver.

## Hands-on Lab

1. **BBB**, discover rather than guess:

   ```bash
   ls -1 /sys/class/leds/
   for led in /sys/class/leds/*; do
       [ -r "$led/trigger" ] || continue
       printf '%s: ' "${led##*/}"
       cat "$led/trigger"
   done
   ```

2. Select one actual onboard LED directory. Replace the example name:

   ```bash
   LED='/sys/class/leds/ACTUAL_DISCOVERED_NAME'
   cat "$LED/trigger"
   cat "$LED/brightness"
   cat "$LED/max_brightness"
   ORIGINAL_TRIGGER=$(sed -n 's/.*\[\([^]]*\)\].*/\1/p' "$LED/trigger")
   ORIGINAL_BRIGHTNESS=$(cat "$LED/brightness")
   MAXIMUM=$(cat "$LED/max_brightness")
   ```

   Save the trigger and brightness before writing. If using a customized trigger,
   record its extra parameters too; these examples restore the trigger name and
   brightness snapshot, not timer delays or other trigger-specific settings.
3. **BBB**, manually turn on, then off:

   ```bash
   printf 'none\n' | sudo tee "$LED/trigger" >/dev/null
   printf '%s\n' "$MAXIMUM" | sudo tee "$LED/brightness" >/dev/null
   cat "$LED/brightness"
   printf '0\n' | sudo tee "$LED/brightness" >/dev/null
   ```

   `sudo echo ... > file` is not sufficient: your unprivileged shell performs
   the redirection. `sudo tee` privileges only the actual write.
4. From the repository root **on BBB**, run the finite Bash lab:

   ```bash
   sudo bash labs/00-getting-started/led-blink/blink.sh "$LED" 6
   ```

   The script snapshots its entry state, blinks at approximately 250 ms on/off,
   and restores that state on exit or handled INT/TERM. Since you already selected
   `none`, it restores `none`; the final step restores your original pre-lab trigger.

   ```bash
   --8<-- "labs/00-getting-started/led-blink/blink.sh"
   ```

5. If `timer` appears in the available triggers, **BBB**:

   ```bash
   printf 'timer\n' | sudo tee "$LED/trigger" >/dev/null
   cat "$LED/delay_on" "$LED/delay_off"
   printf '250\n' | sudo tee "$LED/delay_on" >/dev/null
   printf '750\n' | sudo tee "$LED/delay_off" >/dev/null
   ```

   Observe repeated flashes without a userspace loop. If the LED stays dark,
   set a nonzero brightness after selecting `timer`. Writing zero brightness can
   disable the timer trigger, so inspect `trigger` again after any zero write.
6. **BBB**, return to manual control and build/run C:

   ```bash
   printf 'none\n' | sudo tee "$LED/trigger" >/dev/null
   make -C labs/00-getting-started/led-blink
   sudo labs/00-getting-started/led-blink/led-blink "$LED" 6
   ```

   Native x86 compilation on OptiPlex validates code but produces an x86 binary,
   **not** a BBB executable. Cross-compilation comes later.
7. **BBB**, restore the original pre-lab state:

   ```bash
   printf '%s\n' "$ORIGINAL_BRIGHTNESS" | sudo tee "$LED/brightness" >/dev/null
   printf '%s\n' "$ORIGINAL_TRIGGER" | sudo tee "$LED/trigger" >/dev/null
   cat "$LED/trigger"
   ```

   Restore brightness **before** the trigger: writing zero afterward could disable
   a restored trigger. Reapply custom parameters if you recorded them. SIGKILL,
   power loss, or device removal prevents automatic restoration.

## How It Works

`open()` obtains a file descriptor to a sysfs attribute; `write()` passes a text
value to the kernel driver; `close()` releases the descriptor. Each update opens
at offset zero. A sysfs attribute is not an ordinary persistent configuration
file, and writes can fail if the driver rejects a value.

The C example validates inputs, checks I/O errors, handles INT/TERM through a
`sig_atomic_t` flag, and restores state in normal execution rather than doing
unsafe I/O inside a signal handler. `nanosleep()` yields between writes; this is
not a real-time waveform generator.

```c
--8<-- "labs/00-getting-started/led-blink/led-blink.c"
```

```makefile
--8<-- "labs/00-getting-started/led-blink/Makefile"
```

## Verification

On BBB, observe the selected LED respond to maximum/zero and six blink cycles.
`cat "$LED/trigger"` should show the intended active trigger in brackets after
restoration. With timer active, it should blink after the shell command has exited.
Timings are approximate and scheduling-dependent.

On a **development host**, without sudo or real LED writes:

```bash
make -C labs/00-getting-started/led-blink
python -m unittest discover -s tests -v
```

Fixtures verify maximum-brightness writes, completion restoration, invalid
arguments/missing attributes, and TERM restoration for Bash/C. Regular-file
fixtures do not emulate kernel trigger semantics or prove electrical output.

## Troubleshooting

- **Permission denied:** verify selected path/permissions; use scoped sudo on BBB.
- **No LEDs directory or unexpected names:** inspect kernel/Device Tree and
  booted image. Do not substitute arbitrary GPIO numbers.
- **Manual brightness immediately changes:** confirm active trigger is `none`.
- **No timer attributes:** select an available timer trigger first; if absent,
  kernel support may not be enabled. Bash blinking remains available.
- **Exec format error:** an x86 or incompatible ABI binary was copied to BBB;
  build natively on the target for this lesson.

## Exercises

Change cycle count, compare shell versus timer CPU activity, and explain why a
new kernel module is unnecessary for this experiment.

## Key Takeaways

Subsystem APIs hide board details. Discover attributes, preserve state, check
errors, and distinguish host code validation from hardware verification.

## Further Reading

- [Kernel LED class documentation](https://docs.kernel.org/leds/leds-class.html)
- [Linux open(2)](https://man7.org/linux/man-pages/man2/open.2.html)
- [Linux write(2)](https://man7.org/linux/man-pages/man2/write.2.html)
- [Linux close(2)](https://man7.org/linux/man-pages/man2/close.2.html)

## Lab Status

**Validated in a development environment:** Bash/C fixture tests, native C
compilation, and ShellCheck are provided and executed for the initial release.
**Not verified on physical BBB hardware:** LED names, kernel timer behavior,
visible output, and timing require your board/image evidence.
