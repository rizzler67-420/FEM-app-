"""Command-line interface for FEM application."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from fem.material import Material
from fem.postprocess import displacements_table, element_forces_table, plot_deformed_shape, reactions_table, summary_metrics
from fem.section import Section
from fem.solver import FEMSolver
from problem_library.beam_templates import cantilever_tip_load, simply_supported_center_load, simply_supported_udl
from problem_library.frame_templates import portal_frame
from problem_library.plate_templates import simple_rectangular_plate
from problem_library.truss_templates import triangular_truss, warren_truss

BASE_DIR = Path(__file__).resolve().parents[1]


TEMPLATE_REGISTRY: dict[str, Callable[..., Any]] = {
    "cantilever_tip_load": cantilever_tip_load,
    "simply_supported_center_load": simply_supported_center_load,
    "simply_supported_udl": simply_supported_udl,
    "triangular_truss": triangular_truss,
    "warren_truss": warren_truss,
    "portal_frame": portal_frame,
    "portal_frame_horizontal": lambda **kw: portal_frame(**kw, load_direction="horizontal"),
    "portal_frame_vertical": lambda **kw: portal_frame(**kw, load_direction="vertical"),
    "simple_rectangular_plate": simple_rectangular_plate,
}


def _load_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _input_choice(prompt: str, options: list[str]) -> int:
    while True:
        print(prompt)
        for i, text in enumerate(options, start=1):
            print(f"  {i}. {text}")
        raw = input("Select option: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print("Invalid choice. Please enter a valid number.")


def _input_float(name: str) -> float:
    while True:
        raw = input(f"Enter {name}: ").strip()
        try:
            value = float(raw)
            return value
        except ValueError:
            print("Invalid number. Try again.")


def _input_int(name: str) -> int:
    while True:
        raw = input(f"Enter {name}: ").strip()
        try:
            value = int(raw)
            if value <= 0:
                print("Value must be positive.")
                continue
            return value
        except ValueError:
            print("Invalid integer. Try again.")


def run_cli() -> None:
    materials_db = _load_json(BASE_DIR / "database" / "materials.json")
    sections_db = _load_json(BASE_DIR / "database" / "sections.json")
    problems_db = _load_json(BASE_DIR / "database" / "problems.json")

    print("\n=== FEM Application (SI Units) ===")
    solver = FEMSolver()

    while True:
        type_names = sorted({p["problem_type"] for p in problems_db})
        type_idx = _input_choice("\nAvailable problem types:", type_names)
        selected_type = type_names[type_idx]
        type_problems = [p for p in problems_db if p["problem_type"] == selected_type]

        prob_idx = _input_choice("\nAvailable predefined problems:", [p["name"] for p in type_problems])
        problem = type_problems[prob_idx]

        mat_idx = _input_choice("\nAvailable materials:", [m["name"] for m in materials_db])
        material = Material(**materials_db[mat_idx])

        sec_idx = _input_choice("\nAvailable sections:", [s["name"] for s in sections_db])
        section = Section(**sections_db[sec_idx])

        params: dict[str, Any] = {}
        print("\nEnter problem parameters:")
        for p in problem["parameters"]:
            if p.startswith("n_"):
                params[p] = _input_int(p)
            else:
                params[p] = _input_float(p)

        template_name = problem["template"]
        template_fn = TEMPLATE_REGISTRY[template_name]

        try:
            model = template_fn(material=material, section=section, **params)
            result = solver.solve(model)
        except NotImplementedError as exc:
            print(f"\nTemplate not implemented: {exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"\nError while solving problem: {exc}")
        else:
            print("\n" + displacements_table(model, result))
            print("\n" + reactions_table(result))
            print("\n" + element_forces_table(result))
            print("\n" + summary_metrics(result))
            view = input("\nShow undeformed/deformed plot? [y/n]: ").strip().lower()
            if view in {"y", "yes"}:
                plot_deformed_shape(model, result)

        again = input("\nSolve another problem? [y/n]: ").strip().lower()
        if again not in {"y", "yes"}:
            print("Exiting FEM application.")
            break
