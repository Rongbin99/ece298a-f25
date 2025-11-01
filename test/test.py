# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from audio_util import *

PERIOD_NS = 139

async def write_reg(dut, value, addr, delay=5):
    # setup phase 1 & MSB
    dut.ui_in.value = (addr & 0xF) | (1 << 4) | (0 << 5)
    dut.uio_in.value = value >> 8
    await ClockCycles(dut.clk, delay)

    # enable, writes MSB
    dut.ui_in.value = (addr & 0xF) | (1 << 4) | (1 << 5)
    await ClockCycles(dut.clk, delay)

    # setup LSB
    dut.uio_in.value = value & 0xFF
    await ClockCycles(dut.clk, delay)

    # phase 0, writes LSB
    dut.ui_in.value = (addr & 0xF) | (0 << 4) | (1 << 5)
    await ClockCycles(dut.clk, delay)

    # disable, writes final value to reg
    dut.ui_in.value = (addr & 0xF) | (0 << 4) | (0 << 5)
    await ClockCycles(dut.clk, delay)

    dut.uio_in.value = 0
    dut.ui_in.value = 0

    return delay * PERIOD_NS * 4 / 1e9

def seconds_to_cycles(seconds):
    return int(seconds * 1e9 / PERIOD_NS)

@cocotb.test()
async def play_a_tune(dut):
    dut._log.info("Start")

    # approx 7208960 Hz
    clock = Clock(dut.clk, PERIOD_NS, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Full integration test")

    delay_s = await write_reg(dut, tostep(69), 0)
    delay_s += await write_reg(dut, tostep(69), 1)
    await ClockCycles(dut.clk, seconds_to_cycles(0.01 - delay_s))

    delay_s = await write_reg(dut, tostep(100), 0)
    delay_s += await write_reg(dut, tostep(100), 1)
    await ClockCycles(dut.clk, seconds_to_cycles(0.01 - delay_s))