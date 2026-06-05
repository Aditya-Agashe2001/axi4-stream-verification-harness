"""pytest integration for cocotb AXI4-Stream packet monitor harness."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUN_SIM = PROJECT_ROOT / "scripts" / "run_sim.py"

TEST_MODULES = [
    "test_single_packet",
    "test_back_to_back",
    "test_async_reset",
]


def _run_cocotb_test(module: str, dut: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.pop("PYTEST_CURRENT_TEST", None)
    return subprocess.run(
        [sys.executable, str(RUN_SIM), module, "--dut", dut],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def pytest_generate_tests(metafunc):
    if "cocotb_module" in metafunc.fixturenames:
        metafunc.parametrize("cocotb_module", TEST_MODULES)


def _assert_cocotb_pass(cocotb_module: str, dut: str):
    result = _run_cocotb_test(cocotb_module, dut)
    combined = result.stdout + result.stderr
    assert result.returncode == 0, (
        f"cocotb test {cocotb_module} failed (DUT={dut})\n{combined}"
    )


def test_cocotb_scenario_stub(cocotb_module):
    _assert_cocotb_pass(cocotb_module, "stub")


@pytest.mark.reference
def test_cocotb_scenario_reference(cocotb_module):
    _assert_cocotb_pass(cocotb_module, "reference")
