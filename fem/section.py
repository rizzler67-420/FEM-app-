"""Section properties for 2D members."""

from dataclasses import dataclass


@dataclass(slots=True)
class Section:
    name: str
    area: float
    inertia: float
