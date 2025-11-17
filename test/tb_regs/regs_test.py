import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audio_util import *

import math
import random

PERIOD_NS = 35

async def write_reg(dut, value, addr, delay=5):
    # setup phase 1 & MSB
    dut.phase.value = 1
    dut.address.value = addr & 0xF
    dut.reg_value.value = value >> 8
    await ClockCycles(dut.clk, delay)

    # enable, writes MSB
    dut.enable.value = 1
    await ClockCycles(dut.clk, delay)

    # setup LSB
    dut.reg_value.value = value & 0xFF
    await ClockCycles(dut.clk, delay)

    # phase 0, writes LSB
    dut.phase.value = 0
    await ClockCycles(dut.clk, delay)

    # disable, writes final value to reg
    dut.enable.value = 0
    await ClockCycles(dut.clk, delay)

    dut.address.value = 0
    dut.reg_value.value = 0

    return delay * PERIOD_NS * 4 / 1e9

async def test_setup(dut):
    global subsample_phase

    # approx 28835840 Hz
    clock = Clock(dut.clk, PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.enable.value = 0
    dut.phase.value = 0
    dut.address.value = 0
    dut.reg_value.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut._log.info("Reset complete")

@cocotb.test()
async def test_regs_reset(dut):
    await test_setup(dut)

    await write_reg(dut, 0x1234, 0)
    await write_reg(dut, 0xABCD, 1)

    dut._log.info("Reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut._log.info("Reset complete")

    await ClockCycles(dut.clk, 1)
    assert int(dut.registers_flat.value) == 0, f"Expected 0, got {int(dut.registers_flat.value)}"

@cocotb.test()
async def test_regs_mid_transaction_reset(dut):
    """Reset during an in-progress write transaction clears state and registers."""
    await test_setup(dut)

    # Begin a write to register 0 but reset before it can complete
    dut._log.info("Starting mid-transaction write then resetting")
    dut.phase.value = 1
    dut.address.value = 0
    dut.reg_value.value = 0xAA
    dut.enable.value = 1
    await ClockCycles(dut.clk, 2)

    # Assert reset while enable is high and FSM not yet finished
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # All registers should be cleared and no partial write should persist
    assert int(dut.registers_flat.value) == 0, f"Expected registers cleared after mid-transaction reset, got {int(dut.registers_flat.value)}"

@cocotb.test()
async def test_regs_double_write(dut):
    await test_setup(dut)

    for reg in range(2):
        await write_reg(dut, 0x1234, reg)
        await write_reg(dut, 0x5678, reg)

        await ClockCycles(dut.clk, 1)
        flat = int(dut.registers_flat.value)
        assert ((flat >> (reg * 16)) & 0xFFFF) == 0x5678, f"Expected 0x5678, got {flat:#06x}"

@cocotb.test()
async def test_regs_timing(dut):
    await test_setup(dut)

    # 2-stage ff sync for enable and phase so delay must be at least 3 clk cycles
    for time_delay in [50000, 1000, 100, 10, 4, 3]:
    # for time_delay in [1000, 100, 10, 4, 3]:
        dut._log.info(f"Testing with time delay: {time_delay}")
        for reg in range(2):
            reg_value = random.randint(0, 0xFFFF)
            await write_reg(dut, reg_value, reg, delay=time_delay)
            await ClockCycles(dut.clk, 1)
            flat = int(dut.registers_flat.value)
            assert ((flat >> (reg * 16)) & 0xFFFF) == reg_value,f"Expected {reg_value}, got {flat:#06x}"

@cocotb.test()
async def test_regs_extreme_values(dut):
    """Write extreme 16-bit values to each register and verify storage."""
    await test_setup(dut)

    patterns = [0x0000, 0xFFFF, 0x8000, 0x7FFF, 0x00FF, 0xFF00]
    for reg in range(2):
        for value in patterns:
            dut._log.info(f"Writing value 0x{value:04X} to reg {reg}")
            await write_reg(dut, value, reg)
            await ClockCycles(dut.clk, 1)
            flat = int(dut.registers_flat.value)
            read_back = (flat >> (reg * 16)) & 0xFFFF
            assert read_back == value, f"Extreme-value mismatch on reg{reg}: wrote 0x{value:04X}, read 0x{read_back:04X}"

@cocotb.test()
async def test_regs_error_states(dut):
    for reg in range(2):
        await test_setup(dut)
        dut._log.info("Test case: phase = 0, enable rising edge")
        dut.address.value = reg
        dut.reg_value.value = 0xFF
        dut.phase.value = 0
        dut.enable.value = 0
        await ClockCycles(dut.clk, 5)

        dut.enable.value = 1
        await ClockCycles(dut.clk, 5)
        assert dut.registers_flat.value == 0, "Expected no reg write"

        # reset to state 0
        dut.enable.value = 0
        await ClockCycles(dut.clk, 5)
        assert dut.registers_flat.value == 0, "Expected no reg write"

        await write_reg(dut, 0x1234, reg)
        flat = int(dut.registers_flat.value)
        assert ((flat >> (reg * 16)) & 0xFFFF) == 0x1234, "Expected reg write"
        
        await test_setup(dut)
        dut._log.info("Test case: phase = 1, enable falling edge")
        dut.address.value = reg
        dut.reg_value.value = 0xFF
        dut.phase.value = 1
        dut.enable.value = 0
        await ClockCycles(dut.clk, 5)

        dut.enable.value = 1
        await ClockCycles(dut.clk, 5)

        # should already be reset to state 0
        dut.enable.value = 0
        await ClockCycles(dut.clk, 5)
        assert dut.registers_flat.value == 0, "Expected no reg write"

        await write_reg(dut, 0x1234, reg)
        flat = int(dut.registers_flat.value)
        assert ((flat >> (reg * 16)) & 0xFFFF) == 0x1234, "Expected reg write"
        
        await test_setup(dut)
        dut._log.info("Test case: enabled = 1, phase rising edge")
        dut.address.value = reg
        dut.reg_value.value = 0xFF
        dut.phase.value = 1
        dut.enable.value = 0
        await ClockCycles(dut.clk, 5)

        dut.enable.value = 1
        await ClockCycles(dut.clk, 5)

        dut.phase.value = 0
        await ClockCycles(dut.clk, 5)

        dut.phase.value = 1
        await ClockCycles(dut.clk, 5)
        assert dut.registers_flat.value == 0, "Expected no reg write"

        # reset to state 0
        dut.enable.value = 0
        await ClockCycles(dut.clk, 5)
        assert dut.registers_flat.value == 0, "Expected no reg write"

        await write_reg(dut, 0x1234, reg)
        flat = int(dut.registers_flat.value)
        assert ((flat >> (reg * 16)) & 0xFFFF) == 0x1234, "Expected reg write"
    
@cocotb.test()
async def test_regs_large_addresses(dut):
    await test_setup(dut)

    for reg in range(2, 15):
        await write_reg(dut, 0x1234, reg)
        await ClockCycles(dut.clk, 1)
        assert int(dut.registers_flat.value) == 0, f"Expected 0, got {int(dut.registers_flat.value)}"

@cocotb.test()
async def test_regs_address_boundary_and_no_clobber(dut):
    """Addresses at and beyond NUM_REGS do not clobber lower registers."""
    await test_setup(dut)

    # Seed valid registers with known data
    await write_reg(dut, 0xAAAA, 0)
    await write_reg(dut, 0x5555, 1)
    await ClockCycles(dut.clk, 1)

    # Write to highest possible address within 4-bit range; should be ignored
    for addr in [2, 3, 7, 15]:
        dut._log.info(f"Attempting write to out-of-range addr {addr}")
        await write_reg(dut, 0xDEAD, addr)

    await ClockCycles(dut.clk, 1)

    flat = int(dut.registers_flat.value)
    reg0 = (flat >> 0) & 0xFFFF
    reg1 = (flat >> 16) & 0xFFFF

    assert reg0 == 0xAAAA, f"Reg0 clobbered by out-of-range writes: got 0x{reg0:04X}"
    assert reg1 == 0x5555, f"Reg1 clobbered by out-of-range writes: got 0x{reg1:04X}"
