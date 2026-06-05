"""Shared AXI4-Stream BFM and scoreboard helpers for packet monitor tests."""

from __future__ import annotations

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import NextTimeStep, ReadOnly, RisingEdge


def popcount(keep: int) -> int:
    return bin(keep & 0xF).count("1")


class PacketMonitorTB:
    """Testbench wrapper for axi4_stream_packet_monitor DUT signals."""

    def __init__(self, dut):
        self.dut = dut
        self.clk_period_ns = 10

    async def setup(self):
        cocotb.start_soon(Clock(self.dut.clk, self.clk_period_ns, unit="ns").start())

        self.dut.rst_n.value = 0
        self.dut.s_axis_tvalid.value = 0
        self.dut.s_axis_tdata.value = 0
        self.dut.s_axis_tkeep.value = 0
        self.dut.s_axis_tlast.value = 0

        for _ in range(3):
            await RisingEdge(self.dut.clk)

        self.dut.rst_n.value = 1
        await RisingEdge(self.dut.clk)

    async def assert_reset(self, cycles: int = 2):
        self.dut.rst_n.value = 0
        for _ in range(cycles):
            await RisingEdge(self.dut.clk)

    async def deassert_reset(self):
        self.dut.rst_n.value = 1
        await RisingEdge(self.dut.clk)

    async def idle_cycles(self, n: int = 1):
        self.dut.s_axis_tvalid.value = 0
        for _ in range(n):
            await RisingEdge(self.dut.clk)

    async def drive_beat(self, tdata: int, tkeep: int, tlast: bool = False) -> dict:
        """Drive one beat; handshake completes on the next rising edge."""
        self.dut.s_axis_tvalid.value = 1
        self.dut.s_axis_tdata.value = tdata
        self.dut.s_axis_tkeep.value = tkeep
        self.dut.s_axis_tlast.value = int(tlast)
        await RisingEdge(self.dut.clk)
        await ReadOnly()
        sample = {
            "header_valid": int(self.dut.header_valid.value),
            "header_capture": int(self.dut.header_capture.value),
            "activity": int(self.dut.activity.value),
            "packet_count": int(self.dut.packet_count.value),
            "byte_count": int(self.dut.byte_count.value),
        }
        await NextTimeStep()
        self.dut.s_axis_tvalid.value = 0
        self.dut.s_axis_tlast.value = 0
        return sample

    async def drive_packet(self, beats: list[tuple[int, int, bool]]):
        """Drive a packet as list of (tdata, tkeep, tlast) tuples."""
        for tdata, tkeep, tlast in beats:
            await self.drive_beat(tdata, tkeep, tlast)

    def read_counts(self) -> tuple[int, int]:
        return int(self.dut.packet_count.value), int(self.dut.byte_count.value)

    async def sample_outputs(self) -> dict:
        await ReadOnly()
        result = {
            "packet_count": int(self.dut.packet_count.value),
            "byte_count": int(self.dut.byte_count.value),
            "header_capture": int(self.dut.header_capture.value),
            "header_valid": int(self.dut.header_valid.value),
            "activity": int(self.dut.activity.value),
        }
        await NextTimeStep()
        return result


def check_equal(actual, expected, name: str):
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected}, got {actual}")


async def expect_idle(tb: PacketMonitorTB):
    state = await tb.sample_outputs()
    check_equal(state["header_valid"], 0, "header_valid")
    check_equal(state["activity"], 0, "activity")


async def expect_counts(tb: PacketMonitorTB, packets: int, bytes_: int):
    await ReadOnly()
    pkt = int(tb.dut.packet_count.value)
    byt = int(tb.dut.byte_count.value)
    await NextTimeStep()
    check_equal(pkt, packets, "packet_count")
    check_equal(byt, bytes_, "byte_count")
