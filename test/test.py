# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # async reset: counter should be 0
    assert int(dut.uo_out.value) == 0

    # sync load: put value in uio_in and assert load_en
    load_value = 0x3C
    dut.uio_in.value = load_value
    dut.ui_in.value = 0b1000_0000 # [7] == 1 => load_en enabled
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    assert int(dut.uo_out.value) == load_value # output should be loaded value

    # enable counting
    dut.ui_in.value = 0b0100_0000  # [6] == 1 => count_en enabled
    await ClockCycles(dut.clk, 3)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    assert int(dut.uo_out.value) == (load_value + 3) & 0xFF # output should be loaded value + 3

    # tri-state control
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    assert int(dut.uio_oe.value) == 0x00 # uio_oe should be 0
    dut.ui_in.value = 0b0000_0001 # [0] == 1 => tri_en enabled
    await ClockCycles(dut.clk, 1)
    assert int(dut.uio_oe.value) == 0xFF # uio_oe should be 1
