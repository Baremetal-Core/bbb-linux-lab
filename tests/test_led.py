"""Exercise LED programs on temporary files, never on physical hardware."""

import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/00-getting-started/led-blink"


class LedTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.led = Path(self.directory.name)
        (self.led / "trigger").write_text("none [heartbeat] timer\n")
        (self.led / "brightness").write_text("0\n")
        (self.led / "max_brightness").write_text("255\n")
        self.commands = [
            ["bash", str(LAB / "blink.sh")],
            [str(LAB / "led-blink")],
        ]

    def run_lab(self, command, cycles):
        return subprocess.run(
            command + [str(self.led), cycles], capture_output=True, text=True, timeout=5
        )

    def reset_trigger(self):
        (self.led / "trigger").write_text("none [heartbeat] timer\n")

    def assert_restored(self):
        self.assertEqual((self.led / "brightness").read_text().strip(), "0")
        self.assertEqual((self.led / "trigger").read_text().strip(), "heartbeat")

    def test_blink_and_restore(self):
        for command in self.commands:
            with self.subTest(command=command):
                self.reset_trigger()
                process = subprocess.Popen(
                    command + [str(self.led), "1"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                try:
                    deadline = time.monotonic() + 2
                    while time.monotonic() < deadline:
                        if (self.led / "brightness").read_text().strip() == "255":
                            break
                        time.sleep(0.01)
                    else:
                        self.fail("LED never reached maximum brightness")
                    _, error = process.communicate(timeout=5)
                    self.assertEqual(process.returncode, 0, error)
                    self.assert_restored()
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.communicate()

    def test_invalid_cycles_do_not_write(self):
        for command in self.commands:
            for cycles in ("0", "-1", "garbage", "999999999999999999999"):
                with self.subTest(command=command, cycles=cycles):
                    result = self.run_lab(command, cycles)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(
                        (self.led / "trigger").read_text(), "none [heartbeat] timer\n"
                    )

    def test_missing_attribute_does_not_write(self):
        (self.led / "max_brightness").unlink()
        for command in self.commands:
            result = self.run_lab(command, "1")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                (self.led / "trigger").read_text(), "none [heartbeat] timer\n"
            )

    def test_termination_restores_state(self):
        for command in self.commands:
            with self.subTest(command=command):
                self.reset_trigger()
                process = subprocess.Popen(
                    command + [str(self.led), "10"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                try:
                    deadline = time.monotonic() + 2
                    while time.monotonic() < deadline:
                        if (self.led / "brightness").read_text().strip() == "255":
                            break
                        time.sleep(0.01)
                    else:
                        self.fail("LED never started")
                    process.send_signal(signal.SIGTERM)
                    _, error = process.communicate(timeout=5)
                    self.assertEqual(process.returncode, 143, error)
                    self.assert_restored()
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.communicate()


if __name__ == "__main__":
    unittest.main()
