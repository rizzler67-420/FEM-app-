"""Post-processing utilities: tabular output and plotting."""

from __future__ import annotations

import numpy as np
from matplotlib import pyplot as plt

from fem.model import FEMModel
from fem.solver import SolverResult


def _fmt(value: float) -> str:
    return f"{value:.3e}" if abs(value) >= 1e4 or (0 < abs(value) < 1e-3) else f"{value:.6f}"


def displacements_table(model: FEMModel, result: SolverResult) -> str:
    lines = ["Nodal Displacements (SI)", "Node        ux [m]        uy [m]       rz [rad]"]
    for node in model.nodes:
        ux, uy, rz = result.displacements[node.dof_indices[0]], result.displacements[node.dof_indices[1]], result.displacements[node.dof_indices[2]]
        lines.append(f"{node.id:>4}  {_fmt(ux):>12}  {_fmt(uy):>12}  {_fmt(rz):>12}")
    return "\n".join(lines)


def reactions_table(result: SolverResult) -> str:
    lines = ["Support Reactions (SI)", "Node  DOF      Reaction"]
    for (node_id, dof), reaction in sorted(result.reactions.items()):
        lines.append(f"{node_id:>4}  {dof:>3}  {_fmt(reaction):>12}")
    return "\n".join(lines)


def element_forces_table(result: SolverResult) -> str:
    lines = ["Element Internal Forces (SI)"]
    lines.append("Elem  Type       N [N]        V1 [N]        M1 [N.m]       V2 [N]        M2 [N.m]")
    for er in result.element_results:
        lines.append(
            f"{er.element_id:>4}  {er.element_type:>5}  {_fmt(er.axial_force):>12}  "
            f"{_fmt(er.shear_start or 0.0):>12}  {_fmt(er.moment_start or 0.0):>12}  "
            f"{_fmt(er.shear_end or 0.0):>12}  {_fmt(er.moment_end or 0.0):>12}"
        )
    return "\n".join(lines)


def summary_metrics(result: SolverResult) -> str:
    max_disp = np.max(np.abs(result.displacements))
    max_axial = max(abs(er.axial_force) for er in result.element_results)
    moments = [v for er in result.element_results for v in (er.moment_start, er.moment_end) if v is not None]
    max_moment = max((abs(m) for m in moments), default=0.0)
    return (
        "Summary\n"
        f"Maximum displacement: {_fmt(float(max_disp))} m\n"
        f"Maximum axial force: {_fmt(float(max_axial))} N\n"
        f"Maximum bending moment: {_fmt(float(max_moment))} N.m"
    )


def plot_deformed_shape(model: FEMModel, result: SolverResult, scale: float | None = None) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    coords = np.array([(n.x, n.y) for n in model.nodes])
    disp = np.array([(result.displacements[n.dof_indices[0]], result.displacements[n.dof_indices[1]]) for n in model.nodes])

    if scale is None:
        span = np.ptp(coords[:, 0]) if len(coords) > 1 else 1.0
        umax = max(np.max(np.linalg.norm(disp, axis=1)), 1e-12)
        scale = 0.05 * span / umax

    def pos(node_id: int, deformed: bool) -> tuple[float, float]:
        x, y = coords[node_id]
        if deformed:
            ux, uy = disp[node_id]
            return x + scale * ux, y + scale * uy
        return x, y

    for el in model.elements:
        xi, yi = pos(el.node_i.id, False)
        xj, yj = pos(el.node_j.id, False)
        ax.plot([xi, xj], [yi, yj], "k--", lw=1, label="Undeformed" if el.id == 0 else "")

        xi, yi = pos(el.node_i.id, True)
        xj, yj = pos(el.node_j.id, True)
        ax.plot([xi, xj], [yi, yj], "b-", lw=2, label="Deformed" if el.id == 0 else "")

    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.3)
    ax.set_title(f"Undeformed vs Deformed Shape (scale={scale:.2e})")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.legend()
    plt.tight_layout()
    plt.show()
