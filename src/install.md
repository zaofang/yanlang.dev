# Install

Releases cover macOS (arm64, x86_64) and Linux (x86_64, arm64).

```sh
curl -fsSL https://github.com/zaofang/yan/releases/latest/download/install.sh | sh
```

or with Homebrew:

```sh
brew install zaofang/yan/yan
```

## First program

Save this as `hello.yag`:

```yag
pub def main() uses io:
    io.print("hello, world")
```

```output
hello, world
```

Run it with `yan run hello.yag`; the output is the block above.

`uses io` names the capability the function needs. Without it the checker rejects the program.

## First package

Start from a template (`cli`, `library` or `agent-tool`):

```sh
yan new --template cli total && cd total
yan test
printf '1\n2\n39\n' | yan run src/main.yag
```

## Next

- [Tour](tour/): the language, one idea per page.
- [Playground](play/): check and run Yan in the browser, nothing to install.
- [Source](https://github.com/zaofang/yan): compiler, spec and conformance suite.
