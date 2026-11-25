"""PlantUML text and SVG image for the graph."""

import html
import os

from src.constants import (
    EMPTY_COUNT,
    OUTPUT_DIR,
    SVG_GAP_X,
    SVG_GAP_Y,
    SVG_NODE_HEIGHT,
    SVG_NODE_WIDTH,
    SVG_PAD,
)


def to_plantuml(edges, root):
    """Build PlantUML source for the dependency graph."""
    lines = ["@startuml", f'title "{_escape(root)}"']
    seen = set()
    for src, dst in edges:
        key = (src, dst)
        if key in seen:
            continue
        seen.add(key)
        lines.append(
            f'"{_escape(src)}" --> "{_escape(dst)}"'
        )
    if len(edges) == EMPTY_COUNT:
        lines.append(f'component "{_escape(root)}"')
    lines.append("@enduml")
    return "\n".join(lines)


def _escape(name):
    """Escape quotes in node labels."""
    return name.replace('"', "'")


def to_svg(adjacency, root):
    """Build a simple SVG diagram."""
    levels = _bfs_levels(adjacency, root)
    positions = _layout(levels)
    width, height = _canvas_size(positions)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}">',
        "<style>text{font-family:sans-serif;"
        "font-size:12px;text-anchor:middle;"
        "dominant-baseline:middle}</style>",
    ]
    _draw_edges(parts, adjacency, positions)
    _draw_nodes(parts, positions)
    parts.append("</svg>")
    return "\n".join(parts)


def save_artifacts(output_name, plantuml, svg_text):
    """Write .puml and image file under output/."""
    folder = os.path.join(os.getcwd(), OUTPUT_DIR)
    os.makedirs(folder, exist_ok=True)
    stem = _stem(output_name)
    puml_path = os.path.join(folder, stem + ".puml")
    image_path = os.path.join(folder, output_name)
    _write_text(puml_path, plantuml)
    _write_text(image_path, svg_text)
    return puml_path, image_path


def _stem(filename):
    """Base name without extension."""
    base = os.path.basename(filename)
    name, _ext = os.path.splitext(base)
    if len(name) == EMPTY_COUNT:
        return "graph"
    return name


def _write_text(path, content):
    """Write UTF-8 text file."""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def _bfs_levels(adjacency, root):
    """Assign nodes to BFS depth levels."""
    from collections import deque

    buckets = {}
    queue = deque([(root, 0)])
    seen = {root}
    while len(queue) != EMPTY_COUNT:
        node, depth = queue.popleft()
        buckets.setdefault(depth, []).append(node)
        for dep in adjacency.get(node, []):
            if dep in seen:
                continue
            seen.add(dep)
            queue.append((dep, depth + 1))
    levels = []
    for depth in sorted(buckets):
        levels.append(buckets[depth])
    if not levels:
        levels = [[root]]
    return levels


def _layout(levels):
    """Node center positions for SVG."""
    positions = {}
    for depth, row in enumerate(levels):
        y = SVG_PAD + depth * (SVG_NODE_HEIGHT + SVG_GAP_Y)
        for index, name in enumerate(row):
            x = (
                SVG_PAD
                + index * (SVG_NODE_WIDTH + SVG_GAP_X)
                + SVG_NODE_WIDTH // 2
            )
            cy = y + SVG_NODE_HEIGHT // 2
            positions[name] = (x, cy)
    return positions


def _canvas_size(positions):
    """SVG canvas width and height."""
    if not positions:
        pad = SVG_PAD * 2
        return pad, pad
    max_x = max(x for x, _y in positions.values())
    max_y = max(y for _x, y in positions.values())
    w = max_x + SVG_NODE_WIDTH // 2 + SVG_PAD
    h = max_y + SVG_NODE_HEIGHT // 2 + SVG_PAD
    return w, h


def _draw_edges(parts, adjacency, positions):
    """Draw edge lines between nodes."""
    for src, deps in adjacency.items():
        if src not in positions:
            continue
        x1, y1 = positions[src]
        for dst in deps:
            if dst not in positions:
                continue
            x2, y2 = positions[dst]
            parts.append(
                f'<line x1="{x1}" y1="{y1}" '
                f'x2="{x2}" y2="{y2}" '
                'stroke="#333" stroke-width="1.5"/>'
            )


def _draw_nodes(parts, positions):
    """Draw boxes and labels."""
    half_w = SVG_NODE_WIDTH // 2
    half_h = SVG_NODE_HEIGHT // 2
    for name, (cx, cy) in positions.items():
        x = cx - half_w
        y = cy - half_h
        label = html.escape(name)
        parts.append(
            f'<rect x="{x}" y="{y}" '
            f'width="{SVG_NODE_WIDTH}" '
            f'height="{SVG_NODE_HEIGHT}" '
            'rx="6" fill="#e8f1ff" stroke="#336"/>'
        )
        parts.append(f'<text x="{cx}" y="{cy}">{label}</text>')