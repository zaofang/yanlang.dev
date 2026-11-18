from pathlib import Path

from links import broken


def test_missing_files_and_fragments_are_reported(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "index.html").write_text(
        '<a href="docs/">d</a><a href="docs/#ok">ok</a><a href="docs/#gone">x</a>'
        '<a href="nope.html">n</a><a href="https://x.dev/">e</a><a href="#top">t</a><i id="top"></i>'
    )
    (tmp_path / "docs/index.html").write_text('<h1 id="ok">ok</h1><a href="../index.html">home</a>')
    assert broken(tmp_path) == [
        "index.html: docs/#gone: no id 'gone'",
        "index.html: nope.html: no such file",
    ]
