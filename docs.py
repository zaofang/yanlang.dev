"""Reference pages generated from the yan repository: the spec, the row browser, diagnostic codes
and accepted RFCs, plus a search index, row-id map, Markdown twins and llms.txt.

Everything here is a view of `inputs/docs/` (packed by yan's tools/site_inputs.py); no text is copied
by hand, so the pages cannot drift from the spec.

inputs/docs/spec/*.md, spec/rows.toml, rfcs/*.md, conformance/catalogue.toml,
conformance/manifest.json, conformance/cases/<path> (fail cases that expect a code)
"""

import html
import json
import posixpath
import re
import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from build import Build, Page, inline, render

GITHUB = "https://github.com/zaofang/yan/blob/main/"
SPEC_FILE = re.compile(r"^(\d\d)-.*\.md$")
RFC_FILE = re.compile(r"^(\d{4})-.*\.md$")
ROW = re.compile(r"R(\d+)(?:\s+to\s+R(\d+))?")
NUMBERED = re.compile(r"^(#{2,4}) (\d+(?:\.\d+)*)\.?\s+(.*)$", re.M)
STALE_DAYS = 7


@dataclass
class Row:
    id: str
    topic: str
    sections: list[str]
    cases: list[str] = field(default_factory=list)
    where: str = ""


@dataclass
class Docs:
    sections: dict[int, tuple[str, str]]  # number -> (file name, markdown)
    appendix: str
    rows: dict[str, Row]
    codes: dict[str, dict[str, str]]
    rfcs: dict[str, tuple[str, str, str]]  # number -> (title, status, markdown)
    cases: list[dict]
    case_dir: Path
    entries: list[tuple[str, str, list[str]]] = field(default_factory=list)  # rows text, topic, sections
    anchors: set[str] = field(default_factory=set)


def expand_rows(text: str) -> list[str]:
    out = []
    for m in ROW.finditer(text):
        lo, hi = int(m[1]), int(m[2] or m[1])
        out += [f"R{n}" for n in range(lo, hi + 1)]
    return out


def load(docs: Path) -> Docs:
    spec = docs / "spec"
    sections = {}
    for f in sorted(spec.glob("*.md")):
        if m := SPEC_FILE.match(f.name):
            sections[int(m[1])] = (f.name, f.read_text())
    appendix = (spec / "appendix-a.md").read_text()
    cases = json.loads((docs / "conformance/manifest.json").read_text())["cases"]
    by_row: dict[str, list[str]] = {}
    for c in cases:
        for r in c["rows"]:
            by_row.setdefault(r, []).append(c["path"])
    rows: dict[str, Row] = {}
    entries = []
    for e in tomllib.loads((spec / "rows.toml").read_text())["entry"]:
        sec = [s.strip() for s in e["sections"].split(",")]
        entries.append((e["rows"], e["topic"], sec))
        for r in expand_rows(e["rows"]):
            rows[r] = Row(r, e["topic"], sec, by_row.get(r, []))
    codes = tomllib.loads((docs / "conformance/catalogue.toml").read_text())["codes"]
    rfcs = {}
    for f in sorted((docs / "rfcs").glob("*.md")):
        m = RFC_FILE.match(f.name)
        if not m or m[1] == "0000":
            continue
        text = f.read_text()
        title = re.search(r"^# \d{4}:\s*(.+)$", text, re.M)
        status = re.search(r"^- Status:\s*(.+)$", text, re.M)
        if status and status[1].strip().startswith("accepted"):
            rfcs[m[1]] = (title[1].strip() if title else f.stem, status[1].strip(), text)
    anchors = {m[2] for _, md in sections.values() for m in NUMBERED.finditer(md)}
    return Docs(sections, appendix, rows, codes, rfcs, cases, docs / "conformance/cases", entries, anchors)


def root_of(path: str) -> str:
    return "../" * path.count("/")


def spec_path(n: int | str) -> str:
    return f"docs/spec/{n}.html"


