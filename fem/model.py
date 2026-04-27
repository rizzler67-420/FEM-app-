"""FEM model container and assembly routines."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from fem.elements import BaseElement2D
from fem.node import Node


@dataclass
class FEMModel:
    problem_type: str
    nodes: list[Node] = field(default_factory=list)
    elements: list[BaseElement2D] = field(default_factory=list)
    supports: dict[tuple[int, str], float] = field(default_factory=dict)
    nodal_loads: dict[tuple[int, str], float] = field(default_factory=dict)

    _dof_map: dict[str, int] = field(default_factory=lambda: {"ux": 0, "uy": 1, "rz": 2})

    def add_node(self, x: float, y: float) -> Node:
        node = Node(id=len(self.nodes), x=x, y=y)
        self.nodes.append(node)
        return node

    def add_element(self, element: BaseElement2D) -> None:
        self.elements.append(element)

    def add_support(self, node_id: int, dof: str, value: float = 0.0) -> None:
        self.supports[(node_id, dof)] = value

    def add_nodal_load(self, node_id: int, dof: str, value: float) -> None:
        self.nodal_loads[(node_id, dof)] = self.nodal_loads.get((node_id, dof), 0.0) + value

    @property
    def ndof(self) -> int:
        return 3 * len(self.nodes)

    def dof_index(self, node_id: int, dof: str) -> int:
        return 3 * node_id + self._dof_map[dof]

    def assemble(self) -> tuple[np.ndarray, np.ndarray]:
        k = np.zeros((self.ndof, self.ndof), dtype=float)
        f = np.zeros(self.ndof, dtype=float)

        for element in self.elements:
            edofs = element.dof_indices()
            ke = element.global_stiffness()
            fe = element.equivalent_nodal_load_global()
            for i, gi in enumerate(edofs):
                f[gi] += fe[i]
                for j, gj in enumerate(edofs):
                    k[gi, gj] += ke[i, j]

        for (node_id, dof), value in self.nodal_loads.items():
            f[self.dof_index(node_id, dof)] += value

        return k, f
