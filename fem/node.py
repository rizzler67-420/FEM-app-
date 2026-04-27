"""Node definitions for 2D FEM models."""

from dataclasses import dataclass


@dataclass(slots=True)
class Node:
    """A 2D node with translational and rotational DOFs."""

    id: int
    x: float
    y: float

    @property
    def dof_indices(self) -> tuple[int, int, int]:
        base = 3 * self.id
        return (base, base + 1, base + 2)
