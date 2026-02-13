from src.models import (
    FlyInData, ZoneType, Vertex, Edge, Path
)
from typing import Optional
from math import ceil


class FlyInAlgorithm:
    """
    Core engine for pathfinding and drone route optimization.

    This class implements a Successive Shortest Path algorithm utilizing
    residual graphs to handle flow capacity and turn optimization.
    """
    def __init__(self) -> None:
        """Initializes the algorithm state and graph structures."""
        self.start = ""
        self.end = ""
        self.vertices: dict[str, Vertex] = dict()
        self.adjacency: dict[str, set[str]] = dict()
        self.edges: dict[tuple[str, str], Edge] = dict()
        self.cost = 0
        self.nb_drones = 0
        self.paths: list[Path] = []

    def load_data(self, data: FlyInData) -> None:
        """
        Parses input data and populates the internal graph representation.

        Args:
            data (FlyInData): The raw data parsed from the map file.
        """
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

    def is_connectable(
        self, source: str, target: str, free_node: dict[str, bool]
    ) -> bool:
        """
        Checks if flow can be pushed through an edge considering hub and
        link capacities.

        Args:
            source (str): Name of the source hub.
            target (str): Name of the target hub.
            free_node (dict): Tracks if a hub is eligible for entry via
                standard or residual flow.

        Returns:
            bool: True if the connection is valid under current constraints.
        """
        if (
            self.edges[(source, target)].flow
            == self.edges[(source, target)].max_flow
        ):
            return False
        if self.vertices[target].flow < self.vertices[target].max_flow:
            free_node[target] = True
            return True
        if self.edges[(target, source)].flow > 0:
            free_node[target] = True
            return True
        free_node[target] = False
        return True

    def new_path_to_target(self) -> Optional[Path]:
        """
        Finds the shortest augmenting path using a modified Dijkstra search.

        Returns:
            Optional[Path]: The discovered path, or None if no path exists.
        """
        parent: dict[str, str] = dict()
        stack = [vertex for vertex in self.vertices]
        distances: dict[str, tuple[int | float, int]] = {
            vertex: (float("inf"), 0) for vertex in self.vertices
        }
        distances[self.start] = (0, 0)
        free_node: dict[str, bool] = {
            vertex: True for vertex in self.vertices
        }

        while len(stack) > 0:
            current = min(stack, key=lambda x: distances[x])
            if distances[current][0] == float('inf'):
                return None
            stack.remove(current)
            if current == self.end:
                break
            current_dist, current_priority = distances[current]
            for neighbour in self.adjacency[current]:
                if neighbour not in stack:
                    continue
                if (
                    not free_node[current]
                    and self.edges[(neighbour, current)].flow == 0
                ):
                    continue
                if (
                    self.edges[(current, neighbour)].flow
                    < self.edges[(neighbour, current)].flow
                ):
                    edge_length = - self.edges[(neighbour, current)].length
                    new_priority = 0
                else:
                    edge_length = self.edges[(current, neighbour)].length
                    new_priority = (
                        -1 if self.vertices[neighbour].priority else 0
                    )
                if distances[neighbour] > (
                    current_dist + edge_length,
                    current_priority + new_priority,
                ) and self.is_connectable(current, neighbour, free_node):
                    parent[neighbour] = current
                    distances[neighbour] = (
                        current_dist + edge_length,
                        current_priority + new_priority,
                    )

        if self.end in stack:
            return None

        vertices = [self.end]
        current_vertex = self.end
        while current_vertex != self.start:
            previous_vertex = parent[current_vertex]
            self.vertices[previous_vertex].flow += 1
            if self.edges[(current_vertex, previous_vertex)].flow == 0:
                self.edges[(previous_vertex, current_vertex)].flow += 1
            vertices.insert(0, previous_vertex)
            current_vertex = previous_vertex
        return Path(
            vertices, int(distances[self.end][0]), -distances[self.end][1]
        )

    def calculate_cost(self) -> int:
        """
        Estimates the total turn count based on current paths using the
        L+n-1 formula.

        Returns:
            int: The calculated turn cost for the simulation.
        """
        if not self.paths:
            return 0
        return (
            ceil(
                (sum(path.cost for path in self.paths) + self.nb_drones)
                / len(self.paths)
            )
            - 1
        )

    def register_path(self, path: Path) -> None:
        """
        Adds a path to the algorithm's active set and updates
        edge-to-path mappings.

        Args:
            path (Path): The path to be registered.
        """
        for i in range(len(path.vertices) - 1):
            self.edges[(path.vertices[i], path.vertices[i + 1])].paths.append(
                path
            )
        self.paths.append(path)

    def get_candidate_paths(self) -> None:
        """
        Iteratively identifies and refines augmenting paths until optimal
        throughput is reached.
        """
        if (new_path := self.new_path_to_target()) is None:
            return
        self.register_path(new_path)
        self.cost = new_path.cost + self.nb_drones - 1
        while len(self.paths) < self.nb_drones:
            if (new_path := self.new_path_to_target()) is None:
                return
            if new_path.cost > self.cost:
                return
            self.reroute_paths(new_path)
            self.register_path(new_path)
            self.cost = self.calculate_cost()

    def recalculate_path_cost(self, path: Path) -> None:
        """
        Recalculates the total turn cost and priority score based on current
            hub/edge data.

        Args:
            data (FlyInAlgorithm): The main algorithm instance containing
                the graph.
        """
        path.priority = sum(
            1 if self.vertices[vertex].priority else 0
            for vertex in path.vertices
        )
        path.cost = sum(
            self.edges[(path.vertices[i], path.vertices[i + 1])].length
            for i in range(len(path.vertices) - 1)
        )

    def reroute_paths(self, path: Path) -> None:
        """
        Untangles path conflicts by resolving overlapping and residual flows.

        Args:
            path (Path): The newly discovered path containing potential
                cancellations.
        """
        i = 0
        while i < len(path.vertices) - 1:
            if self.edges[(path.vertices[i + 1], path.vertices[i])].flow > 0:
                self.edges[(path.vertices[i + 1], path.vertices[i])].flow -= 1
                self.vertices[path.vertices[i]].flow -= 1
                self.vertices[path.vertices[i + 1]].flow -= 1
                old_path = self.edges[
                    (path.vertices[i + 1], path.vertices[i])
                ].paths.pop()
                new_i = old_path.vertices.index(path.vertices[i + 1])
                new_path = old_path.vertices[:new_i] + path.vertices[i + 1:]
                old_path.vertices = (
                    path.vertices[:i] + old_path.vertices[new_i + 1:]
                )
                self.recalculate_path_cost(old_path)
                while new_path[new_i - 1] == new_path[new_i + 1] and new_i > 0:
                    self.vertices[new_path[new_i - 1]].flow -= 1
                    self.vertices[new_path[new_i]].flow -= 1
                    new_path = new_path[:new_i - 1] + new_path[new_i + 1:]
                    new_i -= 1
                path.vertices = new_path
                i = new_i
            i += 1
        self.recalculate_path_cost(path)

    def route_optimization(self) -> None:
        """
        Performs the final distribution of drones across the identified
        disjoint paths.
        """
        self.get_candidate_paths()
        self.paths.sort(key=lambda x: x.priority, reverse=True)
        drones = self.nb_drones
        for path in self.paths:
            path_drones = min(drones, self.cost - path.cost + 1)
            path.nb_drones = path_drones
            drones -= path_drones
        self.paths = [path for path in self.paths if path.nb_drones > 0]
