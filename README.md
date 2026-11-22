# BeagleBone Black Linux Lab

A progressive Embedded Linux learning lab, from a safe first boot through
Linux internals, drivers, Buildroot, Yocto, and a custom BSP.

**[Read the course](https://baremetal-core.github.io/bbb-linux-lab/)** |
**[Curriculum](docs/roadmap.md)** |
**[Getting started](docs/00-getting-started/index.md)**

## What is ready

Seven introductory lessons cover hardware, existing eMMC boot, microSD boot,
careful eMMC installation, LEDs, Ethernet, and SSH. Bash/C LED examples and
read-only network diagnostics accompany the lessons. Advanced modules are
explicitly **planned**, not completed lessons.

**Validation is not hardware certification.** CI builds the website, checks
navigation/links, compiles C with warnings as errors, runs ShellCheck, and tests
LED behavior against temporary files. Physical BBB boot, flashing, LED output,
and networking still need verification on your board/image.

## Local documentation

Python **3.11 or newer** is required. On Ubuntu, install the matching
`python3-venv` package if `venv` is unavailable. On macOS, use a current Python 3.

```bash
git clone https://github.com/Baremetal-Core/bbb-linux-lab.git
cd bbb-linux-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
zensical serve
```

Open the URL printed by Zensical (normally `http://localhost:8000/`).
For a static build and validation:

```bash
zensical build --clean
python scripts/host/check-docs.py
shellcheck labs/00-getting-started/led-blink/blink.sh \
  labs/00-getting-started/network-diagnostics/diagnose.sh \
  scripts/target/board-info.sh
make -C labs/00-getting-started/led-blink
python -m unittest discover -s tests -v
```

An Ubuntu host or target needs `build-essential` for native C compilation.
Do not run the LED lab on a development host's real LEDs; tests use isolated
fixtures and never write to `/sys`. No flashing script is provided.

## Repository layout

| Path | Purpose |
| --- | --- |
| `docs/` | Course, prerequisites, full curriculum, contribution guide |
| `labs/00-getting-started/led-blink/` | Bash/C implementations and Makefile |
| `labs/00-getting-started/network-diagnostics/` | Read-only diagnostics |
| `scripts/host/` | Site metadata and documentation validation |
| `scripts/target/` | Read-only board inventory |
| `templates/lesson-template.md` | Format for one lesson at a time |
| `tests/` | Safe host-side LED regression tests |
| `.github/workflows/` | Validation and official Pages deployment |

Keep one Git history. MacBook authors source; OptiPlex provides always-on
SSH/UART and deployment; Ryzen builds large artifacts on demand. Transfer
artifacts, not parallel manually maintained source trees. Do not commit images,
credentials, private keys, or machine-specific network settings.

## GitHub Pages

Repository **Settings > Pages > Build and deployment > Source** must be
**GitHub Actions**. The `Documentation` workflow runs on `main` pushes and manual
dispatch. It uses `configure-pages`, builds static HTML, uploads a Pages
artifact, and deploys through `deploy-pages` to the `github-pages` environment.
No `gh-pages` branch, personal token, or backend is required.

The canonical site URL is taken from `configure-pages`; repository metadata
comes from `GITHUB_REPOSITORY`. `configure-site.py` writes an ignored
`zensical.pages.toml`, so repository-subpath and custom-domain deployments do
not require hardcoding an account in the workflow. Local preview keeps its
localhost URL. PRs run validation with read-only permissions and never deploy.

To reproduce a subpath build locally:

```bash
python scripts/host/configure-site.py \
  --site-url https://example.github.io/bbb-linux-lab/ \
  --repository example/bbb-linux-lab
zensical build --clean --config-file zensical.pages.toml
python scripts/host/check-docs.py --config zensical.pages.toml
```

## Contributing and next milestone

Follow [AGENTS.md](AGENTS.md) and the [lesson template](templates/lesson-template.md).
Record the actual revision, image, kernel, date, commands, and observations when
verifying hardware. Next: verify Module 00 on a physical BBB, then add the first
Linux fundamentals lesson without restructuring the course.

Licensed under [MIT](LICENSE). External materials retain their own licenses;
links do not imply endorsement.
