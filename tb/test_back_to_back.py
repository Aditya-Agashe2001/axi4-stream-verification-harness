"""AC-2: Two back-to-back packets without idle gap."""

import cocotb

from axi4_stream_driver import PacketMonitorTB, check_equal, expect_counts, expect_idle


@cocotb.test()
async def test_back_to_back(dut):
    tb = PacketMonitorTB(dut)
    await tb.setup()

    pkt1_header = 0xCAFE0001
    pkt2_header = 0xCAFE0002

    pkt1 = [
        (pkt1_header, 0b1111, False),
        (0xAAAAAAAA, 0b1100, True),
    ]
    pkt2 = [
        (pkt2_header, 0b1111, False),
        (0xBBBBBBBB, 0b1111, False),
        (0xCCCCCCCC, 0b0011, True),
    ]

    expected_bytes = 4 + 2 + 4 + 4 + 2  # 16

    header_valid_pulses = 0
    captured_headers = []

    async def drive_and_track(beats):
        nonlocal header_valid_pulses
        for tdata, tkeep, tlast in beats:
            sample = await tb.drive_beat(tdata, tkeep, tlast)
            if sample["header_valid"]:
                header_valid_pulses += 1
                captured_headers.append(sample["header_capture"])

    await drive_and_track(pkt1)
    await drive_and_track(pkt2)

    await expect_counts(tb, packets=2, bytes_=expected_bytes)
    check_equal(header_valid_pulses, 2, "header_valid pulse count")
    check_equal(captured_headers, [pkt1_header, pkt2_header], "captured headers")

    await tb.idle_cycles(2)
    await expect_idle(tb)

    dut._log.info("Back-to-back test passed")
