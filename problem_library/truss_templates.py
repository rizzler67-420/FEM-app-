"""Predefined truss problem templates."""

from fem.elements import TrussElement2D
from fem.material import Material
from fem.model import FEMModel
from fem.section import Section


def triangular_truss(span: float, height: float, P: float, material: Material, section: Section) -> FEMModel:
    if span <= 0 or height <= 0:
        raise ValueError("span and height must be positive")
    model = FEMModel(problem_type="2d_truss")
    n0 = model.add_node(0.0, 0.0)
    n1 = model.add_node(span, 0.0)
    n2 = model.add_node(span / 2, height)
    for eid, (ni, nj) in enumerate([(n0, n2), (n2, n1), (n0, n1)]):
        model.add_element(TrussElement2D(eid, ni, nj, material, section))
    model.add_support(0, "ux")
    model.add_support(0, "uy")
    model.add_support(1, "uy")
    model.add_nodal_load(2, "uy", -abs(P))
    return model


def warren_truss(span: float, height: float, n_panels: int, P: float, material: Material, section: Section) -> FEMModel:
    if span <= 0 or height <= 0 or n_panels < 2:
        raise ValueError("span and height must be >0 and n_panels >=2")
    model = FEMModel(problem_type="2d_truss")
    panel = span / n_panels

    bottom_nodes = [model.add_node(i * panel, 0.0) for i in range(n_panels + 1)]
    top_nodes = [model.add_node((i + 0.5) * panel, height if i % 2 == 0 else height) for i in range(n_panels)]

    eid = 0
    for i in range(n_panels):
        model.add_element(TrussElement2D(eid, bottom_nodes[i], bottom_nodes[i + 1], material, section))
        eid += 1

    for i in range(n_panels):
        model.add_element(TrussElement2D(eid, bottom_nodes[i], top_nodes[i], material, section))
        eid += 1
        model.add_element(TrussElement2D(eid, top_nodes[i], bottom_nodes[i + 1], material, section))
        eid += 1

    model.add_support(bottom_nodes[0].id, "ux")
    model.add_support(bottom_nodes[0].id, "uy")
    model.add_support(bottom_nodes[-1].id, "uy")
    model.add_nodal_load(top_nodes[len(top_nodes) // 2].id, "uy", -abs(P))
    return model
