"""Unit tests for the arena dataset pipeline (registry + invariants).

These tests exercise the pure logic of scripts/generate_scenarios.py without
running the generator (no scenario regeneration). They lock in the registry
shape, the disjointness rule, and the manifest contract.

Run with:  python -m pytest tests/test_registry.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_scenarios as gs  # noqa: E402

CONFIG = ROOT / "config" / "scenarios.yaml"


@pytest.fixture(scope="module")
def cfg() -> dict:
    return gs.load_registry(CONFIG)


@pytest.fixture(scope="module")
def full_scale(cfg: dict) -> dict:
    return gs.resolve_scale(cfg, "full")


# --- registry shape ---------------------------------------------------------
def test_registry_has_expected_scenarios(cfg):
    ids = [s["id"] for s in cfg["scenarios"]]
    assert len(ids) == len(set(ids)), "scenario ids must be unique"
    for expected in ("baseline", "noop_neutral_controls", "drift_death_up_2018_2024",
                     "shock_covid_2020_2022", "volatility_ip_sigma_03",
                     "ip_recovery_mental_health_x2"):
        assert expected in ids


def test_every_family_has_train_and_test(cfg):
    by_family = {}
    for s in cfg["scenarios"]:
        by_family.setdefault(s["family"], set()).add(s["split"])
    for family, splits in by_family.items():
        assert splits == {"optimization", "heldout"}, f"family {family} lacks train or test: {splits}"


def test_scale_presets(cfg):
    for name in ("tiny", "medium", "full"):
        assert name in cfg["scales"]
    assert cfg["scales"]["full"]["n_policies"] == 250_000
    assert cfg["scales"]["full"]["target_factor"] == 1.0


# --- disjointness -----------------------------------------------------------
def test_disjointness_ok(cfg):
    gs.check_disjointness(cfg)  # raises SystemExit on violation


def test_disjointness_detects_overlap(cfg):
    broken = dict(cfg)
    scenarios = [dict(s) for s in cfg["scenarios"]]
    # force a real overlap: give a heldout scenario the exact controls of an
    # optimization scenario (shock_covid_2020_2022)
    covid = next(s for s in scenarios if s["id"] == "shock_covid_2020_2022")
    for s in scenarios:
        if s["id"] == "shock_death_2016":
            s["controls"] = covid["controls"]
    broken["scenarios"] = scenarios
    with pytest.raises(SystemExit):
        gs.check_disjointness(broken)


# --- manifest contract ------------------------------------------------------
def test_manifest_single_control(cfg, full_scale):
    spec = next(s for s in cfg["scenarios"] if s["id"] == "drift_death_up_2018_2024")
    m = gs._manifest_for(spec, cfg, full_scale)
    assert m["no_op"] is False
    assert m["primary"]["control_type"] == "drift"
    assert m["primary"]["benefit"] == "Death"
    assert m["primary"]["factor"] == 0.15
    assert m["benefit_lines_untouched"] == ["CI", "TPD", "IP"]


def test_manifest_multi_control(cfg, full_scale):
    spec = next(s for s in cfg["scenarios"] if s["id"] == "sys_shock_crisis_2020_2022")
    m = gs._manifest_for(spec, cfg, full_scale)
    assert m["primary"] is None  # multi-benefit shock cannot flatten
    assert len(m["controls"]) == 1
    assert m["controls"][0]["type"] == "shock"
    assert sorted(m["controls"][0]["benefit"]) == ["CI", "Death", "IP", "TPD"]


def test_manifest_noop(cfg, full_scale):
    spec = next(s for s in cfg["scenarios"] if s["id"] == "baseline")
    m = gs._manifest_for(spec, cfg, full_scale)
    assert m["no_op"] is True
    assert m["controls"] == []


def test_manifest_scale_metadata(cfg, full_scale):
    spec = next(s for s in cfg["scenarios"] if s["id"] == "volatility_ip_sigma_03")
    m = gs._manifest_for(spec, cfg, full_scale)
    assert m["scale"] == "full"
    assert m["n_policies"] == 250_000
    assert m["targets"]["IP"] == 15000
    assert m["study_window"] == [2015, 2024]
