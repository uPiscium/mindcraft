import sys

from mindcraft_py.runner import run_from_cli_args
from mindcraft_py.terminal_logging import setup_terminal_logging


def main():
    with setup_terminal_logging():
        run_from_cli_args(sys.argv[1:])


if __name__ == "__main__":
    main()
