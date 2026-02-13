from src.models import FlyInData, Drone, Path, ZoneType, Color
from src.gui.graphics_engine import GraphicsEngine


class SimulationEngine:
    """
    The core engine responsible for executing the drone routing simulation.

    This class manages the lifecycle of the simulation, including drone
    initialization, path assignment, turn-by-turn state updates, and
    synchronization with the graphical interface.

    Attributes:
        data (FlyInData): Parsed map data including hub definitions and
            constraints.
        drones (list[Drone]): List of all drone objects active in the fleet.
        paths (list[Path]): Disjoint or overlapping paths optimized for
            routing.
        graphics (GraphicsEngine): The visual representation system for the
            simulation.
        graphics_on (bool): Flag to check if graphical output is on.
    """
    def __init__(self, data: FlyInData, paths: list[Path]) -> None:
        """
        Initializes the simulation engine with map data and calculated paths.

        Args:
            data (FlyInData): The object containing all parsed network
                information.
            paths (list[Path]): The calculated optimal paths for the drone
                fleet.
        """
        self.data = data
        self.drones = [Drone(i) for i in range(1, data.nb_drones + 1)]
        self.paths = paths
        self.add_drones_to_paths()
        self.graphics = GraphicsEngine(data, self.drones)
        self.graphics_on = True

    def add_drones_to_paths(self) -> None:
        """
        Distributes the initialized drones across the assigned optimal paths.

        This method partitions the fleet based on the capacity and cost
        analysis of each path to ensure maximum throughput.
        """
        drone_index = 0
        for path in self.paths:
            path.drones = self.drones[
                drone_index: drone_index + path.nb_drones
            ]
            drone_index += path.nb_drones

    def simulate_turn(self) -> tuple[str, list[Drone]]:
        """
        Executes a single discrete simulation turn.

        Processes movement for every drone, handles restricted zone costs
        (2 turns), updates rendering coordinates, and generates the
        mandatory log string.

        Returns:
            tuple[str, list[Drone]]: A tuple containing:
                - The formatted turn log string to print.
                - A list of Drone objects that changed position during
                    this turn.
        """
        log: list[str] = []
        moving_drones: list[Drone] = []
        for path in self.paths:
            path_length = len(path.vertices)
            for drone in path.drones:
                if drone.finished:
                    continue
                previous_index = drone.hub_index
                hub1 = self.data.hubs[path.vertices[previous_index]]
                if drone.waiting:
                    drone.waiting = False
                    log.append(
                        f"{hub1.color_data.ansi}D{drone.id}-"
                        f"{hub1.name}{Color.DEFAULT.ansi}"
                    )
                    drone.target_coords = hub1.graphic_coords
                    moving_drones.append(drone)
                    continue
                drone.hub_index += 1
                hub2 = self.data.hubs[path.vertices[drone.hub_index]]
                if (
                    self.data.hubs[path.vertices[drone.hub_index]].zone
                    == ZoneType.RESTRICTED
                ):
                    drone.waiting = True
                    log.append(
                        f"D{drone.id}-{hub1.color_data.ansi}{hub1.name}"
                        f"{Color.DEFAULT.ansi}-{hub2.color_data.ansi}"
                        f"{hub2.name}{Color.DEFAULT.ansi}"
                    )
                    drone.target_coords = (
                        (hub1.graphic_coords[0] + hub2.graphic_coords[0]) // 2,
                        (hub1.graphic_coords[1] + hub2.graphic_coords[1]) // 2,
                    )
                    moving_drones.append(drone)
                    if previous_index == 0:
                        break
                    continue
                log.append(
                    f"{hub2.color_data.ansi}D{drone.id}-"
                    f"{hub2.name}{Color.DEFAULT.ansi}"
                )
                drone.target_coords = hub2.graphic_coords
                moving_drones.append(drone)
                if drone.hub_index + 1 == path_length:
                    drone.finished = True
                if previous_index == 0:
                    break
        return " ".join(log), moving_drones

    def run_simulation(self) -> None:
        """
        The main simulation loop that executes turns until all drones arrive.

        Outputs the step-by-step movement to the terminal and updates
        the graphical interface until the simulation end condition is met.
        """
        while True:
            log, drones = self.simulate_turn()
            if log == "":
                return
            print(log)
            if self.graphics_on:
                self.graphics_on = self.graphics.simulate_turn(drones)
