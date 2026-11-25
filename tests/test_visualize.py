"""Tests for PlantUML and SVG."""

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, ROOT)

from src.visualize import (
    save_artifacts,
    to_plantuml,
    to_svg,
)


class TestVisualize(unittest.TestCase):
    """Stage 5 text and image output."""

    def test_plantuml_edge(self):
        """PlantUML contains an edge line."""
        text = to_plantuml([("A", "B")], "A")
        self.assertIn("@startuml", text)
        self.assertIn('"A" --> "B"', text)
        self.assertIn("@enduml", text)

    def test_svg_nodes(self):
        """SVG lists root and child."""
        adjacency = {"A": ["B"], "B": []}
        svg = to_svg(adjacency, "A")
        self.assertIn("<svg", svg)
        self.assertIn(">A</text>", svg)
        self.assertIn(">B</text>", svg)

    def test_save_artifacts(self):
        """Files are written under output/."""
        with tempfile.TemporaryDirectory() as tmp:
            old = os.getcwd()
            os.chdir(tmp)
            try:
                puml, image = save_artifacts(
                    "g.svg",
                    "@startuml\n@enduml",
                    "<svg></svg>",
                )
                self.assertTrue(os.path.isfile(puml))
                self.assertTrue(os.path.isfile(image))
            finally:
                os.chdir(old)


if __name__ == "__main__":
    unittest.main()