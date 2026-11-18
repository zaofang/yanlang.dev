<section class="ink">
<div class="han" aria-hidden="true">言<i class="seal"></i></div>
<div>
<p class="label">Yan 言</p>
<h1>Nothing implicit.</h1>
<p class="lede">A typed language where effects, failures and parallelism are written down and checked.</p>
<div class="console"><div class="bar"><span>yan --help</span><a href="play/">open the playground</a></div><pre>fast              native code, measured against Python and Rust
concurrent        parallel work is written with <span class="k">par</span>
deterministic     same result, every run, whatever the scheduling
capability-safe   code touches the world only through
                  capabilities it names
<span class="p">$</span> curl -fsSL https://github.com/zaofang/yan/releases/latest/download/install.sh | sh</pre></div>
<p class="cta"><a class="btn btn-run" href="tour/">Take the tour</a> <a class="btn" href="docs/">Read the docs</a> <a class="btn" href="install.html">Install</a></p>
</div>
</section>

<div class="figures"></div>

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
