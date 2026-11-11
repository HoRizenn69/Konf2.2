"""Точка входа CLI — этап 2 (сбор данных)."""

import sys

from src.collector import collect_direct_deps, print_deps
from src.config import load_config, success_code
from src.stdio import enable_stdio


def main(argv=None):
    """Читает CLI, собирает и печатает прямые зависимости."""
    enable_stdio()
    args = load_config(argv)
    deps = collect_direct_deps(args)
    print_deps(deps, args.package)
    return success_code()


if __name__ == "__main__":
    sys.exit(main())
