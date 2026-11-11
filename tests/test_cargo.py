"""Тесты разбора ответа crates.io."""

import json
import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, ROOT)

from src.cargo import (
    build_crate_url,
    build_deps_url,
    fetch_cargo_deps,
    parse_direct_deps,
    read_stable_version,
)


def _read(name):
    """Читает текст фикстуры."""
    path = os.path.join(ROOT, "fixtures", name)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _load(name):
    """Читает JSON-фикстуру."""
    return json.loads(_read(name))


class TestCargo(unittest.TestCase):
    """Проверка URL и разбора зависимостей."""

    def test_build_urls(self):
        """URL crate и зависимостей собираются из базы."""
        repo = "https://crates.io/api/v1/"
        crate_url = build_crate_url(repo, "serde")
        deps_url = build_deps_url(
            repo,
            "serde",
            "1.0.229",
        )
        self.assertEqual(
            crate_url,
            "https://crates.io/api/v1/crates/serde",
        )
        self.assertEqual(
            build_crate_url(repo, "Serde"),
            crate_url,
        )
        self.assertEqual(
            deps_url,
            "https://crates.io/api/v1/crates/"
            "serde/1.0.229/dependencies",
        )

    def test_parse_keeps_normal_only(self):
        """Optional, dev и build не попадают в список."""
        deps = parse_direct_deps(_load("sample_deps.json"))
        self.assertEqual(
            deps,
            [
                ("serde_core", "=1.0.229"),
                ("libc", "^0.2"),
            ],
        )

    def test_parse_empty(self):
        """Пустой список зависимостей допустим."""
        deps = parse_direct_deps({"dependencies": []})
        self.assertEqual(deps, [])

    def test_parse_missing_field(self):
        """Нет поля dependencies — ошибка."""
        with self.assertRaises(ValueError):
            parse_direct_deps({})

    def test_stable_version(self):
        """Берётся max_stable_version."""
        data = _load("sample_crate.json")
        version = read_stable_version(data)
        self.assertEqual(version, "1.0.229")

    def test_version_fallback(self):
        """Если stable нет, берётся max_version."""
        data = _load("fallback_crate.json")
        version = read_stable_version(data)
        self.assertEqual(version, "0.4.35")

    def test_version_missing(self):
        """Без версии — ошибка."""
        with self.assertRaises(ValueError):
            read_stable_version({"crate": {}})

    def test_fetch_cargo_deps(self):
        """Загрузка склеивает версию и список зависимостей."""
        crate = _read("sample_crate.json")
        deps = _read("sample_deps.json")
        with mock.patch(
            "src.cargo.fetch_text",
            side_effect=[crate, deps],
        ) as mocked:
            found = fetch_cargo_deps(
                "https://crates.io/api/v1",
                "serde",
            )
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(
            found,
            [
                ("serde_core", "=1.0.229"),
                ("libc", "^0.2"),
            ],
        )

    def test_bad_json(self):
        """Некорректный JSON превращается в ValueError."""
        with mock.patch(
            "src.cargo.fetch_text",
            return_value="not-json",
        ):
            with self.assertRaises(ValueError):
                fetch_cargo_deps(
                    "https://crates.io/api/v1",
                    "serde",
                )


if __name__ == "__main__":
    unittest.main()
