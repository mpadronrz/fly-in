from typing import Any


class Drone:
    """
    Represents an autonomous drone within the simulation.

    This class tracks the drone's state, including its current position,
    assigned path progress, and coordinates for graphical rendering.

    Attributes:
        id (int): Unique identifier for the drone, used for logging as D<id>.
        hub_index (int): Current progress index along the drone's
            assigned path.
        waiting (bool): Whether the drone is waiting to enter a
            restricted zone.
        finished (bool): Whether the drone has reached the target location.
        drone_graphics (Any): Reference to the GUI/Pygame surface or
            sprite object.
        current_coords (Tuple[int, int]): The abstract x, y coordinates of
            the drone's current location.
        target_coords (Tuple[int, int]): The x, y coordinates of the
            destination for the current turn's movement.
    """
    def __init__(self, id: int):
        """
        Initializes a new Drone instance.

        Args:
            id (int): The unique identification number for the drone.
        """
        self.id = id
        self.hub_index = 0
        self.waiting = False
        self.finished = False
        self.drone_graphics: Any = None
        self.current_coords = (0, 0)
        self.target_coords = (0, 0)
