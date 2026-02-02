from abc import ABC, abstractmethod
from typing import Any


class MapError(Exception):
    def __init__(self, msg: str, filename: str):
        super().__init__(f"Error parsing input file {filename}: {msg}")


class DataProcessor(ABC):
    @abstractmethod
    def process_data(line: str) -> Any:
        pass


class DroneProcessor(DataProcessor):
    def process_data(line: str) -> int:
        _, n_drones = line.split(":", 1)
        return int(n_drones)



class ReadFile:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.file: list[str] = []

    def read_file(self) -> None:
        try:
            with open(self.filename, "r") as f:
                file = f.read()
                for line in file.split("\n"):
                    line = line.strip()
                    if line and line[0] != "#":
                        self.file.append(line.lower())
        except OSError as e:
            raise MapError(e.strerror, self.filename)

    def parse_file(self) -> None:
        try:
            with open(self.filename, "r") as f:
                for line_num, line in enumerate(f):
                    line = line.strip().lower()
                    if not line or line[0] == "#":
                        continue

        except OSError as e:
            raise MapError(e.strerror, self.filename)
