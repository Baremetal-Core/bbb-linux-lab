"""Check navigation, source links/snippets, and built local links and anchors."""

import argparse
import re
import sys
import tomllib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        for key in ("href", "src"):
            if attributes.get(key):
                self.links.append(attributes[key])


def nav_pages(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from nav_pages(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from nav_pages(item)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="zensical.toml")
    args = parser.parse_args()
    root = Path.cwd().resolve()
    project = tomllib.loads(Path(args.config).read_text())["project"]
    docs = root / project["docs_dir"]
    site = root / project["site_dir"]
    base = project["site_url"].rstrip("/") + "/"
    base_url = urlsplit(base)
    errors = []
    sources = set(docs.rglob("*.md"))
    nav = list(nav_pages(project["nav"]))
    nav_paths = {docs / value for value in nav if not urlsplit(value).scheme}
    for path in nav_paths - sources:
        errors.append(f"Navigation target missing: {path.relative_to(root)}")
    for path in sources - nav_paths:
        errors.append(f"Page missing from navigation: {path.relative_to(root)}")
    if len(nav) != len(set(nav)):
        errors.append("Duplicate navigation target")

    for path in sorted(sources | {root / "README.md", root / "AGENTS.md"}):
        text = path.read_text()
        for snippet in re.findall(r'--8<-- "([^"]+)"', text):
            if not (root / snippet).is_file():
                errors.append(f"{path.relative_to(root)}: missing snippet {snippet}")
        # Ignore code fences: examples are not Markdown links.
        text = re.sub(r"(?ms)^(```|~~~).*?^\1[ \t]*$", "", text)
        for link in re.findall(r"!?\[[^\]]*\]\(([^()\s]+)(?:\s+\"[^\"]*\")?\)", text):
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if not target.exists():
                errors.append(f"{path.relative_to(root)}: broken source link {link}")

    sections = [
        "Overview", "Learning Objectives", "Prerequisites", "Theory", "Hands-on Lab",
        "How It Works", "Verification", "Troubleshooting", "Exercises",
        "Key Takeaways", "Further Reading", "Lab Status",
    ]
    for path in sorted((docs / "00-getting-started").glob("[0-9][0-9]-*.md")):
        headings = set(re.findall(r"^## (.+)$", path.read_text(), re.MULTILINE))
        for heading in sections:
            if heading not in headings:
                errors.append(f"{path.relative_to(root)}: missing section {heading}")

    pages = {path.resolve(): Page(path.read_text()) for path in site.rglob("*.html")}
    if not pages:
        errors.append("No built HTML; run zensical build first")
    for source in sources:
        relative = source.relative_to(docs)
        if relative.name == "index.md":
            target = site / relative.with_suffix(".html")
        elif project.get("use_directory_urls", True):
            target = site / relative.with_suffix("") / "index.html"
        else:
            target = site / relative.with_suffix(".html")
        if target.resolve() not in pages:
            errors.append(f"Page not built: {relative}")

    count = 0
    for path, page in pages.items():
        current = urljoin(base, path.relative_to(site).as_posix())
        for link in page.links:
            url = urlsplit(urljoin(current, link))
            if (url.scheme, url.netloc) != (base_url.scheme, base_url.netloc):
                continue
            decoded_path = unquote(url.path)
            if not decoded_path.startswith(base_url.path):
                errors.append(f"{path.relative_to(site)}: link escapes site subpath: {link}")
                continue
            target = (site / decoded_path[len(base_url.path):]).resolve()
            if not target.is_relative_to(site):
                errors.append(f"{path.relative_to(site)}: link escapes build directory: {link}")
                continue
            if target.is_dir():
                target /= "index.html"
            count += 1
            if not target.is_file():
                errors.append(f"{path.relative_to(site)}: broken built link {link}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{path.relative_to(site)}: missing anchor {link}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {len(sources)} pages, navigation, source links/snippets, "
          f"lesson sections, and {count} built links/assets/anchors")
    print("External URLs and physical hardware are not tested by this check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
