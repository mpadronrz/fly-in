from src.parsing.data_structures import (
    FlyInData,
    ZoneType,
)
from typing import Optional


class Vertex:
    def __init__(self, name: str, max_flow: int) -> None:
        self.name = name
        self.flow = 0
        self.max_flow = max_flow
        self.priority = False


class Edge:
    def __init__(
        self, source: str, target: str, length: int, max_flow: int
    ) -> None:
        self.source = source
        self.target = target
        self.length = length
        self.flow = 0
        self.max_flow = max_flow
        self.reverse_edge: Optional["Edge"] = None


class FlyInAlgorithm:
    def __init__(self) -> None:
        self.start = ""
        self.end = ""
        self.vertices: dict[str, Vertex] = dict()
        self.adjacency: dict[str, set[str]] = dict()
        self.edges: dict[tuple[str, str], Edge] = dict()
        self.cost = 0
        self.nb_drones = 0

    def load_data(self, data: FlyInData) -> None:
        self.nb_drones = data.nb_drones
        self.start = data.start
        self.end = data.end

        for hub_name, hub in data.hubs.items():
            if hub.zone == ZoneType.BLOCKED:
                continue
            self.vertices[hub_name] = Vertex(hub_name, hub.max_drones)
            if hub.zone == ZoneType.PRIORITY:
                self.vertices[hub_name].priority = True
            self.adjacency[hub_name] = set()
        self.vertices[self.start].max_flow = self.nb_drones
        self.vertices[self.end].max_flow = self.nb_drones

        for connection in data.connections:
            hub1, hub2 = connection.hubs
            if hub1 not in self.vertices or hub2 not in self.vertices:
                continue

            edge1 = Edge(
                hub1,
                hub2,
                2 if data.hubs[hub2].zone == ZoneType.RESTRICTED else 1,
                connection.max_link_capacity,
            )
            edge2 = Edge(
                hub2,
                hub1,
                2 if data.hubs[hub1].zone == ZoneType.RESTRICTED else 1,
                connection.max_link_capacity,
            )
            edge1.reverse_edge = edge2
            edge2.reverse_edge = edge1

            self.adjacency[hub1].add(hub2)
            self.adjacency[hub2].add(hub1)
            self.edges[(hub1, hub2)] = edge1
            self.edges[(hub2, hub1)] = edge2

    def new_path_to_target(self) -> None:
        parent: dict[str, str] = dict()
        queue = [self.start]
        distances = {vertex: 0 for vertex in self.vertices}
        step = 1
        while len(queue) > 0:
            current = queue.pop()
            cost = distances[current]
            for vertex in self.adjacency[current]:
                pass
