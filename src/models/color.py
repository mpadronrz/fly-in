from enum import Enum
from typing import NamedTuple

class ColorInfo(NamedTuple):
    """Container for various color representations."""
    rgb: tuple[int, int, int]
    ansi: str

class Color(Enum):
    BLACK = ColorInfo((0, 0, 0), "\033[30m")
    RED = ColorInfo((255, 0, 0), "\033[31m")
    GREEN = ColorInfo((0, 255, 0), "\033[32m")
    YELLOW = ColorInfo((255, 255, 0), "\033[33m")
    BLUE = ColorInfo((0, 0, 255), "\033[34m")
    MAGENTA = ColorInfo((255, 0, 255), "\033[35m")
    CYAN = ColorInfo((0, 255, 255), "\033[36m")
    WHITE = ColorInfo((255, 255, 255), "\033[37m")

    CRIMSON = ColorInfo((220, 20, 60), "\033[31m")    # Maps to Red
    DARKRED = ColorInfo((139, 0, 0), "\033[31m")     # Maps to Red
    MAROON = ColorInfo((128, 0, 0), "\033[31m")      # Maps to Red
    GOLD = ColorInfo((255, 215, 0), "\033[33m")      # Maps to Yellow
    ORANGE = ColorInfo((255, 165, 0), "\033[33m")    # Maps to Yellow
    BROWN = ColorInfo((165, 42, 42), "\033[33m")     # Maps to Yellow/Red
    PURPLE = ColorInfo((128, 0, 128), "\033[35m")    # Maps to Magenta

    DEFAULT = ColorInfo((255, 255, 255), "\033[0m")

    @classmethod
    def from_str(cls, name: str) -> "Color":
        """
        Factory method to get a Color from a string.

        Args:
            name: The color name (e.g., 'red', 'BLUE').

        Returns:
            The matching Color member, or Color.DEFAULT if not found.
        """
        try:
            return cls[name.upper()]
        except (KeyError, AttributeError):
            return cls.DEFAULT

    @property
    def rgb(self) -> tuple[int, int, int]:
        """tuple[int, int, int]: The RGB representation (0-255)."""
        return self.value.rgb

    @property
    def ansi(self) -> str:
        """str: The ANSI escape sequence for terminal coloring."""
        return self.value.ansi
