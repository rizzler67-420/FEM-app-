"""Element formulations for 2D truss and frame members."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from fem.material import Material
from fem.node import Node
from fem.section import Section


@dataclass
class ElementResult:
    element_id: int
    element_type: str
    axial_force: float
    shear_start: float | None = None
    shear_end: float | None = None
    moment_start: float | None = None
    moment_end: float | None = None


@dataclass
class BaseElement2D:
    id: int
    node_i: Node
    node_j: Node
    material: Material
    section: Section

    def length(self) -> float:
        return float(np.hypot(self.node_j.x - self.node_i.x, self.node_j.y - self.node_i.y))

    def direction_cosines(self) -> tuple[float, float]:
        l = self.length()
        c = (self.node_j.x - self.node_i.x) / l
        s = (self.node_j.y - self.node_i.y) / l
        return c, s

    def dof_indices(self) -> list[int]:
        raise NotImplementedError

    def global_stiffness(self) -> np.ndarray:
        raise NotImplementedError

    def equivalent_nodal_load_global(self) -> np.ndarray:
        return np.zeros(len(self.dof_indices()))

    def result_from_displacements(self, u_global: np.ndarray) -> ElementResult:
        raise NotImplementedError


@dataclass
class TrussElement2D(BaseElement2D):
    """2D truss element with axial stiffness only."""

    def dof_indices(self) -> list[int]:
        ui, vi, _ = self.node_i.dof_indices
        uj, vj, _ = self.node_j.dof_indices
        return [ui, vi, uj, vj]

    def global_stiffness(self) -> np.ndarray:
        l = self.length()
        c, s = self.direction_cosines()
        k = self.material.elastic_modulus * self.section.area / l
        return k * np.array(
            [
                [c * c, c * s, -c * c, -c * s],
                [c * s, s * s, -c * s, -s * s],
                [-c * c, -c * s, c * c, c * s],
                [-c * s, -s * s, c * s, s * s],
            ]
        )

    def result_from_displacements(self, u_global: np.ndarray) -> ElementResult:
        dofs = self.dof_indices()
        ue = u_global[dofs]
        l = self.length()
        c, s = self.direction_cosines()
        axial = self.material.elastic_modulus * self.section.area / l * np.dot(np.array([-c, -s, c, s]), ue)
        return ElementResult(element_id=self.id, element_type="truss", axial_force=float(axial))


@dataclass
class FrameElement2D(BaseElement2D):
    """Euler-Bernoulli 2D frame element."""

    udl_local_y: float = field(default=0.0)  # N/m, +local y

    def dof_indices(self) -> list[int]:
        return [*self.node_i.dof_indices, *self.node_j.dof_indices]

    def _local_stiffness(self) -> np.ndarray:
        l = self.length()
        e = self.material.elastic_modulus
        a = self.section.area
        i = self.section.inertia
        ea_l = e * a / l
        ei = e * i
        return np.array(
            [
                [ea_l, 0, 0, -ea_l, 0, 0],
                [0, 12 * ei / l**3, 6 * ei / l**2, 0, -12 * ei / l**3, 6 * ei / l**2],
                [0, 6 * ei / l**2, 4 * ei / l, 0, -6 * ei / l**2, 2 * ei / l],
                [-ea_l, 0, 0, ea_l, 0, 0],
                [0, -12 * ei / l**3, -6 * ei / l**2, 0, 12 * ei / l**3, -6 * ei / l**2],
                [0, 6 * ei / l**2, 2 * ei / l, 0, -6 * ei / l**2, 4 * ei / l],
            ]
        )

    def _transform(self) -> np.ndarray:
        c, s = self.direction_cosines()
        return np.array(
            [
                [c, s, 0, 0, 0, 0],
                [-s, c, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, c, s, 0],
                [0, 0, 0, -s, c, 0],
                [0, 0, 0, 0, 0, 1],
            ]
        )

    def global_stiffness(self) -> np.ndarray:
        t = self._transform()
        return t.T @ self._local_stiffness() @ t

    def equivalent_nodal_load_local(self) -> np.ndarray:
        if self.udl_local_y == 0:
            return np.zeros(6)
        l = self.length()
        q = self.udl_local_y
        return np.array([0, q * l / 2, q * l**2 / 12, 0, q * l / 2, -q * l**2 / 12])

    def equivalent_nodal_load_global(self) -> np.ndarray:
        return self._transform().T @ self.equivalent_nodal_load_local()

    def result_from_displacements(self, u_global: np.ndarray) -> ElementResult:
        dofs = self.dof_indices()
        ue_global = u_global[dofs]
        t = self._transform()
        ue_local = t @ ue_global
        fe_local = self._local_stiffness() @ ue_local - self.equivalent_nodal_load_local()
        return ElementResult(
            element_id=self.id,
            element_type="frame",
            axial_force=float(fe_local[0]),
            shear_start=float(fe_local[1]),
            moment_start=float(fe_local[2]),
            shear_end=float(fe_local[4]),
            moment_end=float(fe_local[5]),
        )
