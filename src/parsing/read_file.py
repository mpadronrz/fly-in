from abc import ABC, abstractmethod
from typing import Any, Optional
from src.models import (
    HubData,
    ConnectionData,
    FlyInData,
    ZoneType,
)
import re
from pydantic import ValidationError


class MapError(Exception):
    """Exception raised for errors encountered during map parsing."""
    def __init__(self, msg: str, filename: str):
        """
        Args:
            msg: The specific error message.
            filename: Location of the error (file and line number).
        """
        super().__init__(f"Error parsing input file {filename}: {msg}")


class DataProcessor(ABC):
    """
    Abstract base class for map data extraction strategies.

    This class defines the interface for all specialized processors that
    handle specific line types (drones, hubs, connections) within the
    map configuration file.
    """
    @abstractmethod
    def process_data(self, line: str, data: FlyInData) -> None:
        """
        Parses a single line of text and updates the FlyInData object.

        Args:
            line (str): The raw string from the map file to be processed.
            data (FlyInData): The data container to be updated
                with parsed values.

        Raises:
            ValueError: If the line format is invalid for this processor.
            ValidationError: If the data fails Pydantic model validation.
        """
        pass


class DroneProcessor(DataProcessor):
    """Processor responsible for parsing the 'nb_drones' configuration line."""
    def process_data(self, line: str, data: FlyInData) -> None:
        """
        Extracts the drone count and updates the simulation data.

        Expects a format: 'nb_drones: <integer>'.
        """
        _, nb_drones = line.split(":", 1)
        data.nb_drones = int(nb_drones)


class HubProcessor(DataProcessor):
    """
    Generic processor for hub-related lines (hub, start_hub, end_hub).

    Attributes:
        valid_metadata (list[str]): Permitted keys in the bracketed metadata.
        hub_type (str): The command prefix this processor instance looks for.
    """

    valid_metadata = ["color", "zone", "max_drones"]
    hub_type = "hub"

    def process_data(self, line: str, data: FlyInData) -> None:
        """
        Parses hub definitions and adds them to the FlyInData registry.

        Args:
            line (str): The hub definition line.
            data (FlyInData): the data registry
        """
        data_dict = self.get_data_dict(line)
        data.add_hub(HubData(**data_dict))

    def get_data_dict(self, line: str) -> dict[str, Any]:
        """
        Regex-parses the input line into a dictionary for HubData creation.

        Args:
            line (str): The hub definition line.

        Returns:
            dict[str, Any]: A dictionary containing name, coords, and metadata.

        Raises:
            ValueError: If the line does not match the expected hub pattern.
        """
        data_dict: dict[str, Any] = {}
        hub_pattern = (
            rf"{self.hub_type}:"
            r"\s+(\S+)\s+([+-]?\d+)\s+([+-]?\d+)"
            r"(?:\s+\[(.*)\])?$"
        )
        match = re.match(hub_pattern, line)
        if match is None:
            raise ValueError(
                f"unrecognized pattern {line!r}\nExpected '{self.hub_type}: "
                "<name: str> <x: int> <y: int> [ [metadata] ]'"
            )
        name, x, y, metadata = match.groups()
        data_dict["name"] = name
        data_dict["coords"] = (x, y)
        self.process_metadata(metadata, data_dict)
        return data_dict

    def process_metadata(
        self, metadata: Optional[str], data_dict: dict[str, Any]
    ) -> None:
        """
        Parses bracketed hub metadata into key-value pairs.

        Args:
            metadata (Optional[str]): The string content found within [].
            data_dict (dict[str, Any]): The dictionary to update with metadata.

        Raises:
            ValueError: If metadata is malformed, unknown, or repeated.
        """
        seen_metadata = []
        if metadata is None:
            return
        for piece in metadata.split():
            if "=" not in piece:
                raise ValueError(
                    f"invalid metadata: [{metadata}]\n"
                    "Expected [key=value] or [key1=value1 key2=value2 ...]"
                )
            key, val = piece.split("=", 1)
            if key not in self.valid_metadata:
                raise ValueError(
                    f"unknown metadata: {key!r}\n"
                    "Expected 'color', 'zone' or 'max_drones'"
                )
            if key in seen_metadata:
                raise ValueError(f"repeated metadata: {key!r}")
            data_dict[key] = val
            seen_metadata.append(key)


