# RTL Specification: AXI4-Stream Packet Monitor

## Overview

Design a passive **AXI4-Stream packet monitor** that observes an incoming AXI4-Stream slave interface and reports packet statistics, header capture, and activity status.

## Module

```
axi4_stream_packet_monitor
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DATA_WIDTH` | 32 | Width of `tdata` in bits |
| `KEEP_WIDTH` | `DATA_WIDTH/8` | Width of `tkeep` |

## Ports

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| `clk` | input | 1 | Rising-edge system clock |
| `rst_n` | input | 1 | Asynchronous active-low reset |
| `s_axis_tvalid` | input | 1 | AXI4-Stream valid |
| `s_axis_tready` | output | 1 | AXI4-Stream ready |
| `s_axis_tdata` | input | DATA_WIDTH | Transfer data |
| `s_axis_tkeep` | input | KEEP_WIDTH | Byte lane qualifiers |
| `s_axis_tlast` | input | 1 | Last beat of packet |
| `packet_count` | output | 32 | Completed packet counter |
| `byte_count` | output | 32 | Total byte counter |
| `header_capture` | output | DATA_WIDTH | First-beat data of current/most recent packet |
| `header_valid` | output | 1 | One-cycle pulse when header is captured |
| `activity` | output | 1 | Transfer-in-progress indicator |

## Functional Requirements

### FR-1: Ready Behavior

The monitor always accepts data at full throughput:

```
s_axis_tready = 1'b1
```

### FR-2: Handshake

A beat is **accepted** on a rising clock edge when:

```
s_axis_tvalid && s_axis_tready
```

### FR-3: Byte Counting

On each accepted beat, increment `byte_count` by the number of set bits in `s_axis_tkeep` (popcount).

Example: `tkeep = 4'b1110` → increment by 3.

### FR-4: Packet Counting

A **packet** completes on an accepted beat where `s_axis_tlast == 1`. Increment `packet_count` by 1 on that cycle.

### FR-5: Header Capture

The **header** is the `tdata` value of the first accepted beat of each packet (beat where the monitor transitions from idle-within-packet to active).

- Latch the header into `header_capture` on the first accepted beat of each packet.
- Assert `header_valid` for exactly **one clock cycle** on that beat.

### FR-6: Activity Signaling

`activity` indicates the monitor is processing a packet:

- Assert `activity` on the first accepted beat of a packet.
- Keep `activity` high through the packet, including the cycle where `tlast` is accepted.
- Deassert `activity` **one clock cycle after** the `tlast` handshake completes.
- When idle (no packet in progress), `activity` must be 0.

Timing example for a 3-beat packet (beats accepted on cycles 1, 2, 3):

| Cycle | Event | activity |
|-------|-------|----------|
| 1 | Beat 0 accepted | 1 |
| 2 | Beat 1 accepted | 1 |
| 3 | Beat 2 (tlast) accepted | 1 |
| 4 | Idle after packet | 0 |

### FR-7: Reset

`rst_n` is an **asynchronous active-low** reset:

- When `rst_n == 0`: immediately clear `packet_count`, `byte_count`, `header_capture`, `header_valid`, and `activity` to 0.
- Reset is **synchronous release**: normal operation resumes after `rst_n` returns to 1 on a clock edge.

### FR-8: Idle Behavior

When no transfers occur:

- `packet_count` and `byte_count` hold their values.
- `header_valid` is 0.
- `activity` is 0.
- `header_capture` holds the last captured header value.

## Acceptance Criteria (Test Mapping)

| ID | Scenario | Checks |
|----|----------|--------|
| AC-1 | Single 3-beat packet | `packet_count=1`, correct `byte_count`, header latched, `header_valid` pulse, `activity` timing |
| AC-2 | Two back-to-back packets | `packet_count=2`, cumulative bytes, two header captures |
| AC-3 | Async reset | Counters cleared on reset; correct behavior after deassert |

## Assumptions

- All packets contain at least one beat.
- `tkeep` may vary per beat; only set bits contribute to byte count.
- No `tuser`, `tid`, or `tdest` signals.
- No back-pressure modeling required (`tready` always 1).

## File to Implement

```
rtl/axi4_stream_packet_monitor.sv
```
