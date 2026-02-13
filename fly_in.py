import sys
try:
    from src.parsing.read_file import ReadFile, MapError
    from src.algorithm.fly_in_algorithm import FlyInAlgorithm
    from src.simulation.engine import SimulationEngine
except ImportError as e:
    print(f"Error importing module: {e}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        print("Error: Missing map file parameter.", file=sys.stderr)
        print("Usage: python3 fly_in.py <map_file.txt>", file=sys.stderr)
        sys.exit(1)
    try:
        data = ReadFile(sys.argv[1]).get_fly_in_data()
    except MapError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    alg = FlyInAlgorithm()
    alg.load_data(data)
    alg.route_optimization()
    if not alg.paths:
        print(
            "No paths between start_hub and end_hub exist"
        )
        sys.exit(0)

    engine = SimulationEngine(data, alg.paths)
    engine.run_simulation()


if __name__ == "__main__":
    main()
