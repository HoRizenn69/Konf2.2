"""Collect direct deps and build transitive graph."""

import sys

from src.cargo import fetch_cargo_deps
from src.constants import EMPTY_COUNT, EXIT_ERROR
from src.graph import build_graph_bfs, has_cycle


def collect_direct_deps(args):
    """Return direct dependencies for CLI args."""
    if args.test_mode:
        return _from_test_repo(args.repo, args.package)
    return _from_cargo(args.repo, args.package)


def collect_graph(args):
    """Build transitive graph (BFS) for CLI args.

    Returns (adjacency, edges, cycle_flag).
    """
    get_deps = _make_getter(args)
    root = _root_name(args)
    adjacency, edges = build_graph_bfs(
        root,
        get_deps,
        args.filter,
    )
    cycle = has_cycle(adjacency)
    return adjacency, edges, cycle


def print_deps(deps, package=""):
    """Print direct dependencies to stdout."""
    _print_header(package)
    if len(deps) == EMPTY_COUNT:
        print("(нет)")
    else:
        for name, req in deps:
            _print_one_dep(name, req)
    print("==========================")


def print_graph(adjacency, edges, package, cycle):
    """Print BFS graph edges and cycle note."""
    print(f"=== Dependency graph: {package} ===")
    if len(edges) == EMPTY_COUNT:
        print("(no edges)")
    else:
        for src, dst in edges:
            print(f"{src} -> {dst}")
    print("--- nodes ---")
    nodes = sorted(adjacency.keys())
    if len(nodes) == EMPTY_COUNT:
        print("(none)")
    else:
        print(", ".join(nodes))
    if cycle:
        print("cycle: yes")
    else:
        print("cycle: no")
    print("==========================")


def _root_name(args):
    """Normalize root package name for test mode."""
    if args.test_mode:
        return args.package.strip().upper()
    return args.package


def _make_getter(args):
    """Return get_deps(name) for test or crates.io."""
    if args.test_mode:
        graph = _load_test_graph(args.repo)
        return lambda name: list(graph.get(name, []))
    repo = args.repo

    def get_deps(name):
        return _cargo_names(repo, name)

    return get_deps


def _cargo_names(repo, package):
    """Direct dependency names; empty list on error."""
    try:
        pairs = fetch_cargo_deps(repo, package)
    except ValueError:
        return []
    return [name for name, _req in pairs]


def _print_header(package):
    """Print section header for direct deps."""
    if len(package) == EMPTY_COUNT:
        print("=== Прямые зависимости ===")
        return
    print(f"=== Прямые зависимости: {package} ===")


def _print_one_dep(name, req):
    """Print one dependency line."""
    if len(req) == EMPTY_COUNT:
        print(name)
    else:
        print(f"{name} {req}")


def _from_cargo(repo, package):
    """Load direct dependencies from crates.io."""
    try:
        return fetch_cargo_deps(repo, package)
    except ValueError as err:
        _fail(str(err))
    return []


def _from_test_repo(path, package):
    """Read direct dependencies from test file."""
    graph = _load_test_graph(path)
    key = package.strip().upper()
    if key not in graph:
        _fail(
            f"package {package} not found "
            "in test repository"
        )
    names = graph[key]
    return [(name, "") for name in names]


def _load_test_graph(path):
    """Load graph lines like 'A: B C' from a file."""
    graph = {}
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            _add_test_line(graph, raw)
    return graph


def _add_test_line(graph, raw):
    """Add one test-repository line to the graph."""
    line = raw.strip()
    if len(line) == EMPTY_COUNT:
        return
    if line.startswith("#"):
        return
    node, _, rest = line.partition(":")
    name = node.strip().upper()
    if len(name) == EMPTY_COUNT:
        return
    parts = rest.strip().split()
    deps = [item.upper() for item in parts]
    graph[name] = deps
    for dep in deps:
        if dep not in graph:
            graph[dep] = []


def _fail(message):
    """Print error and exit."""
    print(f"Ошибка: {message}", file=sys.stderr)
    sys.exit(EXIT_ERROR)
