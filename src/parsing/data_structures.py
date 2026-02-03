from typing import Optional
from enum import Enum
from pydantic import BaseModel, field_validator, Field, ConfigDict


class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class HubData(BaseModel):
    name: str
    coords: tuple[int, int]
    max_drones: int = Field(ge=1, default=1)
    color: Optional[str] = None
    zone_type: ZoneType = ZoneType.NORMAL

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if "-" in v or " " in v:
            raise ValueError("Zone names cannot contain dashes or spaces")
        return v


class ConnectionData(BaseModel):
    # Essential for Pydantic to allow custom __hash__ and set storage
    # model_config = ConfigDict(frozen=True)
    hubs: tuple[str, str]
    max_drones: int = Field(ge=1, default=1)

    @field_validator("hubs")
    @classmethod
    def validate_hubs(cls, v: tuple[str, str]) -> tuple[str, str]:
        if v[0] == v[1]:
            raise ValueError("Connection cannot link a hub to itself")
        if v[0] > v[1]:
            return (v[1], v[0])
        return v

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConnectionData):
            return False
        return self.hubs == other.hubs

    def __hash__(self) -> int:
        return hash(self.hubs)


class FlyInData:
    def __init__(self) -> None:
        self._nb_drones = 0
        self._hubs: dict[str, HubData] = {}
        self._hubs_coords: set[tuple[int, int]] = set()
        self._connections: set[ConnectionData] = set()
        self.start = ""
        self.end = ""

    @property
    def nb_drones(self) -> int:
        return self._nb_drones

    @nb_drones.setter
    def nb_drones(self, drones: int) -> None:
        if drones < 1:
            raise ValueError("Number of drones must be a positive integer.")
        self._nb_drones = drones

    @property
    def hubs(self) -> dict[str, HubData]:
        return self._hubs

    @property
    def hubs_coords(self) -> set[tuple[int, int]]:
        return self._hubs_coords

    @property
    def connections(self) -> set[ConnectionData]:
        return self._connections

    def add_hub(self, new_hub: HubData) -> None:
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
        if new_connection in self.connections:
            raise ValueError("Duplicate connection")
        for hub_name in new_connection.hubs:
            if hub_name not in self.hubs.keys():
                raise ValueError(f"Unknown hub {hub_name!r}")
        self._connections.add(new_connection)
