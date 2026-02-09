from typing import Optional
from src.models.drone_model import Drone


class Vertex:
    """
    Represents a hub in the flight network.

    Attributes:
        name (str): The unique identifier of the hub.
        flow (int): Current number of drones occupying or passing
            through the hub.
        max_flow (int): The maximum drone capacity of the hub (max_drones).
        priority (bool): True if the hub is a priority zone.
    """
    def __init__(self, name: str, max_flow: int) -> None:
        """Initializes a Vertex with a name and its maximum drone capacity."""
        self.name = name
        self.flow = 0
        self.max_flow = max_flow
        self.priority = False


class Edge:
    """
    Represents a directed connection between two hubs.

    Attributes:
        source (str): Starting hub name.
        target (str): Destination hub name.
        length (int): Turn cost to traverse (1 for normal/priority,
            2 for restricted).
        flow (int): Number of drones currently assigned to this connection.
        max_flow (int): Maximum link capacity.
        reverse_edge (Edge): The corresponding edge in the opposite direction.
        paths (list[Path]): List of active paths utilizing this specific edge.
    """
    def __init__(
        self, source: str, target: str, length: int, max_flow: int
    ) -> None:
        """Initializes an Edge with capacity and movement cost."""
        self.source = source
        self.target = target
        self.length = length
        self.flow = 0
        self.max_flow = max_flow
        self.reverse_edge: Optional["Edge"] = None
        self.paths: list["Path"] = []


class Path:
    """
    Represents a sequence of hubs forming a route from start to end.

    Attributes:
        vertices (list[str]): Ordered list of hub names in the path.
        cost (int): Total turn cost to traverse the path.
        priority (int): Count of priority hubs included in the path.
        nb_drones (int): Number of drones assigned to follow this path.
    """
    def __init__(self, vertices: list[str], cost: int, priority: int) -> None:
        """Initializes a Path with its route, cost, and priority score."""
        self.vertices = vertices
        self.cost = cost
        self.priority = priority
        self.nb_drones = 0
        self.drones: list[Drone] = []
