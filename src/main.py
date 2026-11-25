"""CLI entry — stage 3 (BFS dependency graph)."""

import sys

from src.collector import (
    collect_direct_deps,
    collect_graph,
    print_deps,
    print_graph,
)
from src.config import load_config, print_config, success_code
from src.stdio import enable_stdio


def main(argv=None):
    """Stage 3 by default; flags for stage 1–2."""
    enable_stdio()
    args = load_config(argv)
    if args.print_config:
        print_config(args)
        return success_code()
    if args.direct_only:
        deps = collect_direct_deps(args)
        print_deps(deps, args.package)
        return success_code()
    adjacency, edges, cycle = collect_graph(args)
    print_graph(adjacency, edges, args.package, cycle)
    return success_code()


if __name__ == "__main__":
    sys.exit(main())