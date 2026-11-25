"""Demo for stages 4–5: load order and PlantUML/SVG."""

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
    """Run one CLI scenario and print its output."""
    print(f"=== {title} ===")
    env = _child_env()
    cmd = [sys.executable, "-m", "src.main", *args]
    result = _run_child(cmd, env)
    _print_result(result)
    print()


def _print_result(result):
    """Print stdout and stderr of a child process."""
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    if result.stdout or result.stderr:
        return
    print("(no output)")


def run_unit_tests():
    """Run unittest and print the result."""
    print("=== Unit tests ===")
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
    """Run process; decode with console encoding."""
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
    """Child env with PYTHONPATH and IO encoding."""
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT
    env["PYTHONIOENCODING"] = output_encoding()
    env.pop("PYTHONUTF8", None)
    return env


def _banner():
    """Print runtime environment."""
    print(f"Working dir: {ROOT}")
    print(f"Python: {sys.executable}")
    print()


def _sources_ok():
    """True if main.py exists."""
    main_py = os.path.join(ROOT, "src", "main.py")
    if os.path.isfile(main_py):
        return True
    print(f"ERROR: missing file {main_py}")
    _pause()
    return False


def _test_repo_cases():
    """Stage 4 and 5 on local test files."""
    run_case(
        "TEST: simple A (PlantUML/SVG)",
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
        "TEST: simple A (load-order)",
        [
            "--package",
            "A",
            "--repo",
            "fixtures/repo_simple.txt",
            "--output",
            "order.svg",
            "--test-mode",
            "--load-order",
        ],
    )
    run_case(
        "TEST: cycle",
        [
            "--package",
            "A",
            "--repo",
            "fixtures/repo_cycle.txt",
            "--output",
            "cycle.svg",
            "--test-mode",
        ],
    )
    run_case(
        "TEST: filter XX (load-order)",
        [
            "--package",
            "A",
            "--repo",
            "fixtures/repo_filter.txt",
            "--output",
            "filter.svg",
            "--test-mode",
            "--filter",
            "XX",
            "--load-order",
        ],
    )


def _cargo_case():
    """One small crate from crates.io."""
    run_case(
        "TEST: crates.io cfg-if",
        [
            "--package",
            "cfg-if",
            "--repo",
            CRATES,
            "--output",
            OUT,
        ],
    )


def _has_packages():
    """True if package names were passed to demo."""
    return bool(sys.argv[1:])


def _show_packages(names):
    """Build graph for each package name from argv."""
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
    """Entry point for stage 5 demo."""
    enable_stdio()
    if _has_packages():
        return _show_packages(sys.argv[1:])
    _banner()
    if not _sources_ok():
        return EXIT_ERROR
    _test_repo_cases()
    _cargo_case()
    run_unit_tests()
    print("=== DONE ===")
    _pause()
    return EXIT_OK


def _pause():
    """Wait for Enter so cmd window stays open."""
    try:
        input("Press Enter to close...")
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