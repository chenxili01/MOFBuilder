from __future__ import annotations

import importlib.util
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW_RUN = ROOT / "workflow" / "run.py"


def load_workflow_run_module():
    module_name = "workflow_run_for_tests"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, WORKFLOW_RUN)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_load_phases_accepts_live_plans_heading_style():
    workflow_run = load_workflow_run_module()

    phases = workflow_run.load_phases()

    assert [phase.number for phase in phases] == list(range(1, 9))
    assert phases[0].name == "Phase 1 - Planning/spec"
    assert phases[-1].name == "Phase 8 - Docs, examples, and test hardening"


def test_find_phase_index_falls_back_to_phase_number_when_titles_differ():
    workflow_run = load_workflow_run_module()
    phases = workflow_run.load_phases()

    phase_index = workflow_run.find_phase_index(
        phases,
        "Phase 2 — Additive Family/Template Role Metadata",
    )

    assert phase_index == 1
