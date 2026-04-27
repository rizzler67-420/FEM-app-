"""Plate template placeholders."""

from fem.material import Material
from fem.model import FEMModel
from fem.section import Section


def simple_rectangular_plate(*args, **kwargs) -> FEMModel:
    raise NotImplementedError("Rectangular plate solver is a placeholder for future implementation.")
