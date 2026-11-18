<section class="hero">
<p class="label">programming language</p>
<h1>A programming language that compiles to native code.</h1>
<p class="lede">Yan 言 can be written in more than one syntax. Each is checked and compiled by the same core, and programs reach the world only through capabilities they name.</p>
<p class="cta"><a class="btn btn-run" href="play/">Open the playground</a> <a class="btn" href="tour/">Take the tour</a> <a class="btn" href="install.html">Install</a></p>
</section>

<div class="pair">

```yag check
type Shape = Circle(r: int) | Rect(w: int, h: int) | Dot()

def area(s: Shape) -> int:
    match s:
        case Circle(r):
            return 3 * r * r
        case Rect(w, h):
            return w * h
        case Dot():
            return 0
```

```yn check
type Shape = Circle(r: int) | Rect(w: int, h: int) | Dot()

area(s: Shape) -> int uses none =
  Circle(r) -> 3 * r * r
  Rect(w, h) -> w * h
  Dot() -> 0
```

</div>

<div class="claims">
<div><span class="label">fast</span><b>Native code</b><p>Measured against Python and Rust on every commit.</p></div>
<div><span class="label">concurrent</span><b>par blocks</b><p>Parallel work is written with <code>par</code>.</p></div>
<div><span class="label">deterministic</span><b>Same result, every run</b><p>Whatever the scheduling.</p></div>
<div><span class="label">capability-safe</span><b>Named reach</b><p>Code touches the world only through capabilities it names.</p></div>
</div>

## Every surface gets

- **Checked failure.** Failures are part of a signature, handled with `else` or passed on with `?`.
- **Examples as tests.** Public functions carry `ex` lines the checker runs.
- **Native and interpreted.** The interpreter and the native backend agree, checked by differential tests.

[The language](language.html) · [Roadmap](roadmap.html) · [Status](status/)

## Surfaces

<div class="surfaces">
<a href="tour/"><img src="brand/file-icon-yag.svg" alt="" width="48" height="48"><b>Yan Agent</b><span>.yag</span><em>Python-shaped and typed, written by language models.</em></a>
<a href="tour/07-surfaces.html"><img src="brand/file-icon-yn.svg" alt="" width="48" height="48"><b>Yan</b><span>.yn</span><em>The syntax written for people.</em></a>
<a href="play/"><img src="brand/file-icon-yir.svg" alt="" width="48" height="48"><b>Yan Core</b><span>.yir</span><em>The core every surface lowers to.</em></a>
<a href="status/"><img src="brand/file-icon-ymt.svg" alt="" width="48" height="48"><b>Yan Meta</b><span>.ymt</span><em>Research surface, planned after M1.</em></a>
</div>

## Install

```sh
curl -fsSL https://github.com/zaofang/yan/releases/latest/download/install.sh | sh
brew install zaofang/yan/yan
```

Releases cover macOS (arm64, x86_64) and Linux (x86_64, arm64).

Start a package from a template (`cli`, `library` or `agent-tool`):

```sh
yan new --template cli total && cd total
yan test
printf '1\n2\n39\n' | yan run src/main.yag
```
