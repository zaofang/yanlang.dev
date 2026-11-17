import base64
import json
import zlib
from pathlib import Path

from build import Build, build, layout, pages, render, share_hash, status_page, terminal_page


def test_share_hash_round_trips_through_raw_deflate() -> None:
    text = 'pub def main() uses io:\n    io.print("hi")\n'
    lang, data = share_hash("yag", text).split("/")
    raw = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
    assert lang == "yag"
    assert zlib.decompress(raw, -15).decode() == text


def test_output_fence_attaches_to_the_program_before_it() -> None:
    page = render("# T\n\n```yag exit=101\nx\n```\n\n```output\n2\n```\n", "tour/t.html", "../")
    [p] = page.programs
    assert (p.exit, p.stdout, page.title) == (101, "2\n", "T")
    assert 'href="../play/#yag/' in page.body


def test_every_page_renders_with_relative_links(tmp_path: Path) -> None:
    build = Build("0" * 40, "2026-01-01", "")
    all_pages, feed = pages(build)
    paths = {p.path for p in all_pages}
    assert {"index.html", "tour/index.html", "status/index.html", "blog/index.html"} <= paths
    for p in all_pages:
        assert 'href="/' not in layout(p, build, "")
    assert feed.startswith("<?xml")


def test_terminal_page_shows_the_first_tour_program_and_absolute_links() -> None:
    build = Build("abcdef0" + "0" * 33, "2026-01-01", "https://yanlang.dev/")
    tour = next(p for p in pages(build)[0] if p.path.startswith("tour/0"))
    text = terminal_page(tour, build)
    hello = tour.programs[0]
    assert hello.source.rstrip("\n") in text and hello.stdout and hello.stdout in text
    assert "https://yanlang.dev/play/" in text and "<" not in text
    assert "abcdef0 on 2026-01-01" in text


def test_build_from_inputs_writes_playground_status_and_terminal_page(tmp_path: Path) -> None:
    inputs = tmp_path / "inputs"
    (inputs / "playground").mkdir(parents=True)
    (inputs / "brand").mkdir()
    (inputs / "brand/lockup.svg").write_text("<svg/>")
    (inputs / "brand/x.svg").write_text("<svg/>")
    (inputs / "playground/yan.wasm").write_bytes(b"\0asm")
    meta = {"commit": "abcdef0" + "0" * 33, "day": "2026-01-01", "status": None, "cases": {"core": 3}, "rfcs": 2}
    (inputs / "meta.json").write_text(json.dumps(meta))
    out = tmp_path / "out"
    build(out, "https://yanlang.dev/", inputs)
    assert (out / "play/yan.wasm").exists() and (out / "index.txt").exists()
    assert "Conformance cases" in (out / "status/index.html").read_text()


def test_status_page_renders_every_section_with_its_commit() -> None:
    data = {
        "commit": "abcdef0123",
        "date": "2026-01-02",
        "conformance": {
            "executors": ["interp"],
            "milestones": {"M0": {"cases": 4, "pass": 3, "fail": 1, "skip": 0}},
        },
        "differential": {
            "backends": ["interp", "cranelift"],
            "programs": 9,
            "unexplained": 0,
            "allowlisted": 2,
            "refused": 1,
            "stale": 0,
        },
        "spec_debt": {"rows": 10, "rows_without_case": 4, "codes": 5, "codes_unimplemented": 1},
        "bench": {"env": {"system": "Linux", "machine": "x86_64"}, "programs": []},
    }
    body = status_page(Build("0" * 40, "2026-01-03", "", data)).body
    for anchor in ("conformance", "differential", "spec-debt", "bench"):
        assert f'id="{anchor}"' in body
    assert body.count("<code>abcdef0</code>, 2026-01-02") == 4
    assert "<td>75%</td>" in body


def test_status_page_says_when_it_has_no_data() -> None:
    assert "no CI status data" in status_page(Build("0" * 40, "2026-01-03", "")).body
