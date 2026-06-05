#!/usr/bin/env python3
"""Cross-platform cocotb runner (Icarus Verilog). Use when make is unavailable."""

from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from cocotb_tools.runner import get_runner

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TB_DIR = PROJECT_ROOT / "tb"

TEST_MODULES = [
    "test_single_packet",
    "test_back_to_back",
    "test_async_reset",
]


def _parse_results(results_xml: Path) -> tuple[int, int, int]:
    tree = ET.parse(results_xml)
    testcases = tree.findall(".//testcase")
    failures = sum(
        1
        for tc in testcases
        if tc.find("failure") is not None or tc.find("error") is not None
    )
    return len(testcases), failures, 0


def run_sim(module: str, dut: str = "stub") -> None:
    if dut == "reference":
        sources = [
            PROJECT_ROOT / "rtl/reference/axi4_stream_packet_monitor_ref.sv",
            PROJECT_ROOT / "sim/tb_top.sv",
        ]
        defines = {"USE_REFERENCE_DUT": 1}
    else:
        sources = [
            PROJECT_ROOT / "rtl/axi4_stream_packet_monitor.sv",
            PROJECT_ROOT / "sim/tb_top.sv",
        ]
        defines = {}

    build_dir = PROJECT_ROOT / "sim_build" / dut / module
    results_path = build_dir / "results.xml"

    env = os.environ.copy()
    env.pop("PYTEST_CURRENT_TEST", None)
    os.environ.update(env)

    runner = get_runner("icarus")
    runner.build(
        sources=[str(s) for s in sources],
        hdl_toplevel="tb_top",
        build_dir=str(build_dir),
        defines=defines,
        build_args=["-g2012"],
    )
    results_xml = runner.test(
        hdl_toplevel="tb_top",
        test_module=module,
        test_dir=str(TB_DIR),
        extra_env={"PYTHONPATH": str(TB_DIR)},
        results_xml=str(results_path),
    )

    tests, failures, errors = _parse_results(Path(results_xml))
    if failures or errors or tests == 0:
        raise RuntimeError(
            f"{module} (DUT={dut}): tests={tests} failures={failures} errors={errors}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run cocotb simulation")
    parser.add_argument("module", nargs="?", help="Test module name")
    parser.add_argument(
        "--dut",
        choices=["stub", "reference"],
        default="stub",
        help="DUT selection (default: stub)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all test modules",
    )
    args = parser.parse_args(argv)

    if args.all:
        exit_code = 0
        for mod in TEST_MODULES:
            try:
                run_sim(mod, args.dut)
                print(f"PASS: {mod} (DUT={args.dut})")
            except Exception as exc:
                print(f"FAIL: {mod} (DUT={args.dut}): {exc}")
                exit_code = 1
        return exit_code

    if not args.module:
        parser.error("module name required unless --all is set")

    run_sim(args.module, args.dut)
    print(f"PASS: {args.module} (DUT={args.dut})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
