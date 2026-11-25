"""Tests for BFS graph, filter and cycles."""

import os
import sys
import unittest

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, ROOT)

from src.graph import (  # noqa: E402
    build_graph_bfs,
    has_cycle,
    load_order,
    should_skip,
)


class TestGraph(unittest.TestCase):
    """Graph operations for stage 3."""

    def setUp(self):
        """Simple DAG used in several tests."""
        self.repo = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }

    def test_should_skip(self):
        """Filter matches substring in name."""
        self.assertTrue(should_skip("XXC", "XX"))
        self.assertFalse(should_skip("ABC", ""))
        self.assertFalse(should_skip("ABC", "ZZ"))

    def test_bfs_edges(self):
        """BFS collects transitive edges."""
        get_deps = lambda n: list(self.repo.get(n, []))
        adjacency, edges = build_graph_bfs(
            "A",
            get_deps,
            "",
        )
        self.assertIn("D", adjacency)
        self.assertIn(("A", "B"), edges)
        self.assertIn(("B", "D"), edges)
        self.assertFalse(has_cycle(adjacency))

    def test_bfs_filter(self):
        """Packages with filter substring are skipped."""
        repo = {
            "A": ["B", "XXC"],
            "B": ["D"],
            "XXC": ["D"],
            "D": [],
        }
        get_deps = lambda n: list(repo.get(n, []))
        adjacency, edges = build_graph_bfs(
            "A",
            get_deps,
            "XX",
        )
        targets = [dst for _src, dst in edges]
        self.assertNotIn("XXC", targets)
        self.assertNotIn("XXC", adjacency)

    def test_load_order(self):
        """Dependencies appear before the root package."""
        order = load_order(self.repo, "A")
        self.assertEqual(order[-1], "A")
        self.assertLess(order.index("D"), order.index("B"))

    def test_cycle_handled(self):
        """Cycle does not loop forever and is detected."""
        repo = {"A": ["B"], "B": ["C"], "C": ["A"]}
        get_deps = lambda n: list(repo.get(n, []))
        adjacency, edges = build_graph_bfs(
            "A",
            get_deps,
            "",
        )
        self.assertEqual(len(adjacency), 3)
        self.assertIn(("C", "A"), edges)
        self.assertTrue(has_cycle(adjacency))


if __name__ == "__main__":
    unittest.main()
