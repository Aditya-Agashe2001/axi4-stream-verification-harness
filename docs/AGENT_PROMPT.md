# Agent Prompt: AXI4-Stream Packet Monitor

You are an RTL design agent. Implement the module described below and verify it passes all automated tests.

## Task

Implement `axi4_stream_packet_monitor` in:

```
rtl/axi4_stream_packet_monitor.sv
```

Read the full specification in [`docs/RTL_SPEC.md`](RTL_SPEC.md).

## DUT Summary

Passive AXI4-Stream monitor that:

1. **Counts packets** — increment on each accepted beat with `tlast=1`
2. **Counts bytes** — increment by popcount(`tkeep`) per accepted beat
3. **Captures headers** — latch `tdata` of the first beat of each packet; pulse `header_valid` for one cycle
4. **Signals activity** — assert from first beat through one cycle after `tlast` handshake

Interface: 32-bit AXI4-Stream slave (`tvalid`, `tready`, `tdata`, `tkeep`, `tlast`), async active-low reset.

## Constraints

- `s_axis_tready` must always be 1 (full throughput)
- Reset is asynchronous assert, synchronous deassert
- Use SystemVerilog compatible with Icarus Verilog (`iverilog -g2012`)

## How to Verify

```bash
pip install -r requirements.txt
make test
```

Or via pytest:

```bash
pytest tb/
```

## Acceptance Checklist

Run tests iteratively until all pass:

- [ ] **AC-1 Single packet** (`test_single_packet`) — 3-beat packet: counts, header, activity timing
- [ ] **AC-2 Back-to-back** (`test_back_to_back`) — two consecutive packets without idle gap
- [ ] **AC-3 Async reset** (`test_async_reset`) — reset clears state; post-reset transfers work

## Iteration Loop

1. Read failing test output carefully.
2. Fix the DUT logic.
3. Re-run `make test`.
4. Repeat until all three tests pass.

## Do Not Modify

- Test files in `tb/`
- Simulation top in `sim/tb_top.sv`
- Reference implementation in `rtl/reference/`

Only edit `rtl/axi4_stream_packet_monitor.sv`.

## Harness Self-Check

The reference DUT passes all tests. To confirm the harness works:

```bash
make test-ref
```

Your implementation should pass the same tests when complete:

```bash
make test
```
