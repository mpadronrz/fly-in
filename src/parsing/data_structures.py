from typing import Optional
from enum import Enum
from pydantic import BaseModel, field_validator, Field


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


class ConectionData(BaseModel):
    hubs: tuple[str, str]
    max_drones: int = Field(ge=1, default=1)


class FlyInData:
    def __init__(self) -> None:
        self._n_drones = 0
        self._hubs: dict[str, HubData] = {}
        self._conections: list[ConectionData] = []

    @property
    def n_drones(self) -> int:
        return self._n_drones

    @property
    def hubs(self) -> dict[str, HubData]:
        return self._hubs

    @property
    def conections(self) -> list[ConectionData]:
        return self._conections

    @n_drones.setter
    def drones(self, drones: int) -> None:
        if drones < 1:
            raise ValueError("Number of drones must be a positive integer.")
        self._drones = drones

    def add_hub(self, new_hub: HubData) -> None:
        if new_hub.name in self.hubs.keys():
            raise ValueError("")
