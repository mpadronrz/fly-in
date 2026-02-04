import sys
from src.parsing.read_file import ReadFile, MapError
from rich import print as rprint


def main() -> None:
    if len(sys.argv) != 2:
        print("Input error", file=sys.stderr)
        sys.exit(1)
    try:
        data = ReadFile(sys.argv[1]).get_fly_in_data()
        rprint((vars(data)))
    except MapError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