def rewrite_links(body: str, path: str, src_dir: str, d: Docs) -> str:
    """Relative links in repository Markdown: to spec and RFC pages on the site, else to GitHub."""
    spec_files = {name: n for n, (name, _) in d.sections.items()}
    root = root_of(path)

    def fix(m: re.Match[str]) -> str:
        href = m[1]
        if re.match(r"(https?:|mailto:|#)", href):
            return m[0]
        target, _, frag = href.partition("#")
        full = posixpath.normpath(posixpath.join(src_dir, target))
        name = posixpath.basename(full)
        if full == f"spec/{name}" and name in spec_files:
            new = root + spec_path(spec_files[name])
        elif full == "spec/appendix-a.md":
            new = root + spec_path("appendix-a")
        elif (r := RFC_FILE.match(name)) and full == f"rfcs/{name}" and r[1] in d.rfcs:
            new = f"{root}rfc/{r[1]}.html"
        else:
            new = GITHUB + full
        return f'href="{new}{"#" + frag if frag else ""}"'

    return re.sub(r'href="([^"]*)"', fix, body)


def linkify_rows(body: str, root: str, d: Docs, seen: set[str] | None) -> str:
    """Row ids in text link to the row browser. With `seen`, the first mention on a page gets the
    id the row map points at."""
    token = re.compile(r"(<pre.*?</pre>)|(<code>.*?</code>)|(<a .*?</a>)|(<[^>]+>)|\b(R\d{1,4})\b", re.S)

    def fix(m: re.Match[str]) -> str:
        r = m[5]
        if not r or r not in d.rows:
            return m[0]
        anchor = ""
        if seen is not None and r not in seen:
            seen.add(r)
            anchor = f' id="{r}"'
        return f'<a class="row"{anchor} href="{root}docs/rows/#{r}">{r}</a>'

    return token.sub(fix, body)


def number_headings(body: str) -> str:
    """Spec headings are addressed by their section number: `#4.2`."""
    def fix(m: re.Match[str]) -> str:
        n = m[2]
        return f'<h{m[1]} id="{n}"><a class="pin" href="#{n}">#</a>{n}{m[3]}'

    return re.sub(r'<h([1-6]) id="[^"]*">(\d+(?:\.\d+)*)(\.?\s)', fix, body)


def stale(info: Build) -> str:
    age = (date.today() - date.fromisoformat(info.day)).days
    if age <= STALE_DAYS:
        return ""
    return f'<p class="stale">Generated from yan {info.commit[:7]} on {info.day}, {age} days ago.</p>'


def wrap(body: str, info: Build) -> str:
    return f'<div class="doc">{stale(info)}{body}</div>'


def table(head: list[str], rows: list[list[str]], attrs: str = "") -> str:
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr" + (f" {a}" if a else "") + ">" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
                 for a, *cells in rows)
    return f"<table class=\"text\" {attrs}><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"


def section_link(text: str, root: str, d: Docs) -> str:
    """Section numbers in `text` ("9.6.1, 20") link to the spec; a number without a heading links
    to its nearest heading above it."""
    def fix(m: re.Match[str]) -> str:
        sec = m[0]
        major = int(sec.split(".")[0])
        if major not in d.sections:
            return sec
        at = sec
        while at and at not in d.anchors:
            at = at.rpartition(".")[0]
        return f'<a href="{root}{spec_path(major)}#{at or major}">{sec}</a>'

    return re.sub(r"\d+(?:\.\d+)*", fix, text)


