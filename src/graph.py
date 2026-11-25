"""Build dependency graph with BFS (no recursion)."""

from collections import deque

from src.constants import EMPTY_COUNT

COLOR_WHITE = 0
COLOR_GRAY = 1
COLOR_BLACK = 2


def should_skip(package, filt):
    """True if package name contains filter substring."""
    if len(filt) == EMPTY_COUNT:
        return False
    return filt.lower() in package.lower()


def build_graph_bfs(root, get_deps, filt):
    """Build transitive graph using iterative BFS.

    get_deps(name) -> list of dependency names.
    Skips packages matching filter. Cycles are safe:
    each node is expanded at most once.
    Returns (adjacency dict, edge list).
    """
    adjacency = {}
    edges = []
    queue = deque([root])
    visited = set()

    while len(queue) != EMPTY_COUNT:
        package = queue.popleft()
        if package in visited:
            continue
        if should_skip(package, filt):
            continue
        visited.add(package)
        deps = _filter_deps(get_deps(package), filt)
        adjacency[package] = deps
        _enqueue(package, deps, edges, queue, visited)
    return adjacency, edges


def _enqueue(package, deps, edges, queue, visited):
    """Record edges and push unseen children."""
    for dep in deps:
        edges.append((package, dep))
        if dep in visited:
            continue
        queue.append(dep)


def _filter_deps(deps, filt):
    """Drop dependencies that match the filter."""
    result = []
    for dep in deps:
        if should_skip(dep, filt):
            continue
        result.append(dep)
    return result


def has_cycle(adjacency):
    """True if the directed graph has a cycle."""
    color = {}
    for node in adjacency:
        color[node] = COLOR_WHITE
    for start in list(adjacency):
        if color.get(start, COLOR_WHITE) != COLOR_WHITE:
            continue
        if _dfs_cycle(start, adjacency, color):
            return True
    return False


def _dfs_cycle(start, adjacency, color):
    """Iterative DFS cycle search from start."""
    stack = [(start, False)]
    while len(stack) != EMPTY_COUNT:
        node, leaving = stack.pop()
        if leaving:
            color[node] = COLOR_BLACK
            continue
        if _cycle_at(node, color):
            return True
        if color.get(node, COLOR_WHITE) == COLOR_BLACK:
            continue
        color[node] = COLOR_GRAY
        stack.append((node, True))
        if _push_neighbors(node, adjacency, color, stack):
            return True
    return False


def _cycle_at(node, color):
    """True if node is currently on the DFS path."""
    return color.get(node, COLOR_WHITE) == COLOR_GRAY


def _push_neighbors(node, adjacency, color, stack):
    """Push white neighbors; True if gray neighbor seen."""
    for dep in adjacency.get(node, []):
        state = color.get(dep, COLOR_WHITE)
        if state == COLOR_GRAY:
            return True
        if state == COLOR_WHITE:
            stack.append((dep, False))
    return False


def load_order(adjacency, root):
    """Load order: dependencies first, root last (no recursion)."""
    order = []
    visited = set()
    stack = [(root, False)]

    while len(stack) != EMPTY_COUNT:
        node, done = stack.pop()
        if done:
            order.append(node)
            continue
        if node in visited:
            continue
        if node not in adjacency and node != root:
            continue
        visited.add(node)
        stack.append((node, True))
        children = adjacency.get(node, [])
        for dep in reversed(children):
            if dep not in visited:
                stack.append((dep, False))
    return order
