#!/bin/sh
# Cloudflare Pages build: fetch Yan's brand files and first tour page, then render dist/.
set -eu
yan=$(mktemp -d)/yan
git clone --quiet --depth 1 --filter=blob:none --sparse https://github.com/zaofang/yan "$yan"
git -C "$yan" sparse-checkout set site/brand site/tour
python3 build.py --yan "$yan"
