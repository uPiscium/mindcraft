import sys

from .runner import run_from_cli_args


def main():
    run_from_cli_args(sys.argv[1:])


if __name__ == "__main__":
    main()
