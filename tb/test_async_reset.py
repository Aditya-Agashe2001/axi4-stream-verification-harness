"""AC-3: Async reset during idle and during activity."""

import cocotb
from cocotb.triggers import ReadOnly, RisingEdge, NextTimeStep

from axi4_stream_driver import PacketMonitorTB, check_equal, expect_counts, expect_idle


async def expect_all_zero(tb: PacketMonitorTB):
    state = await tb.sample_outputs()
    check_equal(state["packet_count"], 0, "packet_count after reset")
    check_equal(state["byte_count"], 0, "byte_count after reset")
    check_equal(state["header_capture"], 0, "header_capture after reset")
    check_equal(state["header_valid"], 0, "header_valid after reset")
    check_equal(state["activity"], 0, "activity after reset")


@cocotb.test()
async def test_async_reset(dut):
    tb = PacketMonitorTB(dut)
    await tb.setup()

    # --- Phase 1: transfer then reset during idle ---
    await tb.drive_packet([
        (0x01020304, 0b1111, False),
        (0x05060708, 0b1111, True),
    ])
    await expect_counts(tb, packets=1, bytes_=8)
    await tb.idle_cycles(2)

    await tb.assert_reset(cycles=3)
    await expect_all_zero(tb)

    await tb.deassert_reset()
    await expect_idle(tb)

    # --- Phase 2: reset asserted during active transfer ---
    dut.s_axis_tvalid.value = 1
    dut.s_axis_tdata.value = 0xAABBCCDD
    dut.s_axis_tkeep.value = 0b1111
    dut.s_axis_tlast.value = 0
    await RisingEdge(dut.clk)
    await ReadOnly()
    check_equal(int(dut.activity.value), 1, "activity during mid-packet")
    await NextTimeStep()

    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.s_axis_tvalid.value = 0

    await expect_all_zero(tb)

    await tb.deassert_reset()

    # Post-reset transfer must work
    post_header = 0x99887766
    await tb.drive_packet([
        (post_header, 0b1111, False),
        (0x00000001, 0b1100, True),
    ])

    await expect_counts(tb, packets=1, bytes_=6)
    check_equal(int(dut.header_capture.value), post_header, "post-reset header")

    await tb.idle_cycles(2)
    await expect_idle(tb)

    dut._log.info("Async-reset test passed")
