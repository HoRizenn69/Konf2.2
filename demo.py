"""Демонстрация этапа 2: ошибки и прямые зависимости."""

import os
import subprocess
import sys

from src.constants import EXIT_ERROR, EXIT_OK
from src.main import main as run_cli
from src.stdio import enable_stdio, output_encoding

ROOT = os.path.dirname(os.path.abspath(__file__))
CRATES = "https://crates.io/api/v1"
OUT = "graph.svg"


def run_case(title, args):
    """Запускает один сценарий и печатает его вывод."""
    print(f"=== {title} ===")
    env = _child_env()
    cmd = [sys.executable, "-m", "src.main", *args]
    result = _run_child(cmd, env)
    _print_result(result)
    print()


def _print_result(result):
    """Печатает stdout и stderr сценария."""
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    if result.stdout or result.stderr:
        return
    print("(нет вывода)")


def run_unit_tests():
    """Запускает unittest и печатает результат."""
    print("=== Юнит-тесты ===")
    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v",
    ]
    result = _run_child(cmd, _child_env())
    _print_result(result)
    print()


def _run_child(cmd, env):
    """Запускает процесс и читает вывод в кодировке консоли."""
    encoding = output_encoding()
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        encoding=encoding,
        errors="replace",
        capture_output=True,
    )


def _child_env():
    """Окружение дочернего процесса в кодировке консоли."""
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT
    env["PYTHONIOENCODING"] = output_encoding()
    env.pop("PYTHONUTF8", None)
    return env


def _banner():
    """Печатает окружение запуска."""
    print(f"Working dir: {ROOT}")
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    print()


def _sources_ok():
    """Проверяет, что точка входа на месте."""
    main_py = os.path.join(ROOT, "src", "main.py")
    if os.path.isfile(main_py):
        return True
    print(f"ERROR: нет файла {main_py}")
    print("Скопируйте папку проекта целиком.")
    _pause()
    return False


def _error_cases():
    """Сценарии с пустыми обязательными параметрами."""
    run_case(
        "ТЕСТ 1: нет --package",
        ["--repo", CRATES, "--output", OUT],
    )
    run_case(
        "ТЕСТ 2: нет --repo",
        ["--package", "serde", "--output", OUT],
    )
    run_case(
        "ТЕСТ 3: нет --output",
        ["--package", "serde", "--repo", CRATES],
    )


def _path_error_cases():
    """Сценарии с неверным путём и расширением."""
    run_case(
        "ТЕСТ 4: неверное расширение",
        _serde_args("--output", "x.txt"),
    )
    run_case(
        "ТЕСТ 5: путь без --test-mode",
        [
            "--package",
            "serde",
            "--repo",
            "fixtures/repo_simple.txt",
            "--output",
            OUT,
        ],
    )
    run_case(
        "ТЕСТ 6: нет файла test-mode",
        [
            "--package",
            "A",
            "--repo",
            "missing.txt",
            "--output",
            OUT,
            "--test-mode",
        ],
    )


def _success_cases():
    """Успешные сценарии этапа 2."""
    run_case(
        "ТЕСТ 7: тестовый репозиторий",
        [
            "--package",
            "A",
            "--repo",
            "fixtures/repo_simple.txt",
            "--output",
            "out.svg",
            "--test-mode",
        ],
    )
    run_case(
        "ТЕСТ 8: crates.io serde",
        _serde_args("--filter", "syn"),
    )


def _serde_args(*extra):
    """Базовые аргументы запроса пакета serde."""
    base = [
        "--package",
        "serde",
        "--repo",
        CRATES,
        "--output",
        OUT,
    ]
    return base + list(extra)


def _has_packages():
    """True, если при запуске передали имена пакетов."""
    return bool(sys.argv[1:])


def _show_packages(names):
    """Печатает зависимости каждого переданного пакета."""
    for name in names:
        run_cli(
            [
                "--package",
                name,
                "--repo",
                CRATES,
                "--output",
                OUT,
            ]
        )
    _pause()
    return EXIT_OK


def main():
    """Точка входа демо этапа 2."""
    enable_stdio()
    if _has_packages():
        return _show_packages(sys.argv[1:])
    _banner()
    if not _sources_ok():
        return EXIT_ERROR
    _error_cases()
    _path_error_cases()
    _success_cases()
    run_unit_tests()
    print("=== ГОТОВО ===")
    _pause()
    return EXIT_OK


def _pause():
    """Ждёт Enter, чтобы окно cmd не закрылось сразу."""
    try:
        input("Нажмите Enter, чтобы закрыть...")
    except (EOFError, UnicodeError, OSError):
        return


if __name__ == "__main__":
    try:
        code = main()
    except Exception as err:
        print(f"ERROR: {err}")
        _pause()
        code = EXIT_ERROR
    sys.exit(code)