def spec_pages(info: Build, d: Docs, seen: set[str]) -> tuple[list[Page], dict[str, str], list[list[str]]]:
    pages, files, entries = [], {}, []
    for n, (name, md) in [*d.sections.items(), (-1, ("appendix-a.md", d.appendix))]:
        path = spec_path("appendix-a" if n < 0 else n)
        page = render(md, path, root_of(path), run=False)
        body = number_headings(page.body)
        body = rewrite_links(body, path, "spec", d)
        body = linkify_rows(body, root_of(path), d, seen if n >= 0 else None)
        page.body = wrap(f'<p class="label">Spec</p>{body}', info)
        pages.append(page)
        files[path.removesuffix(".html") + ".md"] = md
        for m in NUMBERED.finditer(md):
            entries.append(["spec", m[2], m[3].strip(), f"{path}#{m[2]}"])
    return pages, files, entries


def plain(markdown: str) -> str:
    return re.sub(r"<[^>]+>", "", inline(markdown))


def row_pages(info: Build, d: Docs) -> tuple[Page, dict[str, str]]:
    """One table line per rows.toml entry; every row id in it is an anchor and links to the page
    that states it."""
    root = "../../"
    body, md = [], ["| Rows | Topic | Sections | Cases |", "| --- | --- | --- | --- |"]
    for rows_text, topic, secs in d.entries:
        ids = expand_rows(rows_text)
        anchors = "".join(f'<span id="{r}"></span>' for r in ids)
        label = ROW.sub(lambda m: _row_link(m, root, d), html.escape(rows_text))
        have = [d.rows[r] for r in ids]
        missing = sum(1 for r in have if not r.cases)
        total = sum(len(r.cases) for r in have)
        if missing == len(ids):
            cases = '<span class="label rejected nowrap">no case</span>'
        else:
            cases = f"{total}" + (f' <span class="label rejected nowrap">{missing} without</span>' if missing else "")
        query = html.escape(" ".join(ids) + " " + plain(topic) + " " + " ".join(secs), quote=True).lower()
        body.append([f'data-q="{query}"', anchors + label, inline(topic), section_link(", ".join(secs), root, d), cases])
        md.append(f"| {rows_text} | {topic} | {', '.join(secs)} | {total} |")
    bare = sum(1 for r in d.rows.values() if not r.cases)
    lead = (
        f"<p>{len(d.rows)} spec rows in {len(d.entries)} entries, {bare} rows without a conformance case. "
        f"Generated from yan {info.commit[:7]} on {info.day}.</p>"
        '<p><input type="search" placeholder="Filter rows: R345, ownership, 8.6" data-filter="rows" '
        'aria-label="Filter rows"></p>'
    )
    page_body = (
        f'<h1>Spec rows</h1>{lead}'
        f'{table(["Rows", "Topic", "Sections", "Cases"], body, "data-rows")}'
        f'<script src="{root}docs.js" defer></script>'
    )
    page = Page("docs/rows/index.html", "Spec rows", wrap(page_body, info))
    return page, {"docs/rows/index.md": "# Spec rows\n\n" + "\n".join(md) + "\n"}


def _row_link(m: re.Match[str], root: str, d: Docs) -> str:
    where = {r: d.rows[r].where for r in expand_rows(m[0]) if r in d.rows}
    first = where.get(f"R{m[1]}")
    return f'<a href="{root}{first}">{m[0]}</a>' if first else m[0]


