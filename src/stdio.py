"""Кодировка консоли: UTF-8 на macOS, OEM-страница на Windows."""

import locale
import os
import sys

from src.constants import EMPTY_COUNT


def enable_stdio():
    """Настраивает stdout и stderr под текущую консоль."""
    encoding = output_encoding()
    _reconfigure(sys.stdout, encoding)
    _reconfigure(sys.stderr, encoding)


def output_encoding():
    """Кодировка печати: UTF-8 либо страница консоли Windows."""
    forced = os.environ.get("PYTHONIOENCODING", "")
    if len(forced.strip()) != EMPTY_COUNT:
        return _io_name(forced)
    if sys.platform != "win32":
        return "utf-8"
    if not _is_console(sys.stdout):
        return "utf-8"
    code = _console_code_page()
    if code == EMPTY_COUNT:
        return _preferred_encoding()
    return "cp" + str(code)


def _io_name(value):
    """Имя кодировки из PYTHONIOENCODING без суффикса errors."""
    name = value.split(":", 1)[0].strip()
    if len(name) == EMPTY_COUNT:
        return "utf-8"
    return name


def _reconfigure(stream, encoding):
    """Ставит кодировку и не падает на незнакомых символах."""
    if stream is None:
        return
    method = getattr(stream, "reconfigure", None)
    if method is None:
        return
    try:
        method(encoding=encoding, errors="replace")
    except (OSError, ValueError, LookupError):
        _errors_only(stream)


def _errors_only(stream):
    """Оставляет кодировку потока, но глушит ошибку печати."""
    method = getattr(stream, "reconfigure", None)
    if method is None:
        return
    try:
        method(errors="replace")
    except (OSError, ValueError, LookupError):
        return


def _is_console(stream):
    """True, если поток прикреплён к консоли."""
    isatty = getattr(stream, "isatty", None)
    if isatty is None:
        return False
    try:
        return bool(isatty())
    except (OSError, ValueError):
        return False


def _console_code_page():
    """Кодовая страница вывода консоли Windows или 0."""
    try:
        import ctypes
        return int(ctypes.windll.kernel32.GetConsoleOutputCP())
    except (OSError, AttributeError, ValueError):
        return EMPTY_COUNT


def _preferred_encoding():
    """ANSI-кодировка Windows, если страницу консоли не прочитать."""
    encoding = locale.getpreferredencoding(False)
    if not encoding:
        return "utf-8"
    return encoding
