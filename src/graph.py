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
    edges = find_cycle_edges(adjacency)
    return len(edges) != EMPTY_COUNT


def find_cycle_edges(adjacency):
    """Return back edges (u, v) found during cycle DFS."""
    color = {}
    for node in adjacency:
        color[node] = COLOR_WHITE
    found = []
    for start in list(adjacency):
        if color.get(start, COLOR_WHITE) != COLOR_WHITE:
            continue
        _dfs_collect_cycles(start, adjacency, color, found)
    return found


def print_graph(adjacency, cycles):
    """Печатает граф зависимостей и найденные циклы."""
    print("=== Граф зависимостей ===")
    if len(adjacency) == EMPTY_COUNT:
        print("(пусто)")
    else:
        for node in adjacency:
            _print_node_edges(node, adjacency[node])
    print("=========================")
    _print_cycles(cycles)


def _print_node_edges(node, deps):
    """Печатает исходящие рёбра одного узла."""
    if len(deps) == EMPTY_COUNT:
        print(f"{node} ->")
        return
    joined = ", ".join(deps)
    print(f"{node} -> {joined}")


def _print_cycles(cycles):
    """Печатает информацию о циклических зависимостях."""
    print("=== Циклы ===")
    if len(cycles) == EMPTY_COUNT:
        print("(нет)")
    else:
        for src, dst in cycles:
            print(f"{src} -> {dst}")
    print("=============")


def _dfs_collect_cycles(start, adjacency, color, found):
    """Iterative DFS; append back edges to found."""
    stack = [(start, False)]
    while len(stack) != EMPTY_COUNT:
        node, leaving = stack.pop()
        if leaving:
            color[node] = COLOR_BLACK
            continue
        if color.get(node, COLOR_WHITE) == COLOR_BLACK:
            continue
        color[node] = COLOR_GRAY
        stack.append((node, True))
        _push_cycle_edges(node, adjacency, color, stack, found)


def _push_cycle_edges(node, adjacency, color, stack, found):
    """Push white neighbors; record gray back edges."""
    for dep in adjacency.get(node, []):
        state = color.get(dep, COLOR_WHITE)
        if state == COLOR_GRAY:
            found.append((node, dep))
            continue
        if state == COLOR_WHITE:
            stack.append((dep, False))


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