def code_pages(info: Build, d: Docs) -> tuple[list[Page], dict[str, str], list[list[str]]]:
    by_code: dict[str, list[dict]] = {}
    for c in d.cases:
        for e in c["expect"]:
            by_code.setdefault(e["code"], []).append(c)
    pages, files, entries = [], {}, []
    index_rows, md = [], ["| Code | Status | Section | Meaning | Cases |", "| --- | --- | --- | --- | --- |"]
    for code, e in sorted(d.codes.items()):
        cases = by_code.get(code, [])
        path = f"docs/codes/{code}.html"
        root = "../../"
        meaning = e.get("meaning", "")
        status = e.get("status", "")
        sec = e.get("section", "")
        out = [f"<h1>{code}</h1>", f"<p>{html.escape(meaning)}</p>",
               f'<p class="label">{html.escape(status)} · spec {section_link(sec, root, d)}</p>']
        rows = sorted({r for c in cases for r in c["rows"]}, key=lambda r: (r[0], int(r[1:]) if r[1:].isdigit() else 0, r))
        if rows:
            out.append("<h2>Rows</h2><p>" + linkify_rows(", ".join(rows), root, d, None) + "</p>")
        shown = 0
        for c in cases:
            f = d.case_dir / c["path"]
            if shown == 2 or not f.is_file() or f.stat().st_size > 4096:
                continue
            line = next(x for x in c["expect"] if x["code"] == code)
            src = f.read_text()
            lang = c["path"].split("/")[0]
            out.append(f"<h2>Example</h2><p>Conformance case <a href=\"{GITHUB}conformance/{c['path']}\">"
                       f"<code>{html.escape(c['path'])}</code></a> is rejected with {code} at "
                       f"{line.get('line')}:{line.get('col')}.</p>")
            fence = render(f"```{lang if lang in ('yag', 'yn', 'yir') else ''}\n{src}```", path, root, run=False)
            out.append(fence.body)
            shown += 1
        if cases:
            out.append(f"<p>{len(cases)} conformance cases expect {code}.</p>")
        else:
            out.append("<p>No conformance case expects this code yet.</p>")
        pages.append(Page(path, code, wrap("".join(out), info)))
        files[path.removesuffix(".html") + ".md"] = f"# {code}\n\n{meaning}\n\n{status}, spec {sec}\n"
        entries.append(["code", code, meaning, path])
        index_rows.append([f'data-q="{html.escape(code + " " + meaning, quote=True).lower()}"',
                           f'<a href="{code}.html">{code}</a>', html.escape(status),
                           section_link(sec, root, d), html.escape(meaning), str(len(cases))])
        md.append(f"| {code} | {status} | {sec} | {meaning} | {len(cases)} |")
    lead = (f"<p>{len(d.codes)} codes. Generated from yan {info.commit[:7]} on {info.day}.</p>"
            '<p><input type="search" placeholder="Filter codes: E301, ownership" data-filter="codes" '
            'aria-label="Filter codes"></p>')
    body = (f"<h1>Diagnostic codes</h1>{lead}"
            f'{table(["Code", "Status", "Spec", "Meaning", "Cases"], index_rows, "data-rows")}'
            '<script src="../../docs.js" defer></script>')
    pages.append(Page("docs/codes/index.html", "Diagnostic codes", wrap(body, info)))
    files["docs/codes/index.md"] = "# Diagnostic codes\n\n" + "\n".join(md) + "\n"
    return pages, files, entries


def rfc_pages(info: Build, d: Docs) -> tuple[list[Page], dict[str, str], list[list[str]]]:
    pages, files, entries, rows = [], {}, [], []
    for n, (title, status, md) in d.rfcs.items():
        path = f"rfc/{n}.html"
        page = render(md, path, "../", run=False)
        body = rewrite_links(page.body, path, "rfcs", d)
        body = linkify_rows(body, "../", d, None)
        page.body = wrap(f'<p class="label">RFC {n}</p>{body}', info)
        pages.append(page)
        files[f"rfc/{n}.md"] = md
        entries.append(["rfc", n, title, path])
        rows.append([f'data-q="{html.escape(n + " " + title, quote=True).lower()}"',
                     f'<a href="{n}.html">{n}</a>', html.escape(title), html.escape(status)])
    body = (f"<h1>RFCs</h1><p>{len(d.rfcs)} accepted RFCs. Drafts and the studies behind them stay in "
            f'<a href="{GITHUB}rfcs/README.md">the repository</a>. Generated from yan '
            f"{info.commit[:7]} on {info.day}.</p>"
            '<p><input type="search" placeholder="Filter RFCs: 0084, packages" data-filter="rfcs" '
            'aria-label="Filter RFCs"></p>'
            f'{table(["RFC", "Title", "Status"], rows, "data-rows")}'
            '<script src="../docs.js" defer></script>')
    pages.append(Page("rfc/index.html", "RFCs", wrap(body, info)))
    return pages, files, entries


