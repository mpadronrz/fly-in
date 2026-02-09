from src.models import FlyInData, Drone, Path, ZoneType


class SimulationEngine:
    def __init__(self, data: FlyInData, paths: list[Path]) -> None:
        self.data = data
        self.drones = [Drone(i) for i in range(1, data.nb_drones + 1)]
        self.paths = paths
        self.add_drones_to_paths()

    def add_drones_to_paths(self) -> None:
        drone_index = 0
        for path in self.paths:
            path.drones = self.drones[
                drone_index: drone_index + path.nb_drones
            ]
            drone_index += path.nb_drones

    def simulate_turn(self) -> str:
        log: list[str] = []
        for path in self.paths:
            path_length = len(path.vertices)
            for drone in path.drones:
                if drone.finished:
                    continue
                previous_index = drone.hub_index
                if drone.waiting:
                    drone.waiting = False
                    log.append(f"D{drone.id}-{path.vertices[drone.hub_index]}")
                    continue
                drone.hub_index += 1
                if (
                    self.data.hubs[path.vertices[drone.hub_index]].zone
                    == ZoneType.RESTRICTED
                ):
                    drone.waiting = True
                    log.append(
                        f"D{drone.id}-{path.vertices[previous_index]}"
                        f"-{path.vertices[drone.hub_index]}"
                    )
                    if previous_index == 0:
                        break
                    continue
                log.append(f"D{drone.id}-{path.vertices[drone.hub_index]}")
                if drone.hub_index + 1 == path_length:
                    drone.finished = True
                if previous_index == 0:
                    break
        return " ".join(log)

    def run_simulation(self) -> None:
        while (log := self.simulate_turn()) != "":
            print(log)
