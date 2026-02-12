import sys
from src.parsing.read_file import ReadFile, MapError
from src.algorithm.fly_in_algorithm import FlyInAlgorithm
from src.simulation.engine import SimulationEngine


def main() -> None:
    if len(sys.argv) != 2:
        print("Input error", file=sys.stderr)
        sys.exit(1)
    try:
        data = ReadFile(sys.argv[1]).get_fly_in_data()
    except MapError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    alg = FlyInAlgorithm()
    alg.load_data(data)
    alg.route_optimization()

    engine = SimulationEngine(data, alg.paths)
    engine.run_simulation()


if __name__ == "__main__":
    main()