class StartHubProcessor(HubProcessor):
    """Processor for 'start_hub:' lines. Also sets the global start point."""

    hub_type = "start_hub"

    def process_data(self, line: str, data: FlyInData) -> None:
        """
        Parses the hub and assigns its name as the simulation starting hub.

        Args:
            line (str): The hub definition line.
            data (FlyInData): the data registry

        Raises:
            ValueError: If a start hub has already been defined or if the
                provided hub is in a blocked zone
        """
        if data.start:
            raise ValueError(
                "duplicate start_hub definition: already set to "
                f"{data.start!r}"
            )
        data_dict = self.get_data_dict(line)
        data.add_hub(HubData(**data_dict))
        data.start = data_dict["name"]
        if data.hubs[data.start].zone == ZoneType.BLOCKED:
            raise ValueError("start_hub cannot be blocked")


class EndHubProcessor(HubProcessor):
    """Processor for 'end_hub:' lines. Also sets the global end point."""

    hub_type = "end_hub"

    def process_data(self, line: str, data: FlyInData) -> None:
        """
        Parses the hub and assigns its name as the simulation destination.

        Args:
            line (str): The hub definition line.
            data (FlyInData): the data registry

        Raises:
            ValueError: If a end hub has already been defined or if the
                provided hub is in a blocked zone
        """
        if data.end:
            raise ValueError(
                f"duplicate end_hub definition: already set to {data.end!r}"
            )
        data_dict = self.get_data_dict(line)
        data.add_hub(HubData(**data_dict))
        data.end = data_dict["name"]
        if data.hubs[data.end].zone == ZoneType.BLOCKED:
            raise ValueError("end_hub cannot be blocked")


class ConnectionProcessor(DataProcessor):
    """Processor for 'connection:' lines defining links between hubs."""
    def process_data(self, line: str, data: FlyInData) -> None:
        """
        Parses connection info and adds it to the FlyInData registry.

        Args:
            line (str): The hub definition line.
            data (FlyInData): the data registry
        """
        data_dict = self.get_data_dict(line)
        data.add_connection(ConnectionData(**data_dict))

    def get_data_dict(self, line: str) -> dict[str, Any]:
        """
        Regex-parses the input line into a dict for ConnectionData creation.

        Args:
            line (str): The connection definition line.

        Returns:
            dict[str, Any]: A dictionary containing the hubs and metadata.

        Raises:
            ValueError: If the line does not match the expected pattern.
        """
        data_dict: dict[str, Any] = {}
        connection_pattern = (
            r"connection:\s+([^\s-]+)-([^\s-]+)(?:\s+\[(.*)\])?$"
        )
        match = re.match(connection_pattern, line)
        if match is None:
            raise ValueError(
                f"unrecognized pattern {line!r}\n"
                "Expected 'connection: <hub1>-<hub2> [ [metadata] ]"
            )
        hub1, hub2, metadata = match.groups()
        data_dict["hubs"] = (hub1, hub2)
        self.process_metadata(metadata, data_dict)
        return data_dict

    def process_metadata(
        self, metadata: Optional[str], data_dict: dict[str, Any]
    ) -> None:
        """
        Parses connection-specific metadata

        Args:
            metadata (Optional[str]): The string content found within [].
            data_dict (dict[str, Any]): The dictionary to update with metadata.

        Raises:
            ValueError: If metadata is malformed, unknown, or repeated.
        """
        if metadata is None or not metadata.strip():
            return
        if "=" not in metadata:
            raise ValueError(
                f"invalid metadata: [{metadata}]\nExpected [key=value]"
            )
        metadata = metadata.strip()
        key, val = metadata.split("=", 1)
        if key != "max_link_capacity":
            raise ValueError(
                f"unknown metadata: {key!r}.\nExpected 'max_link_capacity'"
            )
        data_dict[key] = val


