"""AC-1: Single 3-beat packet — counts, header capture, activity timing."""

import cocotb
from cocotb.triggers import ReadOnly, RisingEdge, NextTimeStep

from axi4_stream_driver import PacketMonitorTB, check_equal, expect_counts, expect_idle, popcount


@cocotb.test()
async def test_single_packet(dut):
    tb = PacketMonitorTB(dut)
    await tb.setup()

    await expect_idle(tb)

    header = 0xDEADBEEF
    beats = [
        (header, 0b1111, False),
        (0x11111111, 0b1110, False),
        (0x22222222, 0b1011, True),
    ]
    expected_bytes = sum(popcount(tkeep) for _, tkeep, _ in beats)

    for i, (tdata, tkeep, tlast) in enumerate(beats):
        sample = await tb.drive_beat(tdata, tkeep, tlast)

        if i == 0:
            check_equal(sample["header_valid"], 1, "header_valid on first beat")
            check_equal(sample["header_capture"], header, "header_capture")
        else:
            check_equal(sample["header_valid"], 0, f"header_valid beat {i}")

        check_equal(sample["activity"], 1, f"activity during beat {i}")

    await RisingEdge(dut.clk)
    await ReadOnly()
    check_equal(int(dut.activity.value), 0, "activity one cycle after tlast")
    await NextTimeStep()

    await expect_counts(tb, packets=1, bytes_=expected_bytes)

    final_header = int(dut.header_capture.value)
    check_equal(final_header, header, "header_capture held after packet")

    await tb.idle_cycles(2)
    await expect_idle(tb)

    dut._log.info("Single-packet test passed")
