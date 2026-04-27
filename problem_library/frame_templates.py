"""Predefined frame problem templates."""

from fem.elements import FrameElement2D
from fem.material import Material
from fem.model import FEMModel
from fem.section import Section


def portal_frame(
    width: float,
    height: float,
    P: float,
    material: Material,
    section: Section,
    load_direction: str = "horizontal",
) -> FEMModel:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    model = FEMModel(problem_type="2d_frame")
    n0 = model.add_node(0.0, 0.0)
    n1 = model.add_node(0.0, height)
    n2 = model.add_node(width, height)
    n3 = model.add_node(width, 0.0)

    model.add_element(FrameElement2D(0, n0, n1, material, section))
    model.add_element(FrameElement2D(1, n1, n2, material, section))
    model.add_element(FrameElement2D(2, n2, n3, material, section))

    for nid in (n0.id, n3.id):
        model.add_support(nid, "ux")
        model.add_support(nid, "uy")
        model.add_support(nid, "rz")

    if load_direction == "horizontal":
        model.add_nodal_load(n2.id, "ux", abs(P))
    elif load_direction == "vertical":
        model.add_nodal_load(n2.id, "uy", -abs(P))
    else:
        raise ValueError("load_direction must be 'horizontal' or 'vertical'")
    return model
