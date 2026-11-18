import json
from pathlib import Path

from build import Build, render
from docs import doc_pages, expand_rows, number_headings, section_link

SPEC = """# Yan spec

## 4. Ownership

### 4.1 Moves

A move is final (R2). Rows R1 and R9999 appear. See [laws](02-laws.md#x) and [code](../crates/a.rs).

```yag
def f(): pass
```
"""


def make_docs(tmp: Path) -> Path:
    (tmp / "spec").mkdir(parents=True)
    (tmp / "rfcs").mkdir()
    (tmp / "conformance/cases/yag/fail").mkdir(parents=True)
    (tmp / "spec/04-own.md").write_text(SPEC)
    (tmp / "spec/appendix-a.md").write_text("## Appendix A\n")
    (tmp / "spec/rows.toml").write_text(
        '[[entry]]\nrows = "R1 to R2"\ntopic = "moves `x`"\nsections = "4.1, 4.7"\n'
    )
    (tmp / "rfcs/0001-a.md").write_text("# 0001: First\n\n- Status: accepted\n- Rows: R1\n")
    (tmp / "rfcs/0002-b.md").write_text("# 0002: Second\n\n- Status: draft\n")
    (tmp / "conformance/catalogue.toml").write_text(
        '[codes]\nE401 = { section = "4.1", status = "active", meaning = "use after move" }\n'
    )
    case = {"path": "yag/fail/m.yag", "kind": "fail", "rows": ["R1"], "spec": [], "flags": [],
            "expect": [{"code": "E401", "line": 3, "col": 1}]}
    (tmp / "conformance/manifest.json").write_text(json.dumps({"cases": [case]}))
    (tmp / "conformance/cases/yag/fail/m.yag").write_text("def f():\n    pass\n")
    return tmp


def test_expand_rows_reads_lists_and_ranges() -> None:
    assert expand_rows("R1, R3 (x), R5 to R7") == ["R1", "R3", "R5", "R6", "R7"]


def test_lists_nest_and_surface_fences_are_plain_text_when_not_run() -> None:
    page = render("- a\n  - b\n\n1. c\n\n```yag\nx\n```\n", "t.html", "", run=False)
    assert "<ul><li>a<ul><li>b</li></ul></li></ul>" in page.body
    assert "<ol><li>c</li></ol>" in page.body
    assert page.programs == []


def test_spec_rows_sections_codes_and_rfcs(tmp_path: Path) -> None:
    info = Build("a" * 40, "2026-11-18", "https://yanlang.dev/")
    pages, files = doc_pages(info, make_docs(tmp_path))
    by_path = {p.path: p.body for p in pages}
    spec = by_path["docs/spec/4.html"]
    assert 'id="4.1"' in spec and 'id="R2"' in spec
    assert 'href="../../docs/rows/#R1"' in spec
    assert "R9999" in spec and "#R9999" not in spec  # unknown rows stay plain
    assert 'href="https://github.com/zaofang/yan/blob/main/crates/a.rs"' in spec
    assert json.loads(files["docs/rows.json"]) == {"R1": "docs/spec/4.html#R1", "R2": "docs/spec/4.html#R2"}
    assert "rfc/0001.html" in by_path and "rfc/0002.html" not in by_path
    assert "rfc/0001.md" in files and "docs/spec/4.md" in files
    assert "docs/codes/E401.html" in by_path and "use after move" in by_path["docs/codes/E401.html"]
    assert "yag/fail/m.yag" in by_path["docs/codes/E401.html"]
    assert "no case" not in by_path["docs/rows/index.html"]
    assert "[0001 First](https://yanlang.dev/rfc/0001.md)" in files["llms.txt"]
    search = json.loads(files["docs/search.json"])
    assert ["row", "R1", "moves x", "docs/spec/4.html#R1"] in search


def test_section_links_fall_back_to_the_nearest_heading(tmp_path: Path) -> None:
    from docs import load

    d = load(make_docs(tmp_path))
    assert 'href="../docs/spec/4.html#4.1"' in section_link("4.1.3", "../", d)
    assert 'href="../docs/spec/4.html#4"' in section_link("4.9", "../", d)
    assert section_link("99", "../", d) == "99"


def test_headings_are_addressed_by_section_number() -> None:
    assert number_headings('<h3 id="x-y">4.2 Moves</h3>').startswith('<h3 id="4.2">')
