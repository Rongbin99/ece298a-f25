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

# values closer to 64 are more noisy by nature of the CORDIC algorithm
SAMPLE_TOLERANCE_LOW = 3
SAMPLE_TOLERANCE_HIGH = 9

SAMPLE_FREQ = 28160  # Hz

subsample_phase = 0

async def test_setup(dut):
    global subsample_phase

    # approx 28835840 Hz
    clock = Clock(dut.clk, PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    subsample_phase = 0
    dut._log.info("Reset")
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut._log.info("Reset complete")

async def inc_subsample_phase(dut, inc):
    global subsample_phase

    for _ in range(inc):
        subsample_phase = (subsample_phase + 1) % 1024
        dut.subsample_phase.value = subsample_phase
        await ClockCycles(dut.clk, 1)

@cocotb.test()
async def test_sine_reset(dut):
    global subsample_phase
    await test_setup(dut)

    dut._log.info("Starting 440 Hz sine wave")
    dut.freq_increment.value = calculate_step(440)
    await inc_subsample_phase(dut, 500)

    dut._log.info("Reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut._log.info("Reset complete")

    await ClockCycles(dut.clk, 1)
    assert dut.out.value == 64, f"Expected 64, got {dut.out.value.integer}"

@cocotb.test()
async def test_random_frequencies(dut):
    global subsample_phase
    await test_setup(dut)

    # get to start of first cordic cycle
    await inc_subsample_phase(dut, 1022)
    
    dut._log.info("Starting 0 Hz sine wave")
    await inc_subsample_phase(dut, 1 + 7)
    assert dut.out.value == 64, f"Expected 64, got {dut.out.value.integer}"

    subsample_phase = 7 # accumulator increments on s_p = 8
    dut.subsample_phase.value = subsample_phase

    phase = 0
    freq_list = list(range(221, 1760))
    # test random frequencies between 220 and 1760 Hz (intended range)
    for freq in random.sample(freq_list, k=10) + [220, 1760]:
        dut._log.info(f"Starting {freq} Hz sine wave")
        dut.freq_increment.value = calculate_step(freq)
        await inc_subsample_phase(dut, 3)

        # play 100 samples of each frequency
        for sample_num in range(100):
            expected = int(64 + 63 * math.sin(phase))
            # print(f"Freq {freq} Hz, Sample {sample_num}: Expected {expected}, got {dut.out.value.integer}")
            tolerance = round(abs(expected - 64) / 63 * (SAMPLE_TOLERANCE_LOW - SAMPLE_TOLERANCE_HIGH) + SAMPLE_TOLERANCE_HIGH)
            assert abs(int(dut.out.value) - expected) <= tolerance, \
                f"Freq {freq} Hz, Sample {sample_num}: Expected {expected}, got {dut.out.value.integer}"

            if sample_num == 99:
                await inc_subsample_phase(dut, 1024 - 3)
            else:
                await inc_subsample_phase(dut, 1024)
            phase += 2 * math.pi * freq / SAMPLE_FREQ

@cocotb.test()
async def test_silence(dut):
    global subsample_phase
    await test_setup(dut)

    # get to start of first cordic cycle
    await inc_subsample_phase(dut, 1022)
    
    dut._log.info("Starting 0 Hz sine wave")
    await inc_subsample_phase(dut, 1 + 7)
    assert dut.out.value == 64, f"Expected 64, got {dut.out.value.integer}"

    subsample_phase = 7 # accumulator increments on s_p = 8
    dut.subsample_phase.value = subsample_phase

    phase = 0

    freq = 220
    dut._log.info(f"Starting {freq} Hz sine wave")
    dut.freq_increment.value = calculate_step(freq)
    await inc_subsample_phase(dut, 3)

    # play 50 samples
    for sample_num in range(50):
        expected = int(64 + 63 * math.sin(phase))
        # print(f"Freq {freq} Hz, Sample {sample_num}: Expected {expected}, got {dut.out.value.integer}")
        tolerance = round(abs(expected - 64) / 63 * (SAMPLE_TOLERANCE_LOW - SAMPLE_TOLERANCE_HIGH) + SAMPLE_TOLERANCE_HIGH)
        assert abs(int(dut.out.value) - expected) <= tolerance, \
            f"Freq {freq} Hz, Sample {sample_num}: Expected {expected}, got {dut.out.value.integer}"

        if sample_num == 49:
            await inc_subsample_phase(dut, 1024 - 3)
        else:
            await inc_subsample_phase(dut, 1024)
        phase += 2 * math.pi * freq / SAMPLE_FREQ

    freq = 0
    dut._log.info(f"Starting silence")
    dut.freq_increment.value = calculate_step(freq)
    await inc_subsample_phase(dut, 3)

    expected_silence = int(dut.out.value)
    await inc_subsample_phase(dut, 1024)

    # play 50 samples
    for sample_num in range(50):
        assert int(dut.out.value) == expected_silence, \
            f"Silence, Sample {sample_num}: Expected {expected_silence}, got {dut.out.value.integer}"

        if sample_num == 49:
            await inc_subsample_phase(dut, 1024 - 3)
        else:
            await inc_subsample_phase(dut, 1024)