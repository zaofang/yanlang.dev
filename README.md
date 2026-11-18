# yanlang.dev

The Yan website: home, tour, playground, status, blog (with an Atom feed), a generated reference (spec, rows, diagnostic codes, RFCs) with search and Markdown twins, and a text page for terminals (`curl yanlang.dev`).

| Path | What |
|---|---|
| `src/` | Pages (`index.md`, `tour/`, `blog/YYYY-MM-DD-slug.md`), `style.css`, `terminal.toml` |
| `build.py` | Renders `src/` plus the yan inputs to static files; checks the tour programs |
| `docs.py` | The reference pages, generated from `inputs/docs/`; see below |
| `worker.js`, `wrangler.jsonc` | Cloudflare Worker: `index.txt` to terminals at `/`, http to https |
| `tests/` | Builder tests |

## Yan inputs

Everything coupled to the compiler comes from the `site-inputs` release of zaofang/yan, published by that repository's `site-inputs` workflow after each green ci run on main. `uv run build.py fetch` extracts it into `inputs/`:

- `brand/`: the lockup, tokens, icons, favicons and social card (the single source is yan's `brand/`).
- `meta.json`: commit, date, CI status figures, conformance case counts per surface, RFC count (all stamped with the yan commit and date).
- `playground/`: `index.html`, `worker.js`, `examples.js` and `yan.wasm`, which version together.
- `docs/`: `spec/` (sections, `rows.toml`), `rfcs/`, `conformance/` (catalogue, manifest, small failing cases). The reference pages are skipped when it is absent.
- `yan` and `libyan_rt.a`: the compiler, used by `check`.

## Reference

`docs.py` generates, from `inputs/docs/` only (no page text is typed here):

| Path | What |
|---|---|
| `docs/` | Index with search over rows, codes, RFCs and section headings |
| `docs/spec/N.html` | Spec section N; headings are `#N.M`, row ids are anchors (`#R345`) |
| `docs/rows/` | Every row with its sections and conformance case count; rows with no case are flagged |
| `docs/codes/` | One page per diagnostic code: meaning, rows, a failing conformance case |
| `rfc/` | Accepted RFCs (drafts stay in the repository) |
| `docs/rows.json`, `docs/search.json` | Row to page map and the static search index |
| `*.md`, `llms.txt` | A Markdown twin of every reference page and an index of them |

`worker.js` redirects `/docs/spec/R345` and `/docs/spec/4.2` to the page and anchor. Every page carries the yan commit and date and a banner when it is older than seven days.

## Build

```sh
uv sync
uv run build.py fetch
uv run build.py check                  # tour programs on the interpreter and native backends
uv run build.py build _site
python3 -m http.server -d _site 8000
```

Pages are a Markdown subset (headings, paragraphs, lists, tables, fences, raw HTML blocks). A `yag`, `yn` or `yir` fence is a program with an "Open in playground" link; `check` runs it and compares stdout with the `output` fence after it. Fence attributes: `expect=E301` (must be rejected with that code), `exit=101`, `check` (check only, no run). The first tour program with its output is the terminal page.

`uv run pytest` runs the builder tests.

## Deploy

`.github/workflows/site.yml` builds on every PR (including `wrangler deploy --dry-run`) and deploys from main on push, every six hours, on demand, and on a `yan-site-inputs` repository_dispatch event. A red tour check blocks the deploy and leaves the last good site up. The deploy job runs in the GitHub environment `production` (deployment branches: main only), which holds `CLOUDFLARE_API_TOKEN` (a custom token: Workers Scripts Edit and Account Settings Read on the account, Workers Routes Edit on the yanlang.dev zone) and `CLOUDFLARE_ACCOUNT_ID`.

The Worker owns the apex domain (`wrangler.jsonc` custom domain). The Cloudflare Pages project that served the interim page must be detached from yanlang.dev first; never run both.