def index_page(info: Build, d: Docs) -> Page:
    sections = "".join(
        f'<li><a href="../{spec_path(n)}">{html.escape(_title(md))}</a></li>'
        for n, (_, md) in d.sections.items()
    )
    body = f"""<h1>Docs</h1>
<p><input type="search" placeholder="Search rows, codes, RFCs, sections: R345, E301, 0084, ownership" data-search aria-label="Search the docs"></p>
<ul class="hits" data-hits></ul>
<div class="cols">
<div><p class="label">Learn</p><ul><li><a href="../tour/">Tour</a></li><li><a href="../language.html">The language</a></li><li><a href="../install.html">Install</a></li></ul></div>
<div><p class="label">Reference</p><ul><li><a href="rows/">Spec rows</a> ({len(d.rows)})</li><li><a href="codes/">Diagnostic codes</a> ({len(d.codes)})</li><li><a href="../rfc/">RFCs</a> ({len(d.rfcs)} accepted)</li></ul></div>
<div><p class="label">Evidence</p><ul><li><a href="../status/">Status</a></li><li><a href="../llms.txt">llms.txt</a></li></ul></div>
</div>
<h2>Specification</h2>
<ol class="toc">{sections}<li><a href="../{spec_path("appendix-a")}">Traceability (appendix A)</a></li></ol>
<script src="../docs.js" defer></script>"""
    return Page("docs/index.html", "Docs", wrap(body, info))


def _title(md: str) -> str:
    m = re.search(r"^#{1,2} (?:\d+\.?\s+)?(.+)$", md, re.M)
    return m[1].strip() if m else ""


def doc_pages(info: Build, docs: Path) -> tuple[list[Page], dict[str, str]]:
    d = load(docs)
    seen: set[str] = set()
    pages, files, entries = spec_pages(info, d, seen)
    # The row's home: the page that mentions it first, else the first section its entry names.
    for page in pages:
        for r in re.findall(r'<a class="row" id="(R\d+)"', page.body):
            d.rows[r].where = f"{page.path}#{r}"
    for r in d.rows.values():
        if not r.where and r.sections:
            major = r.sections[0].split(".")[0]
            if major.isdigit() and int(major) in d.sections:
                r.where = f"{spec_path(int(major))}#{r.sections[0]}"
    row_page, row_files = row_pages(info, d)
    code_page_list, code_files, code_entries = code_pages(info, d)
    rfc_page_list, rfc_files, rfc_entries = rfc_pages(info, d)
    pages += [index_page(info, d), row_page, *code_page_list, *rfc_page_list]
    files |= row_files | code_files | rfc_files
    entries += [["row", r.id, plain(r.topic)[:90], r.where] for r in d.rows.values() if r.where]
    entries += code_entries + rfc_entries
    files["docs/rows.json"] = json.dumps({r.id: r.where for r in d.rows.values() if r.where}, indent=0)
    files["docs/search.json"] = json.dumps(entries, separators=(",", ":"), ensure_ascii=False)
    lines = ["# Yan", "", "> A typed language where effects, failures and parallelism are written down and checked.", "",
             f"Generated from yan {info.commit[:7]} on {info.day}. Every page has a Markdown twin at the same path with .md.", ""]
    lines += ["## Spec", *(f"- [{n}. {_title(md)}]({info.url}{spec_path(n).removesuffix('.html')}.md)" for n, (_, md) in d.sections.items())]
    lines += ["", "## Reference", f"- [Spec rows]({info.url}docs/rows/index.md)", f"- [Diagnostic codes]({info.url}docs/codes/index.md)", "",
              "## RFCs (accepted)", *(f"- [{n} {t}]({info.url}rfc/{n}.md)" for n, (t, _, _) in d.rfcs.items())]
    files["llms.txt"] = "\n".join(lines) + "\n"
    return pages, files
