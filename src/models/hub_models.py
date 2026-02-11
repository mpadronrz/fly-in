from enum import Enum
from pydantic import BaseModel, field_validator, Field, model_validator
from src.models.color import Color


class ZoneType(str, Enum):
    """Enumeration of possible hub zone types."""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class HubData(BaseModel):
    """
    Data model representing a physical hub in the network.

    Attributes:
        name (str): Unique identifier for the hub (no dashes/spaces).
        coords (tuple[int, int]): Cartesian coordinates (x, y).
        max_drones (int): Maximum number of drones the hub can hold.
        color_str (str): Display color for the hub.
        zone (ZoneType): The type of zone.
    """
    name: str
    coords: tuple[int, int]
    max_drones: int = Field(ge=1, default=1)
    color: str = "default"
    zone: ZoneType = ZoneType.NORMAL
    graphic_coords: tuple[int, int] = (0, 0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensures the hub name contains no invalid characters."""
        if "-" in v or " " in v:
            raise ValueError("Zone names cannot contain dashes or spaces")
        return v

    @model_validator(mode='after')
    def set_color_data(self) -> 'HubData':
        """Converts the color string into a Color Enum object after init."""
        self._color_data = Color.from_str(self.color)
        return self

    @property
    def color_data(self) -> Color:
        """Access the Smart Color object (with .rgb and .ansi)."""
        return self._color_data


class ConnectionData(BaseModel):
    """
    Represents a bidirectional link between two hubs.

    Attributes:
        hubs (tuple[str, str]): The names of the two connected hubs.
        max_link_capacity (int): Max drones allowed on this link.
    """
    # Essential for Pydantic to allow custom __hash__ and set storage
    # model_config = ConfigDict(frozen=True)
    hubs: tuple[str, str]
    max_link_capacity: int = Field(ge=1, default=1)

    @field_validator("hubs")
    @classmethod
    def validate_hubs(cls, v: tuple[str, str]) -> tuple[str, str]:
        """
        Ensures the connection doesn't link the same hub and
        sorts both hubs alphabetically to ensure (A, B) == (B, A)
        """
        if v[0] == v[1]:
            raise ValueError("Connection cannot link a hub to itself")
        if v[0] > v[1]:
            return (v[1], v[0])
        return v

    def __eq__(self, other: object) -> bool:
        """
        Determines equality based on the connected hubs.

        Args:
            other (object): The object to compare with this instance.

        Returns:
            bool: True if 'other' is a ConnectionData instance and has
                the identical hub pair, False otherwise.
        """
        if not isinstance(other, ConnectionData):
            return False
        return self.hubs == other.hubs

    def __hash__(self) -> int:
        """
        Returns a hash value based on the hub names.

        This allows ConnectionData instances to be stored in sets or used
        as dictionary keys, ensuring link uniqueness.

        Returns:
            int: The hash value of the hubs tuple.
        """
        return hash(self.hubs)


class FlyInData:
    """
    Root container for all parsed map data.

    Attributes:
        nb_drones (int): Total number of drones in the simulation.
        hubs (dict[str, HubData]): Map of hub names to their data.
        connections (set[ConnectionData]): List of link definitions.
        start (str): Name of the starting hub.
        end (str): Name of the ending hub.
    """
    def __init__(self) -> None:
        """
        Initializes the FlyInData container with empty registries.

        Attributes:
            _nb_drones (int): Internal storage for the number of drones.
            _hubs (dict): Internal mapping of hub names to HubData objects.
            _hubs_coords (set): Internal registry of occupied coordinates.
            _connections (set): Internal collection of unique network links.
            start (str): The name of the designated departure hub.
            end (str): The name of the designated arrival hub.
        """
        self._nb_drones = 0
        self._hubs: dict[str, HubData] = {}
        self._hubs_coords: set[tuple[int, int]] = set()
        self._connections: set[ConnectionData] = set()
        self.start = ""
        self.end = ""

    @property
    def nb_drones(self) -> int:
        """int: The total number of drones available in the simulation."""
        return self._nb_drones

    @nb_drones.setter
    def nb_drones(self, drones: int) -> None:
        """
        Sets the number of drones.

        Args:
            drones (int): The number of drones to assign.

        Raises:
            ValueError: If drones is less than 1.
        """
        if drones < 1:
            raise ValueError("Number of drones must be a positive integer.")
        self._nb_drones = drones

    @property
    def hubs(self) -> dict[str, HubData]:
        """
        dict[str, HubData]: Mapping of hub names to their respective data.
        """
        return self._hubs

    @property
    def hubs_coords(self) -> set[tuple[int, int]]:
        """set[tuple[int, int]]: Registry of all occupied hub coordinates."""
        return self._hubs_coords

    @property
    def connections(self) -> set[ConnectionData]:
        """
        set[ConnectionData]: Unique set of all established hub connections.
        """
        return self._connections

    def add_hub(self, new_hub: HubData) -> None:
        """
        Registers a new hub in the simulation data.

        Validates that both the hub name and its coordinates are unique
        before adding to the internal registries.

        Args:
            new_hub (HubData): The hub object to be added.

        Raises:
            ValueError: If the hub name or coordinates are already in use.
        """
        if new_hub.name in self.hubs:
            raise ValueError(
                f"Hub name {new_hub.name!r} "
                "is already asociated to another hub"
            )
        if new_hub.coords in self.hubs_coords:
            raise ValueError(
                f"Hub coordinates {new_hub.coords} "
                "are already asociated to another hub"
            )
        self._hubs[new_hub.name] = new_hub
        self._hubs_coords.add(new_hub.coords)

    def add_connection(self, new_connection: ConnectionData) -> None:
        """
        Establishes a connection between two existing hubs.

        Args:
            new_connection (ConnectionData): The connection to be registered.

        Raises:
            ValueError: If the connection already exists or if it references
                hubs that have not been defined yet.
        """
        if new_connection in self.connections:
            raise ValueError("Duplicate connection")
        for hub_name in new_connection.hubs:
            if hub_name not in self.hubs:
                raise ValueError(f"Unknown hub {hub_name!r}")
        self._connections.add(new_connection)