class ReadFile:
    """
    Orchestrates the parsing of a map configuration file.

    This class manages the file reading process, delegates line parsing to
    specific DataProcessor strategies, and ensures the logical integrity
    of the resulting FlyInData object.

    Attributes:
        filename (str): Path to the map configuration file.
        data (FlyInData): The container where parsed information is stored.
        proccesors (dict): Mapping of command prefixes to their respective
            DataProcessor instances.
    """
    def __init__(self, filename: str) -> None:
        """
        Initializes the parser with a filename and required processors.

        Args:
            filename: The path to the file to be parsed.
        """
        self.filename = filename
        self.data = FlyInData()
        self.proccesors: dict[str, DataProcessor] = {
            "hub": HubProcessor(),
            "start_hub": StartHubProcessor(),
            "end_hub": EndHubProcessor(),
            "connection": ConnectionProcessor(),
        }

    def ignore_line(self, line: str) -> bool:
        """
        Determines if a line should be skipped during parsing.

        Args:
            line: The raw line string to check.

        Returns:
            bool: True if the line is empty or starts with a comment (#),
                False otherwise.
        """
        if not line or line[0] == "#":
            return True
        return False

    def find_nb_drones(self, enum_file: enumerate[str]) -> None:
        """
        Locates and parses the mandatory 'nb_drones' line.

        This method acts as a state guard, ensuring that 'nb_drones' is the
        first meaningful line in the file. It advances the file iterator.

        Args:
            enum_file: An enumerated iterator of the file lines.

        Raises:
            MapError: If 'nb_drones' is missing, misplaced, or malformed.
        """
        try:
            while True:
                line_num, line = next(enum_file)
                line = line.strip().lower()
                if self.ignore_line(line):
                    continue
                if not line.startswith("nb_drones:"):
                    raise MapError(
                        "expected to find 'nb_drones: <nb_drones>'",
                        f"{self.filename}, line {line_num + 1}",
                    )
                DroneProcessor().process_data(line, self.data)
                return

        except StopIteration:
            raise MapError(
                "reached end-of-file without finding 'nb_drones'",
                f"{self.filename}, line {line_num + 1}",
            )
        except ValueError as e:
            raise MapError(str(e), f"{self.filename}, line {line_num + 1}")

    def parse_file(self) -> None:
        """
        Reads the file line-by-line and dispatches data to processors.

        This is the core loop of the parser. It handles file I/O errors
        and maps low-level validation errors to user-friendly MapErrors.

        Raises:
            MapError: For any I/O issues, unknown data, or validation failures.
        """
        try:
            with open(self.filename, "r") as f:
                enum_file = enumerate(f)
                self.find_nb_drones(enum_file)
                for line_num, line in enum_file:
                    line = line.strip().lower()
                    if self.ignore_line(line):
                        continue
                    self.proccesors[line.split(":", 1)[0]].process_data(
                        line, self.data
                    )

        except OSError as e:
            raise MapError(str(e.strerror), self.filename)

        except KeyError:
            raise MapError(
                f"unknown command: {line.split(':', 1)[0]!r}\n"
                "Expected 'hub: <data>', 'start_hub: <data>', "
                "'end_hub: <data>' or 'connection: <data>'",
                f"{self.filename}, line {line_num + 1}",
            )

        except ValidationError as e:
            error = e.errors()[0]
            clean_error = error["msg"].replace("Value error, ", "")
            raise MapError(
                clean_error, f"{self.filename}, line {line_num + 1}"
            )

        except ValueError as e:
            raise MapError(str(e), f"{self.filename}, line {line_num + 1}")

    def check_start_end(self) -> None:
        """
        Verifies that both start and end hubs were defined in the map.

        Raises:
            MapError: If either the start_hub or end_hub is missing.
        """
        if not self.data.start:
            raise MapError(
                "finished parsing file without finding 'start_hub'",
                self.filename,
            )
        if not self.data.end:
            raise MapError(
                "finished parsing file without finding 'end_hub'",
                self.filename,
            )

    def get_fly_in_data(self) -> FlyInData:
        """
        Triggers the full parsing pipeline and returns the validated data.

        Returns:
            FlyInData: The fully populated and validated data structure.
        """
        self.parse_file()
        self.check_start_end()
        return self.data
