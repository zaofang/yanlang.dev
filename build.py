"""Render yanlang.dev from content.toml as dist/index.html and dist/index.txt.

The lockup, tokens, favicon, stamp and the session program come from a clone of zaofang/yan.
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from string import Template

HERE = Path(__file__).parent
BRAND = Path("site/brand")
KEYWORDS = frozenset(
    "def fn pub let var if else elif for in while return match case with uses fail type "
    "import from as par class pass and or not None True False".split()
)
TOKEN = re.compile(r'(#.*$)|("(?:[^"\\\n]|\\.)*")|(\b\d[\d_]*\b)|([A-Za-z_]\w*)', re.M)


def tokens(yan: Path) -> str:
    t = json.loads((yan / BRAND / "tokens.json").read_text())

    def block(theme: dict) -> str:
        flat = {k: v for k, v in theme.items() if isinstance(v, str)}
        flat |= {f"syntax-{k}": v for k, v in theme["syntax"].items()}
        return " ".join(f"--y-{k}: {v};" for k, v in flat.items())

    return (
        f":root {{ {block(t['light'])} color-scheme: light; }}\n"
        f"@media (prefers-color-scheme: dark) {{ :root {{ {block(t['dark'])} color-scheme: dark; }} }}"
    )


def svg(path: Path) -> str:
    s = path.read_text().strip()
    return re.sub(r"<title>.*?</title>", "", s, flags=re.S)


def session(md: Path) -> tuple[str, str]:
    """The first yag program on the page and the output fence that follows it."""
    m = re.search(r"```yag\n(.*?)```\n+```output\n(.*?)```", md.read_text(), re.S)
    if not m:
        raise SystemExit(f"{md}: no yag program followed by an output fence")
    return m.group(1).rstrip("\n"), m.group(2).rstrip("\n")


def highlight(src: str) -> str:
    out, at = [], 0
    for m in TOKEN.finditer(src):
        out.append(html.escape(src[at : m.start()], quote=False))
        w = html.escape(m.group(0), quote=False)
        cls = "c" if m.group(1) else "s" if m.group(2) else "n" if m.group(3) else "k" if w in KEYWORDS else ""
        out.append(f'<span class="{cls}">{w}</span>' if cls else w)
        at = m.end()
    return "".join(out) + html.escape(src[at:], quote=False)


def built(yan: Path) -> str:
    log = ["git", "-C", str(yan), "log", "-1", "--format=%h · %cs"]
    return subprocess.run(log, check=True, capture_output=True, text=True).stdout.strip()


def text(c: dict, src: str, out: str, stamp: str) -> str:
    col = max(len(x["id"]) for x in c["links"]) + 3
    lines = ["言 yan", "", *c["lines"], "", f"$ cat {c['file']}", src, "", f"$ yan run {c['file']}", out, ""]
    for x in c["links"]:
        lines += [x["id"].ljust(col) + x["summary"], " " * col + x["url"]]
    return "\n".join([*lines, "", f"in development · {stamp}", "a zaofang project · 造坊出品"]) + "\n"


def page(c: dict, yan: Path, src: str, out: str, stamp: str) -> str:
    e = html.escape
    rows = "".join(
        f'<tr><td><a href="{x["url"]}">{e(x["id"])}</a></td><td class="d">{e(x["summary"])}</td>'
        f'<td class="m">{e(x["label"])}</td></tr>'
        for x in c["links"]
    )
    first, *rest = c["lines"]
    p = '<span class="p" aria-hidden="true">$ </span>'
    return Template((HERE / "page.html").read_text()).substitute(
        tokens=tokens(yan),
        lockup=svg(yan / BRAND / "lockup.svg"),
        avatar=svg(yan / BRAND / "zaofang-avatar.svg"),
        lines=f'{e(first)} <span class="m">{" ".join(e(x) for x in rest)}</span>',
        cat=f"{p}cat {e(c['file'])}\n{highlight(src)}",
        run=f"{p}yan run {e(c['file'])}\n" + f'<span class="m">{e(out)}</span>',
        rows=rows,
        stamp=e(stamp),
        github=c["github"],
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yan", type=Path, default=HERE.parent / "yan", help="clone of zaofang/yan")
    ap.add_argument("--out", type=Path, default=HERE / "dist")
    args = ap.parse_args()
    c = tomllib.loads((HERE / "content.toml").read_text())
    src, out = session(args.yan / c["session"])
    stamp = built(args.yan)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "index.html").write_text(page(c, args.yan, src, out, stamp))
    (args.out / "index.txt").write_text(text(c, src, out, stamp))
    shutil.copy(args.yan / BRAND / "favicon.svg", args.out / "favicon.svg")


if __name__ == "__main__":
    main()
