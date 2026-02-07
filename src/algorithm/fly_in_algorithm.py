from src.parsing.data_structures import (
    FlyInData,
    ZoneType,
)
from typing import Optional
from math import ceil


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


class Path:
    def __init__(self, vertices, cost, priority, cancelations):
        self.vertices: list[Vertex] = vertices
        self.cost = cost
        self.priority = priority
        self.nb_drones = 0
        self.cancelations = cancelations


class FlyInAlgorithm:
    def __init__(self) -> None:
        self.start = ""
        self.end = ""
        self.vertices: dict[str, Vertex] = dict()
        self.adjacency: dict[str, set[str]] = dict()
        self.edges: dict[tuple[str, str], Edge] = dict()
        self.cost = 0
        self.nb_drones = 0
        self.paths: list[Path] = []

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

    def is_connectable(self, source, target) -> bool:
        if self.edges[(source, target)].flow == self.edges[(source, target)].max_flow:
            return False
        if self.vertices[target].flow < self.vertices[target].max_flow:
            return True
        return self.edges[(target, source)].flow > 0

    def new_path_to_target(self) -> Optional[Path]:
        parent: dict[str, str] = dict()
        stack = [vertex for vertex in self.vertices]
        distances: dict[str, tuple[int | float, int]] = {vertex: (float('inf'), 0) for vertex in self.vertices}
        distances[self.start] = (0, 0)

        while len(stack) > 0:
            current = min(stack, key=lambda x: distances[x])
            stack.remove(current)
            if current == self.end:
                break
            current_dist, current_priority = distances[current]
            for neighbour in self.adjacency[current]:
                edge_length = self.edges[(current, neighbour)].length
                if distances[neighbour] > current_dist + edge_length and self.is_connectable(current, neighbour):
                    parent[neighbour] = current
                    if self.vertices[neighbour].priority:
                        current_priority -= 1
                    distances[neighbour] = (current_dist + edge_length, current_priority)

        if self.end in stack:
            return

        vertices = [self.end]
        current_vertex = self.end
        cancelations = 0
        while current_vertex != self.start:
            previous_vertex = parent[current_vertex]
            self.vertices[previous_vertex].flow += 1
            self.edges[(previous_vertex, current_vertex)].flow += 1
            if self.edges[(current_vertex, previous_vertex)].flow > 0:
                cancelations += 1
            vertices.insert(0, previous_vertex)
        return Path(vertices, distances[self.end][0], -distances[self.end][1], cancelations)

    def calculate_cost(self) -> int:
        if not self.paths:
            return 0
        return (
            ceil(
                (sum(path.cost for path in self.paths) + self.nb_drones)
                / len(self.paths)
            )
            + 1
        )

    def undo_cancelations(self, new_path: Path) -> None:
        while new_path.cancelations > 0:
            pass

    def get_candidate_paths(self):
        if (new_path := self.new_path_to_target()) is None:
            return
        self.paths.append(new_path)
        self.cost = new_path.cost + self.nb_drones - 1
        while len(self.paths) < self.nb_drones:
            if (new_path := self.new_path_to_target()) is None:
                return
            if new_path.cost - 2 * new_path.cancelations > self.cost:
                return
            if new_path.cancelations > 0:
                self.undo_cancelations(new_path)
            self.paths.append(new_path)
            self.cost = self.calculate_cost()

    def route_optimization(self):
        pass
