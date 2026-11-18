"""Checks a built site's internal links: every href and src resolves to a file, and every fragment to
an id on the target page. External links, and pages and fragments inside the playground bundle, are
skipped.

    uv run links.py _site
"""

import posixpath
import re
import sys
from pathlib import Path

LINK = re.compile(r'(?:href|src)="([^"]+)"')
ID = re.compile(r'\bid="([^"]+)"')
SKIP = re.compile(r"^(?:[a-z]+:|//)")


def resolve(site: Path, page: Path, target: str) -> Path | None:
    rel = posixpath.normpath(posixpath.join(page.parent.relative_to(site).as_posix(), target))
    if rel.startswith(".."):
        return None
    p = site / rel
    if p.is_dir():
        p = p / "index.html"
    elif not p.exists() and p.with_name(p.name + ".html").exists():
        p = p.with_name(p.name + ".html")
    return p if p.is_file() else None


def broken(site: Path) -> list[str]:
    ids: dict[Path, set[str]] = {}
    out = []
    for page in sorted(site.rglob("*.html")):
        if page.relative_to(site).parts[0] == "play":
            continue
        for link in LINK.findall(page.read_text()):
            if SKIP.match(link):
                continue
            path, _, frag = link.partition("#")
            target = resolve(site, page, path) if path else page
            where = page.relative_to(site).as_posix()
            if target is None:
                out.append(f"{where}: {link}: no such file")
            # The playground reads its fragment as program state, not as an id.
            elif frag and target.suffix == ".html" and target.relative_to(site).parts[0] != "play":
                if target not in ids:
                    ids[target] = set(ID.findall(target.read_text()))
                if frag not in ids[target]:
                    out.append(f"{where}: {link}: no id {frag!r}")
    return out


def main() -> int:
    bad = broken(Path(sys.argv[1]))
    for line in bad:
        print(line)
    print(f"{len(bad)} broken links")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
