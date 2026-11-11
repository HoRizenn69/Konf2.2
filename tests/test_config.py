"""Тесты разбора и валидации конфигурации."""

import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, ROOT)

from src.config import (
    build_parser,
    print_config,
    validate_config,
)


def _parse(argv):
    """Разбирает argv без валидации."""
    parser = build_parser()
    return parser.parse_args(argv)


class TestConfig(unittest.TestCase):
    """Проверка параметров CLI этапа 1."""

    def test_parser_defaults(self):
        """Флаг test-mode по умолчанию выключен."""
        args = _parse(
            [
                "--package",
                "serde",
                "--repo",
                "https://crates.io/api/v1",
                "--output",
                "graph.svg",
            ]
        )
        self.assertFalse(args.test_mode)
        self.assertEqual(args.filter, "")

    def test_missing_package_exits(self):
        """Ошибка при отсутствии --package."""
        args = _parse(
            [
                "--repo",
                "https://crates.io/api/v1",
                "--output",
                "graph.svg",
            ]
        )
        with self.assertRaises(SystemExit):
            validate_config(args)

    def test_missing_repo_exits(self):
        """Ошибка при отсутствии --repo."""
        args = _parse(
            [
                "--package",
                "serde",
                "--output",
                "graph.svg",
            ]
        )
        with self.assertRaises(SystemExit):
            validate_config(args)

    def test_missing_output_exits(self):
        """Ошибка при отсутствии --output."""
        args = _parse(
            [
                "--package",
                "serde",
                "--repo",
                "https://crates.io/api/v1",
            ]
        )
        with self.assertRaises(SystemExit):
            validate_config(args)

    def test_bad_output_extension(self):
        """Ошибка при неверном расширении --output."""
        args = _parse(
            [
                "--package",
                "serde",
                "--repo",
                "https://crates.io/api/v1",
                "--output",
                "graph.txt",
            ]
        )
        with self.assertRaises(SystemExit):
            validate_config(args)

    def test_output_with_directory_exits(self):
        """Ошибка, если в --output указан каталог."""
        args = _parse(
            [
                "--package",
                "serde",
                "--repo",
                "https://crates.io/api/v1",
                "--output",
                "dir/graph.svg",
            ]
        )
        with self.assertRaises(SystemExit):
            validate_config(args)

    def test_png_output_ok(self):
        """Расширение .png допустимо."""
        args = _parse(
            [
                "--package",
                "serde",
                "--repo",
                "https://crates.io/api/v1",
                "--output",
                "graph.png",
            ]
        )
        validate_config(args)
        self.assertEqual(args.output, "graph.png")

    def test_invalid_url_exits(self):
        """Ошибка при пути без --test-mode."""
        args = _parse(
            [
                "--package",
                "serde",
                "--repo",
                "not-a-url",
                "--output",
                "graph.svg",
            ]
        )
        with self.assertRaises(SystemExit):
            validate_config(args)

    def test_test_mode_requires_file(self):
        """Ошибка, если тестовый файл не существует."""
        args = _parse(
            [
                "--package",
                "A",
                "--repo",
                "/no/such/file.txt",
                "--output",
                "graph.svg",
                "--test-mode",
            ]
        )
        with self.assertRaises(SystemExit):
            validate_config(args)

    def test_test_mode_rejects_lowercase(self):
        """В test-mode имя пакета только из заглавных."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
        ) as handle:
            handle.write("A: B\n")
            path = handle.name
        try:
            args = _parse(
                [
                    "--package",
                    "serde",
                    "--repo",
                    path,
                    "--output",
                    "out.svg",
                    "--test-mode",
                ]
            )
            with self.assertRaises(SystemExit):
                validate_config(args)
        finally:
            os.unlink(path)

    def test_test_mode_rejects_non_latin(self):
        """В test-mode нельзя цифры и не латинские буквы."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
        ) as handle:
            handle.write("A: B\n")
            path = handle.name
        try:
            args = _parse(
                [
                    "--package",
                    "A1",
                    "--repo",
                    path,
                    "--output",
                    "out.svg",
                    "--test-mode",
                ]
            )
            with self.assertRaises(SystemExit):
                validate_config(args)
        finally:
            os.unlink(path)

    def test_test_mode_ok(self):
        """Успешная валидация test-mode."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
        ) as handle:
            handle.write("A: B\nB:\n")
            path = handle.name
        try:
            args = _parse(
                [
                    "--package",
                    "A",
                    "--repo",
                    path,
                    "--output",
                    "out.svg",
                    "--test-mode",
                    "--filter",
                    "XX",
                ]
            )
            validate_config(args)
            self.assertEqual(args.package, "A")
            self.assertEqual(args.filter, "XX")
            self.assertTrue(args.test_mode)
        finally:
            os.unlink(path)

    def test_print_config(self):
        """Печать ключ-значение не падает."""
        args = _parse(
            [
                "--package",
                "serde",
                "--repo",
                "https://crates.io/api/v1",
                "--output",
                "graph.svg",
            ]
        )
        validate_config(args)
        with mock.patch("builtins.print") as mocked:
            print_config(args)
            self.assertTrue(mocked.called)


if __name__ == "__main__":
    unittest.main()
