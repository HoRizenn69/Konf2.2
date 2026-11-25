# Cargo dependency graph — stage 5 (full)

Variant 16. Konf2.2 base + stages 3–5.

## Stages

| Stage | How to run |
| --- | --- |
| 1 | `--print-config` |
| 2 | `--direct-only` |
| 3 | `--print-graph` |
| 4 | `--load-order` |
| 5 | default (graph text + PlantUML/SVG) |

Stage 5: **PlantUML** on stdout plus files in `output/`:
`<stem>.puml` and the image from `--output` (e.g. `out.svg`).

Required options: `--package`, `--repo`, `--output`.

There is no `--path` — use `--repo`.

## Windows (cmd.exe)

Open **cmd**, not Git Bash. `python` alone only prints
**Python** (Store alias) — always run the module via
`py -3` or `cli.bat`.

```bat
cd /d D:\konf2.3
```

Full demo + unit tests:

```bat
run.bat
```

Stage 3:

```bat
stage3.bat
```

or:

```bat
cli.bat --package A --repo fixtures\repo_simple.txt --output out.svg --test-mode --print-graph
```

Stage 4:

```bat
stage4.bat
```

or:

```bat
cli.bat --package A --repo fixtures\repo_simple.txt --output order.svg --test-mode --load-order
```

Stage 5:

```bat
stage5.bat
```

or:

```bat
cli.bat --package A --repo fixtures\repo_simple.txt --output out.svg --test-mode
```

Stage 1 / 2 examples:

```bat
cli.bat --package serde --repo https://crates.io/api/v1 --output x.svg --print-config
cli.bat --package serde --repo https://crates.io/api/v1 --output x.svg --direct-only
```

Three crates for stage 5 (network):

```bat
cli.bat --package serde --repo https://crates.io/api/v1 --output graph.svg
cli.bat --package cfg-if --repo https://crates.io/api/v1 --output graph.svg
cli.bat --package log --repo https://crates.io/api/v1 --output graph.svg
```

If `py` is missing, `cli.bat` falls back to `python -m`.
Do not type only `--package ...` — that is not a command.

## Example load order (package A)

```text
=== Load order: A ===
1. D
2. B
3. C
4. A
==========================
```

## vs `cargo tree`

`cargo` uses lockfile, features, and target OS.
This tool uses crates.io `normal` deps and a simple
topological order from the BFS graph. Order and set
can differ.