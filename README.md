# Agentic RTL Verification Harness — AXI4-Stream

A self-contained benchmark fixture for agent-under-test (AUT) RTL verification. An agent reads the structured spec, implements an AXI4-Stream packet monitor DUT, and is scored by automated cocotb/pytest pass/fail checks.

> **Background:** This is a clean-room public demo of an agentic RTL verification loop. Prior related work was under NDA; this repo is a minimal, reproducible slice — structured spec, stub DUT, golden reference, and automated cocotb/pytest scoring.

## Quickstart

### Prerequisites

- Python 3.9+
- [Icarus Verilog](http://iverilog.icarus.com/) (`iverilog`, `vvp`) on PATH
- GNU Make

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Run tests

```bash
# Validate harness against golden reference DUT (must pass)
make test-ref
# Or without make (Windows/cross-platform):
python scripts/run_sim.py --all --dut reference

# Run agent benchmark against stub DUT (expected to fail until implemented)
make test
python scripts/run_sim.py --all --dut stub

# Single scenario
make sim MODULE=test_single_packet DUT=stub
python scripts/run_sim.py test_single_packet --dut stub

# pytest wrapper
pytest tb/                      # stub DUT
pytest tb/ -m reference         # reference DUT
```

## Project Layout

```
docs/RTL_SPEC.md              Structured DUT specification
docs/AGENT_PROMPT.md          Copy-paste prompt for agent benchmark
rtl/axi4_stream_packet_monitor.sv       Agent-facing stub (incomplete)
rtl/reference/..._ref.sv      Golden reference implementation
sim/tb_top.sv                 Cocotb simulation top
tb/                           Cocotb testbenches + pytest integration
```

## Agent-in-the-Loop Workflow

1. Read [`docs/RTL_SPEC.md`](docs/RTL_SPEC.md) and [`docs/AGENT_PROMPT.md`](docs/AGENT_PROMPT.md).
2. Implement the DUT in [`rtl/axi4_stream_packet_monitor.sv`](rtl/axi4_stream_packet_monitor.sv).
3. Run `make test` or `pytest tb/`.
4. Fix failures iteratively until all three scenarios pass:
   - **Single packet** — counting, header capture, activity timing
   - **Back-to-back** — consecutive packets without idle gap
   - **Async reset** — counters cleared on reset, correct post-reset behavior

## Test Scenarios

| Test | File | Description |
|------|------|-------------|
| Single packet | `tb/test_single_packet.py` | One 3-beat packet; verify counts, header, activity |
| Back-to-back | `tb/test_back_to_back.py` | Two consecutive packets |
| Async reset | `tb/test_async_reset.py` | Reset during idle and during activity |

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make sim MODULE=<test> DUT=stub\|reference` | Run one cocotb test |
| `make test` | All tests against stub DUT |
| `make test-ref` | All tests against reference DUT |
| `make clean-all` | Remove build artifacts |
