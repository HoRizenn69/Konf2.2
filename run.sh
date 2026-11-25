#!/bin/bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH="."

CRATES="https://crates.io/api/v1"
PY="python3 -m src.main"

echo "=== TEST: print-graph simple ==="
$PY --package A \
  --repo fixtures/repo_simple.txt \
  --output out.svg \
  --test-mode \
  --print-graph

echo "=== TEST: simple PlantUML/SVG ==="
$PY --package A \
  --repo fixtures/repo_simple.txt \
  --output out.svg \
  --test-mode

echo "=== TEST: cycle ==="
$PY --package A \
  --repo fixtures/repo_cycle.txt \
  --output cycle.svg \
  --test-mode

echo "=== TEST: filter XX ==="
$PY --package A \
  --repo fixtures/repo_filter.txt \
  --output filter.svg \
  --test-mode \
  --filter XX

echo "=== TEST: load-order simple ==="
$PY --package A \
  --repo fixtures/repo_simple.txt \
  --output order.svg \
  --test-mode \
  --load-order

echo "=== TEST: load-order cycle ==="
$PY --package A \
  --repo fixtures/repo_cycle.txt \
  --output order.svg \
  --test-mode \
  --load-order

echo "=== TEST: crates.io cfg-if ==="
$PY --package cfg-if --repo "$CRATES" --output graph.svg

echo "=== Unit tests ==="
python3 -m unittest discover -s tests -v

echo "=== DONE ==="