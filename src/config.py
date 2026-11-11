"""Разбор и проверка параметров командной строки."""

import argparse
import os
import sys

from src.constants import EMPTY_COUNT, EXIT_ERROR, EXIT_OK


def build_parser():
    """Создаёт парсер опций CLI для варианта 16."""
    parser = argparse.ArgumentParser(
        description=(
            "Визуализация графа зависимостей Cargo"
        ),
    )
    _add_core_args(parser)
    _add_mode_args(parser)
    return parser


def _add_core_args(parser):
    """Добавляет основные параметры пакета и вывода."""
    parser.add_argument(
        "--package",
        help="Имя анализируемого пакета",
    )
    parser.add_argument(
        "--repo",
        help=(
            "URL репозитория или путь к тестовому файлу"
        ),
    )
    parser.add_argument(
        "--output",
        help="Имя файла с изображением графа",
    )
    parser.add_argument(
        "--filter",
        default="",
        help="Подстрока для фильтрации пакетов",
    )


def _add_mode_args(parser):
    """Добавляет флаг тестового режима."""
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Режим работы с тестовым репозиторием",
    )


def _fail(message):
    """Печатает ошибку и завершает процесс."""
    print(f"Ошибка: {message}", file=sys.stderr)
    sys.exit(EXIT_ERROR)


def validate_config(args):
    """Проверяет все настраиваемые параметры."""
    if not args.package:
        _fail("не задан параметр --package")
    if not args.repo:
        _fail("не задан параметр --repo")
    if not args.output:
        _fail("не задан параметр --output")

    package = args.package.strip()
    repo = args.repo.strip()
    output = args.output.strip()
    filt = args.filter if args.filter else ""

    if not package:
        _fail("имя пакета не может быть пустым")
    if not repo:
        _fail("URL или путь репозитория пуст")
    if not output:
        _fail("имя файла вывода не может быть пустым")
    _validate_output_name(output)

    if args.test_mode:
        _validate_test_repo(repo, package)
    else:
        _validate_url(repo)

    args.package = package
    args.repo = repo
    args.output = output
    args.filter = filt
    return args


def _validate_output_name(output):
    """Проверяет имя файла изображения графа."""
    if os.path.sep in output or (
        os.path.altsep and os.path.altsep in output
    ):
        _fail(
            "в --output укажите имя файла без каталогов"
        )
    if not output.lower().endswith((".svg", ".png")):
        _fail(
            "файл вывода должен иметь расширение "
            ".svg или .png"
        )


def _validate_test_repo(path, package):
    """Проверяет путь к файлу тестового репозитория."""
    if not os.path.isfile(path):
        _fail(f"тестовый репозиторий не найден: {path}")
    if not _is_latin_name(package):
        _fail(
            "в test-mode имя пакета — "
            "заглавные латинские буквы"
        )


def _is_latin_name(package):
    """True, если имя состоит только из букв A–Z."""
    if len(package) == EMPTY_COUNT:
        return False
    for char in package:
        if not _is_latin_upper(char):
            return False
    return True


def _is_latin_upper(char):
    """True для одной буквы от A до Z."""
    if char < "A":
        return False
    return char <= "Z"


def _validate_url(repo):
    """Проверяет, что repo похож на URL репозитория."""
    lower = repo.lower()
    has_http = lower.startswith("http://")
    has_https = lower.startswith("https://")
    if not has_http and not has_https:
        _fail(
            "ожидался URL (http/https) "
            "или включите --test-mode"
        )


def print_config(args):
    """Выводит параметры в формате ключ-значение."""
    print("=== Параметры конфигурации ===")
    print(f"package={args.package}")
    print(f"repo={args.repo}")
    print(f"test_mode={args.test_mode}")
    print(f"output={args.output}")
    print(f"filter={args.filter}")
    print("================================")


def load_config(argv=None):
    """Разбирает argv, валидирует и возвращает args."""
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_config(args)
    return args


def success_code():
    """Возвращает код успешного завершения."""
    return EXIT_OK
