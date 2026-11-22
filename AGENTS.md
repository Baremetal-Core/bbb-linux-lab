# Contributor and agent rules

- Preserve the progressive curriculum and separate docs, labs, and utilities.
- Follow `templates/lesson-template.md`; add one focused lesson at a time.
- Use minimal, understandable examples and existing dependencies.
- Never invent hardware test results. Distinguish documented, host-validated,
  and physically verified work. Record evidence before promoting lab status.
- Identify board-revision, image, bootloader, kernel, and networking assumptions.
  Never assume a particular MMC number, LED name, password, or IP address.
- Prefer BeagleBoard, TI, Linux kernel, Buildroot, Yocto, and upstream tool
  documentation. Explain in original language; do not copy proprietary courses.
- Keep executable examples buildable. Include expected results and recovery
  procedures. Use snippets for source in docs rather than duplicate code.
- Synchronize navigation and roadmap when adding lessons. Do not represent a
  planned topic as an implemented or tested lab.
- After changes, run `zensical build --clean` and
  `python scripts/host/check-docs.py`; run ShellCheck, C build, and tests for
  relevant code changes. See README for exact commands.
- Do not modify unrelated lessons or restructure the project unnecessarily.
- Never perform destructive hardware operations without explicit approval.
  Do not add auto-flashing, guessed disk targets, or privileged CI hardware tests.
- Never commit credentials, host-specific settings, board backups, or images.
