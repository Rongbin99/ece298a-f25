import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Edge, Timer
from audio_util import *

PERIOD_NS = 35

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
    # sim takes about 1s per ms without vcd dumping

    dut._log.info("Start")

    # approx 28835840 Hz
    clock = Clock(dut.clk, PERIOD_NS, units="ns")
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
    write_data = []

    delay_s = await write_reg(dut, tostep(60), 0) # c4 ~262
    delay_s += await write_reg(dut, tostep(64), 1) # e4 ~330

    await Timer(0.005 - delay_s, units="sec")

    delay_s = await write_reg(dut, tostep(72), 0)
    delay_s += await write_reg(dut, 0, 1)

    await Timer(0.005 - delay_s, units="sec")
    
    with open("pwm_edges.log", "w") as f:
        for (time_ns, value) in write_data:
            f.write(f"{time_ns},{value}\n")

@cocotb.test()
async def single_sine_note(dut):
    """Full integration test: single sine channel active."""

    dut._log.info("Start single_sine_note")

    # approx 28835840 Hz
    clock = Clock(dut.clk, PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Single sine channel integration test")

    # Enable only the sine channel on register 0 (A4)
    await write_reg(dut, tostep(69), 0)
    await write_reg(dut, 0, 1)

    await Timer(0.003, units="sec")

@cocotb.test()
async def single_triangle_note(dut):
    """Full integration test: single triangle channel active."""

    dut._log.info("Start single_triangle_note")

    # approx 28835840 Hz
    clock = Clock(dut.clk, PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Single triangle channel integration test")

    # Enable only the triangle channel on register 1 (A3)
    await write_reg(dut, 0, 0)
    await write_reg(dut, tostep(57), 1)

    await Timer(0.003, units="sec")

@cocotb.test()
async def sine_and_triangle_together(dut):
    """Full integration test: sine and triangle channels active together."""

    dut._log.info("Start sine_and_triangle_together")

    # approx 28835840 Hz
    clock = Clock(dut.clk, PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Sine + triangle integration test")

    # Program both channels: sine A4 and triangle A3
    await write_reg(dut, tostep(69), 0)
    await write_reg(dut, tostep(57), 1)

    await Timer(0.003, units="sec")
    