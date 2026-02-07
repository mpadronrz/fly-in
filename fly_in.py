import sys
from src.parsing.read_file import ReadFile, MapError
from rich import print as rprint
from src.algorithm.fly_in_algorithm import FlyInAlgorithm


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

    print()
    print()
    print()
    print("ALGORITHM")
    print()
    alg = FlyInAlgorithm()
    alg.load_data(data)
    # rprint((vars(alg)))

    alg.route_optimization()
    for path in alg.paths:
        rprint(vars(path))


if __name__ == "__main__":
    main()
