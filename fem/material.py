"""Material model definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class Material:
    name: str
    elastic_modulus: float
    density: float = 0.0
