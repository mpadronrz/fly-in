from src.models import FlyInData, Drone, Path, ZoneType, Color


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
                    continue
                drone.hub_index += 1
                if (
                    self.data.hubs[path.vertices[drone.hub_index]].zone
                    == ZoneType.RESTRICTED
                ):
                    drone.waiting = True
                    hub1 = path.vertices[previous_index]
                    hub2 = path.vertices[drone.hub_index]
                    log.append(
                        f"D{drone.id}-{self.data.hubs[hub1].color_data.ansi}{hub1}{Color.DEFAULT.ansi}"
                        f"-{self.data.hubs[hub2].color_data.ansi}{hub2}{Color.DEFAULT.ansi}"
                    )
                    if previous_index == 0:
                        break
                    continue
                hub = path.vertices[drone.hub_index]
                log.append(f"{self.data.hubs[hub].color_data.ansi}D{drone.id}-{hub}{Color.DEFAULT.ansi}")
                if drone.hub_index + 1 == path_length:
                    drone.finished = True
                if previous_index == 0:
                    break
        return " ".join(log)

    def run_simulation(self) -> None:
        while (log := self.simulate_turn()) != "":
            print(log)
