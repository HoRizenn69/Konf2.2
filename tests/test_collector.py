"""Тесты сборщика прямых зависимостей."""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, ROOT)

from src.collector import collect_direct_deps, print_deps
from src.config import build_parser, validate_config


def _load_args(argv):
    """Собирает и валидирует аргументы CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return validate_config(args)


class TestCollector(unittest.TestCase):
    """Проверка test-mode и вывода."""

    def test_test_mode_direct_deps(self):
        """Прямые зависимости из тестового файла."""
        path = os.path.join(
            ROOT,
            "fixtures",
            "repo_simple.txt",
        )
        args = _load_args(
            [
                "--package",
                "A",
                "--repo",
                path,
                "--output",
                "out.svg",
                "--test-mode",
            ]
        )
        deps = collect_direct_deps(args)
        self.assertEqual(deps, [("B", ""), ("C", "")])

    def test_test_mode_leaf(self):
        """Лист без зависимостей даёт пустой список."""
        path = os.path.join(
            ROOT,
            "fixtures",
            "repo_simple.txt",
        )
        args = _load_args(
            [
                "--package",
                "D",
                "--repo",
                path,
                "--output",
                "out.svg",
                "--test-mode",
            ]
        )
        deps = collect_direct_deps(args)
        self.assertEqual(deps, [])

    def test_filter_not_applied(self):
        """На этапе 2 фильтр ещё не отсекает пакеты."""
        path = os.path.join(
            ROOT,
            "fixtures",
            "repo_simple.txt",
        )
        args = _load_args(
            [
                "--package",
                "A",
                "--repo",
                path,
                "--output",
                "out.svg",
                "--test-mode",
                "--filter",
                "B",
            ]
        )
        deps = collect_direct_deps(args)
        self.assertEqual(deps, [("B", ""), ("C", "")])

    def test_unknown_package(self):
        """Неизвестный пакет в test-mode — ошибка."""
        path = os.path.join(
            ROOT,
            "fixtures",
            "repo_simple.txt",
        )
        args = _load_args(
            [
                "--package",
                "Z",
                "--repo",
                path,
                "--output",
                "out.svg",
                "--test-mode",
            ]
        )
        with self.assertRaises(SystemExit):
            collect_direct_deps(args)

    def test_cargo_mode_uses_fetch(self):
        """В обычном режиме вызывается загрузка Cargo."""
        args = _load_args(
            [
                "--package",
                "serde",
                "--repo",
                "https://crates.io/api/v1",
                "--output",
                "graph.svg",
            ]
        )
        found = [("serde_core", "=1.0.229")]
        with mock.patch(
            "src.collector.fetch_cargo_deps",
            return_value=found,
        ) as mocked:
            deps = collect_direct_deps(args)
        mocked.assert_called_once_with(
            "https://crates.io/api/v1",
            "serde",
        )
        self.assertEqual(deps, found)

    def test_print_deps(self):
        """Печать списка зависимостей не падает."""
        with mock.patch("builtins.print") as mocked:
            print_deps([("serde_core", "=1.0.229")])
            print_deps([])
            self.assertTrue(mocked.called)


if __name__ == "__main__":
    unittest.main()
