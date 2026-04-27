"""Linear solver for 2D FEM model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fem.elements import ElementResult
from fem.model import FEMModel


@dataclass
class SolverResult:
    displacements: np.ndarray
    reactions: dict[tuple[int, str], float]
    element_results: list[ElementResult]


class FEMSolver:
    def solve(self, model: FEMModel) -> SolverResult:
        k, f = model.assemble()
        u = np.zeros(model.ndof, dtype=float)

        fixed_indices = np.array([model.dof_index(nid, dof) for (nid, dof) in model.supports], dtype=int)
        fixed_values = np.array([val for val in model.supports.values()], dtype=float)
        free = np.setdiff1d(np.arange(model.ndof), fixed_indices)

        if free.size == 0:
            raise ValueError("Model has no free DOFs.")

        kff = k[np.ix_(free, free)]
        kfc = k[np.ix_(free, fixed_indices)] if fixed_indices.size else np.zeros((free.size, 0))
        ff = f[free]
        rhs = ff - kfc @ fixed_values

        u[free] = np.linalg.solve(kff, rhs)
        if fixed_indices.size:
            u[fixed_indices] = fixed_values

        reactions_vec = k @ u - f
        reactions = {(nid, dof): float(reactions_vec[model.dof_index(nid, dof)]) for (nid, dof) in model.supports}

        element_results = [el.result_from_displacements(u) for el in model.elements]
        return SolverResult(displacements=u, reactions=reactions, element_results=element_results)
