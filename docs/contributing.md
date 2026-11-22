# Contributing a lesson

Keep each contribution small: one observable experiment and the theory needed
to understand it. The repository's `AGENTS.md` applies to people and agents.

## Workflow

1. Choose the next dependency-ready topic from the [roadmap](roadmap.md).
2. Copy `templates/lesson-template.md` into the appropriate `docs/` module.
3. Put reusable code in `labs/`, host utilities in `scripts/host/`, and target
   utilities in `scripts/target/`. Use the existing snippets extension to show
   source without maintaining a second copy.
4. Add the page to `zensical.toml` navigation and update its roadmap status.
5. Build documentation, check links, and run relevant code checks described in
   the root README. A successful build alone does not prove all links work.
6. Submit a PR with checks run, exact assumptions, and unverified behavior.

## Lesson evidence

The template includes overview, measurable objectives, prerequisites, theory,
numbered lab, mechanisms, verification, troubleshooting, exercises, takeaways,
references, and lab status.

When reporting hardware verification, include date, printed board revision,
image source/checksum, kernel and bootloader where relevant, exact commands,
observations, and any deviations. Redact secrets and private network information.
Host fixtures test program behavior, not pin wiring, kernel trigger availability,
timings, or hardware recovery.

## Safety and originality

Use read-only discovery before configuration changes. Mark storage writes and
network changes prominently and provide a recovery path. Never ship a script
that guesses an eMMC target or automatically flashes the board.

Prefer upstream references and original explanations. Link official diagrams;
do not copy proprietary course figures or transcripts. Keep advanced roadmap
entries lightweight until a real lab is implemented.
