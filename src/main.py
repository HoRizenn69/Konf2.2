"""CLI entry — stage 5 default, stage 4 with --load-order."""

import sys

from src.collector import (
    collect_direct_deps,
    collect_graph,
    print_deps,
    print_load_order,
    save_graph_visualization,
)
from src.config import load_config, print_config, success_code
from src.graph import load_order
from src.stdio import enable_stdio


def main(argv=None):
    """Stages 1–2 via flags; 4 or 5 on graph."""
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
    root = _graph_root(args)
    if args.load_order:
        order = load_order(adjacency, root)
        print_load_order(order, args.package)
        return success_code()
    save_graph_visualization(
        adjacency,
        edges,
        root,
        args.output,
        cycle,
    )
    return success_code()


def _graph_root(args):
    """Root node id used in the built graph."""
    if args.test_mode:
        return args.package.strip().upper()
    return args.package


if __name__ == "__main__":
    sys.exit(main())