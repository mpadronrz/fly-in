from abc import ABC, abstractmethod
from typing import Any
from src.parsing.data_structures import HubData, ConnectionData, FlyInData
import re


class MapError(Exception):
    def __init__(self, msg: str, filename: str):
        super().__init__(f"Error parsing input file {filename}: {msg}")


class DataProcessor(ABC):
    @abstractmethod
    def process_data(self, line: str, data: FlyInData) -> None:
        pass


class DroneProcessor(DataProcessor):
    def process_data(self, line: str, data: FlyInData) -> None:
        _, nb_drones = line.split(":", 1)
        data.nb_drones = int(nb_drones)


class HubProcessor(DataProcessor):
    def process_data(self, line: str, data: FlyInData) -> None:
        data: dict[str, Any] = {}
        hub_pattern = r"hub:\s+(\S+)\s+([+-]?\d+)\s+([+-]?\d+)(?:\s+\[(.*)\])?"
        matches = re.match(hub_pattern, line)
        if matches is None:
            raise ValueError(f"unrecognized pattern {line!r}")



class StartHubProcessor(DataProcessor):
    def process_data(self, line: str, data: FlyInData) -> None:
        pass


class EndHubProcessor(DataProcessor):
    def process_data(self, line: str, data: FlyInData) -> None:
        pass


class ConnectionProcessor(DataProcessor):
    def process_data(self, line: str, data: FlyInData) -> None:
        pass


class ReadFile:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.data = FlyInData()
        self.proccesors: dict[str, DataProcessor] = {
            "hub": HubProcessor(),
            "start_hub": StartHubProcessor(),
            "end_hub": EndHubProcessor(),
            "connection": ConnectionProcessor()
        }

    def ignore_line(line: str) -> bool:
        if not line or line[0] == "#":
            return True
        return False

    def find_nb_drones(self, enum_file: enumerate[str]) -> None:
        try:
            while True:
                line_num, line = next(enum_file)
                line = line.strip().lower()
                if self.ignore_line(line):
                    continue
                if not line.startswith("nb_drones:"):
                    raise MapError(
                        "expected to find 'nb_drones: <nb_drones>'",
                        f"{self.filename}, line {line_num + 1}"
                    )
                DroneProcessor().process_data(line, self.data, line_num)

        except StopIteration:
            raise MapError(
                "reached end-of-file without finding 'nb_drones'",
                f"{self.filename}, line {line_num + 1}"
            )
        except ValueError as e:
            raise MapError(
                e, f"{self.filename}, line {line_num + 1}"
            )

    def parse_file(self) -> None:
        try:
            with open(self.filename, "r") as f:
                enum_file = enumerate(f)
                self.find_drones(enum_file)
                for line_num, line in enum_file:
                    line = line.strip().lower()
                    if self.ignore_line(line):
                        continue
                    self.proccesors[line.split(":", 1)[0]].process_data(
                        line, self.data
                    )

        except OSError as e:
            raise MapError(e.strerror, self.filename)
        except KeyError:
            raise MapError(
                f"unable to process data: {line!r}",
                f"{self.filename}, line {line_num + 1}"
            )
