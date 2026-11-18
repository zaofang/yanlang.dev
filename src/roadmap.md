# Roadmap

Yan is a 0.1.0 draft. This page names the milestones in the spec and what each one is for. Figures
(cases passing, spec debt, benchmarks) are generated per commit on the [status page](status/); nothing
here is a measurement.

| Milestone | What it delivers |
|---|---|
| M0 | Yan Core: the data types, text format and validator. |
| M1 | Yan Agent and the agent toolchain: reader, lenient reader, elaborator, checker, interpreter. |
| M1b | Native code: JIT first, then ahead-of-time output. |
| M2 | Systems layer, performance (the gate is Rust parity) and the standard library. |
| M3 | Yan, the human syntax, projections between surfaces, and self-hosting stages S1 to S3. |
| RC | Release candidate: the 0.1.0 edition is named and the freeze list takes effect. |
| 0.1.x | Releases under the release train, after 0.1.0. |
| M4 | Depth: proof level with an SMT solver, arena references, reflection. |

Yan Meta and the other named surfaces are planned after the first milestone and are not part of 0.1.0.

## Where to follow

- [Status](status/): conformance by milestone, differential runs, spec debt and benchmarks.
- [Blog](blog/): what changed, with an Atom feed.
- [Specification](https://github.com/zaofang/yan/tree/main/spec): section 23 holds the acceptance
  criteria for every milestone.
