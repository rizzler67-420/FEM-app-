# FEM-app-

Python finite element analysis (FEA) command-line application for simple 2D structural problems.

## Features

- Linear elastic, small-displacement 2D analysis.
- Problem types:
  - 2D truss
  - 2D beam
  - 2D frame
  - rectangular plate placeholder (future implementation)
- JSON-backed internal database for:
  - materials
  - sections
  - predefined problem templates
- Robust CLI workflow with input validation:
  1. choose problem type
  2. choose predefined problem
  3. choose material
  4. choose section
  5. enter parameters
  6. solve and display results
  7. optionally plot undeformed/deformed shape
  8. solve another or exit

## Implemented predefined templates

- `cantilever_tip_load(L, P, material, section, n_elements)`
- `simply_supported_center_load(L, P, material, section, n_elements)`
- `simply_supported_udl(L, q, material, section, n_elements)`
- `triangular_truss(span, height, P, material, section)`
- `warren_truss(span, height, n_panels, P, material, section)`
- `portal_frame(width, height, P, material, section)`

Each template auto-generates nodes, elements, supports, and loads, then returns a complete `FEMModel` object.

## Project structure

```text
fem/
  node.py
  material.py
  section.py
  elements.py
  model.py
  solver.py
  postprocess.py
database/
  materials.json
  sections.json
  problems.json
problem_library/
  beam_templates.py
  truss_templates.py
  frame_templates.py
  plate_templates.py
ui/
  cli.py
main.py
requirements.txt
tests/
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Result output

After solving, the app displays:

- nodal displacement table (`ux`, `uy`, `rz`)
- support reaction table
- internal element force table
- maximum displacement
- maximum axial force
- maximum bending moment (for frame/beam elements)

SI units are used throughout. Large/small values are formatted in scientific notation.

## Validation / tests

Run tests with:

```bash
pytest -q
```

Included checks:

- cantilever tip displacement vs analytical Euler-Bernoulli solution
- global reaction equilibrium for simply supported beam center load
- global reaction equilibrium for simply supported beam UDL
- sanity checks for truss/frame templates and solver
- plate placeholder raises `NotImplementedError`
