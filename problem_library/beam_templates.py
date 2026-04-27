"""Predefined beam problem templates."""

from fem.elements import FrameElement2D
from fem.material import Material
from fem.model import FEMModel
from fem.section import Section


def _beam_mesh(length: float, n_elements: int, problem_type: str = "2d_beam") -> FEMModel:
    if length <= 0 or n_elements < 1:
        raise ValueError("Length must be > 0 and n_elements >= 1.")
    model = FEMModel(problem_type=problem_type)
    for i in range(n_elements + 1):
        model.add_node(x=length * i / n_elements, y=0.0)
    return model


def cantilever_tip_load(L: float, P: float, material: Material, section: Section, n_elements: int) -> FEMModel:
    model = _beam_mesh(L, n_elements)
    for i in range(n_elements):
        model.add_element(FrameElement2D(i, model.nodes[i], model.nodes[i + 1], material, section))
    model.add_support(0, "ux")
    model.add_support(0, "uy")
    model.add_support(0, "rz")
    model.add_nodal_load(n_elements, "uy", -abs(P))
    return model


def simply_supported_center_load(L: float, P: float, material: Material, section: Section, n_elements: int) -> FEMModel:
    model = _beam_mesh(L, n_elements)
    for i in range(n_elements):
        model.add_element(FrameElement2D(i, model.nodes[i], model.nodes[i + 1], material, section))
    model.add_support(0, "ux")
    model.add_support(0, "uy")
    model.add_support(n_elements, "uy")
    mid = n_elements // 2
    model.add_nodal_load(mid, "uy", -abs(P))
    return model


def simply_supported_udl(L: float, q: float, material: Material, section: Section, n_elements: int) -> FEMModel:
    model = _beam_mesh(L, n_elements)
    for i in range(n_elements):
        model.add_element(FrameElement2D(i, model.nodes[i], model.nodes[i + 1], material, section, udl_local_y=-abs(q)))
    model.add_support(0, "ux")
    model.add_support(0, "uy")
    model.add_support(n_elements, "uy")
    return model
