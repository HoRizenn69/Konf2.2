# Cargo dependency graph — stage 3

Variant 16. Practice 2. Based on accepted Konf2.2 + **stage 3**.

## What stage 3 does

- BFS graph (no recursion), transitive deps
- `--filter` skips packages by substring
- Cycles: no hang, prints `cycle: yes/no`
- `--test-mode` + file `fixtures/*.txt` (names `A`, `B`, …)

Stage 2 still works: add `--direct-only`.  
Stage 1: add `--print-config`.

## Options (required unless noted)

| Option | Meaning |
| --- | --- |
| `--package` | Crate name |
| `--repo` | `https://crates.io/api/v1` or path to test file |
| `--output` | File name `graph.svg` or `out.png` (no folders) |
| `--test-mode` | Use test graph file |
| `--filter` | Optional substring filter |
| `--direct-only` | Stage 2 only |
| `--print-config` | Stage 1 only |

There is **no** `--path` flag — use **`--repo`**.

## Windows

```bat
cd /d path\to\david-konfigs
run.bat
```

Manual test (no internet):

```bat
set PYTHONPATH=.
py -3 -m src.main --package A --repo fixtures\repo_simple.txt --output out.svg --test-mode
```

Stage 2:

```bat
py -3 -m src.main --package serde --repo https://crates.io/api/v1 --output graph.svg --direct-only
```

PyCharm Parameters example:

```text
--package A --repo fixtures/repo_simple.txt --output out.svg --test-mode
```

Working directory = project folder. Environment: `PYTHONPATH=.`

## Example output

```text
=== Dependency graph: A ===
A -> B
A -> C
B -> D
C -> D
--- nodes ---
A, B, C, D
cycle: no
==========================
```