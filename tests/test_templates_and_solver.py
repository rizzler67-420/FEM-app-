import numpy as np
import pytest

from fem.material import Material
from fem.solver import FEMSolver
from fem.section import Section
from problem_library.beam_templates import cantilever_tip_load, simply_supported_center_load, simply_supported_udl
from problem_library.frame_templates import portal_frame
from problem_library.plate_templates import simple_rectangular_plate
from problem_library.truss_templates import triangular_truss, warren_truss


@pytest.fixture
def steel():
    return Material(name="Steel", elastic_modulus=210e9)


@pytest.fixture
def section():
    return Section(name="Test", area=0.01, inertia=8e-6)


def test_cantilever_tip_displacement_matches_theory(steel, section):
    L, P = 2.0, 1000.0
    model = cantilever_tip_load(L=L, P=P, material=steel, section=section, n_elements=12)
    result = FEMSolver().solve(model)
    uy_tip = result.displacements[model.dof_index(len(model.nodes) - 1, "uy")]
    theory = -P * L**3 / (3 * steel.elastic_modulus * section.inertia)
    assert np.isclose(uy_tip, theory, rtol=0.05)


def test_simply_supported_reactions_center_load(steel, section):
    P = 1200.0
    model = simply_supported_center_load(L=6.0, P=P, material=steel, section=section, n_elements=10)
    result = FEMSolver().solve(model)
    ry_left = result.reactions[(0, "uy")]
    ry_right = result.reactions[(len(model.nodes) - 1, "uy")]
    assert np.isclose(ry_left + ry_right, P, rtol=1e-3)


def test_simply_supported_udl_total_reaction(steel, section):
    L, q = 4.0, 800.0
    model = simply_supported_udl(L=L, q=q, material=steel, section=section, n_elements=8)
    result = FEMSolver().solve(model)
    total_reaction = result.reactions[(0, "uy")] + result.reactions[(len(model.nodes) - 1, "uy")]
    assert np.isclose(total_reaction, q * L, rtol=1e-3)


def test_truss_and_frame_templates_build_and_solve(steel, section):
    truss = triangular_truss(span=4.0, height=2.0, P=5e3, material=steel, section=section)
    warren = warren_truss(span=12.0, height=2.0, n_panels=6, P=8e3, material=steel, section=section)
    frame_h = portal_frame(width=4.0, height=3.0, P=10e3, material=steel, section=section)
    frame_v = portal_frame(width=4.0, height=3.0, P=10e3, material=steel, section=section, load_direction="vertical")

    for model in [truss, warren, frame_h, frame_v]:
        result = FEMSolver().solve(model)
        assert np.all(np.isfinite(result.displacements))


def test_plate_placeholder():
    with pytest.raises(NotImplementedError):
        simple_rectangular_plate()
