# The language

Yan is one core with many surfaces. A surface is a syntax; the core is what runs. Every surface is read
into the same checked form, Yan Core (`.yir`), and everything after that point is shared: the checker,
the optimizer and the backends.

<div class="flow" role="img" aria-label="Surfaces .yag, .yn and .ymt are read into Yan Core, which feeds the interpreter and native code.">
<div class="col"><span class="label">Surfaces</span><b>Yan Agent <i>.yag</i></b><b>Yan <i>.yn</i></b><b>Yan Meta <i>.ymt</i></b></div>
<div class="col core"><span class="label">One core</span><b>Yan Core <i>.yir</i></b><em>checked, then optimized</em></div>
<div class="col"><span class="label">Backends</span><b>Interpreter</b><b>Native code</b></div>
</div>

## Four claims

- **Fast.** Native code is the goal for every surface, benchmarked against Python and Rust on the
  [status page](status/#bench).
- **Concurrent.** Parallel work is written with `par` blocks.
- **Deterministic.** A `par` block gives the same result on every run, whatever the scheduling.
- **Capability-safe.** A function reaches the terminal, files, network or clock only through
  capabilities it names. Code that names none is pure.

## Surfaces

| Surface | Ext | State |
|---|---|---|
| Yan Agent | `.yag` | Built. Python-shaped and typed, written by language models. |
| Yan | `.yn` | Built. The syntax written for people. |
| Yan Core | `.yir` | Built. The core every surface lowers to. |
| Yan Meta | `.ymt` | Planned. Research surface, built after the first milestone. |
| Other job surfaces | `.ynsh`, `.ybf`, ... | Named, none built. |

## Failure and checking

Failures are part of a function's signature. They are handled with `else` or passed on with `?`, and are
checked. Public functions carry `ex` example lines that the
checker runs as tests. Ownership is checked before anything runs; see the tour.

Read the [tour](tour/) for each idea in one page, or open the [playground](play/) and print any
module in every surface.

## Specification

The Yan 0.1.0 specification is a draft. It is in the
[`spec/` directory](https://github.com/zaofang/yan/tree/main/spec) of the compiler repository, one
file per section, with a conformance suite that any implementation must pass.
