"""Create a deploy-specific config without changing local preview settings."""

import argparse
import json
import re
import tomllib
from pathlib import Path
from urllib.parse import urlsplit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-url", required=True)
    parser.add_argument("--repository", required=True, help="owner/repository")
    args = parser.parse_args()
    url = urlsplit(args.site_url)
    if url.scheme not in ("https", "http") or not url.netloc or url.query or url.fragment:
        parser.error("--site-url must be an absolute HTTP(S) URL without query/fragment")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        parser.error("--repository must be owner/repository")
    text = Path("zensical.toml").read_text()
    settings = {
        "site_url": args.site_url.rstrip("/") + "/",
        "repo_url": "https://github.com/" + args.repository,
        "repo_name": args.repository,
    }
    for key, value in settings.items():
        text, count = re.subn(
            rf"^{key} = .*$", f"{key} = {json.dumps(value)}", text, flags=re.MULTILINE
        )
        if count != 1:
            raise ValueError(f"Expected exactly one {key} in configuration")
    tomllib.loads(text)
    Path("zensical.pages.toml").write_text(text)


if __name__ == "__main__":
    main()
