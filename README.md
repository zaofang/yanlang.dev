# yanlang.dev

The interim Yan home page. One source, `content.toml`, renders to `dist/index.html` for browsers and `dist/index.txt` for terminals:

```sh
curl yanlang.dev
```

Links go to the Yan repository until the full site is hosted.

The lockup, colour tokens, favicon and stamp are read from a clone of zaofang/yan (`site/brand/`), never copied in. The session on the page is the first program of `site/tour/01-hello.md` with its output fence, which the Yan site checks on the interpreter and native backends. The footer carries the commit and date of that clone.

## Build

```sh
uv run build.py --yan ../yan
sh build.sh                       # sparse-clones zaofang/yan to a temp dir first
```

## Deploy

Cloudflare Pages, connected to this repository:

| Setting | Value |
|---|---|
| Build command | `sh build.sh` |
| Output directory | `dist` |
| Environment variable | `PYTHON_VERSION=3.13` |

`functions/_middleware.js` sends `index.txt` to curl, wget, HTTPie and xh at `/`, and HTML to everyone else.

## Edit

Change `content.toml` for words and links, `page.html` for layout.
