"""Сбор прямых зависимостей пакета Cargo."""

import sys

from src.cargo import fetch_cargo_deps
from src.constants import EMPTY_COUNT, EXIT_ERROR


def collect_direct_deps(args):
    """Возвращает прямые зависимости по параметрам CLI."""
    if args.test_mode:
        return _from_test_repo(args.repo, args.package)
    return _from_cargo(args.repo, args.package)


def print_deps(deps, package=""):
    """Печатает прямые зависимости пакета на экран."""
    _print_header(package)
    if len(deps) == EMPTY_COUNT:
        print("(нет)")
    else:
        for name, req in deps:
            _print_one_dep(name, req)
    print("==========================")


def _print_header(package):
    """Печатает заголовок, при имени — для этого пакета."""
    if len(package) == EMPTY_COUNT:
        print("=== Прямые зависимости ===")
        return
    print(f"=== Прямые зависимости: {package} ===")


def _print_one_dep(name, req):
    """Печатает одну зависимость в удобном виде."""
    if len(req) == EMPTY_COUNT:
        print(name)
    else:
        print(f"{name} {req}")


def _from_cargo(repo, package):
    """Загружает прямые зависимости из репозитория."""
    try:
        return fetch_cargo_deps(repo, package)
    except ValueError as err:
        _fail(str(err))


def _from_test_repo(path, package):
    """Читает прямые зависимости из тестового файла."""
    graph = _load_test_graph(path)
    key = package.strip().upper()
    if key not in graph:
        _fail(
            f"пакет {package} отсутствует "
            "в тестовом репозитории"
        )
    names = graph[key]
    return [(name, "") for name in names]


def _load_test_graph(path):
    """Загружает граф вида 'A: B C' из текстового файла."""
    graph = {}
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            _add_test_line(graph, raw)
    return graph


def _add_test_line(graph, raw):
    """Добавляет одну строку тестового репозитория."""
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


def _fail(message):
    """Печатает ошибку и завершает процесс."""
    print(f"Ошибка: {message}", file=sys.stderr)
    sys.exit(EXIT_ERROR)
