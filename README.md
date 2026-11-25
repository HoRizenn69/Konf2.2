# Cargo dependency graph — stage 5 (full)

Variant 16. Konf2.2 base + stages 3–5.

## Stages

| Stage | How to run |
| --- | --- |
| 1 | `--print-config` |
| 2 | `--direct-only` |
| 3 | BFS graph (same collection as 4–5; use tests) |
| 4 | `--load-order` |
| 5 | default (no extra flag) |

Stage 5: **PlantUML** on stdout plus files in `output/`:
`<stem>.puml` and the image from `--output` (e.g. `out.svg`).

Required options: `--package`, `--repo`, `--output`.

There is no `--path` — use `--repo`.

## Windows

```bat
cd /d path\to\david-konfigs
run.bat
```

Stage 5 (test file):

```bat
set PYTHONPATH=.
py -3 -m src.main --package A --repo fixtures\repo_simple.txt --output out.svg --test-mode
```

Stage 4:

```bat
py -3 -m src.main --package A --repo fixtures\repo_simple.txt --output order.svg --test-mode --load-order
```

Three crates for stage 5 (needs network):

```bat
run.bat serde
run.bat cfg-if
run.bat log
```

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