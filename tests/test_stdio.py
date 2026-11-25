"""Тесты выбора кодировки консоли."""

import os
import sys
import unittest

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, ROOT)

from src.stdio import _io_name, output_encoding


class TestStdio(unittest.TestCase):
    """Проверка имени кодировки и значения по умолчанию."""

    def test_io_name_strips_errors(self):
        """Суффикс :errors отбрасывается."""
        self.assertEqual(_io_name("cp866:replace"), "cp866")

    def test_io_name_empty(self):
        """Пустое значение заменяется на utf-8."""
        self.assertEqual(_io_name("   "), "utf-8")

    def test_output_encoding_posix(self):
        """Вне Windows без переменной окружения — utf-8."""
        if sys.platform == "win32":
            return
        old = os.environ.pop("PYTHONIOENCODING", None)
        try:
            self.assertEqual(output_encoding(), "utf-8")
        finally:
            if old is not None:
                os.environ["PYTHONIOENCODING"] = old


if __name__ == "__main__":
    unittest.main()
