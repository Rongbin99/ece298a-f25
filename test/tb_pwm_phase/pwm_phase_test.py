import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, ReadOnly

import random

PERIOD_NS = 35

async def test_setup(dut):
    """Start clock and reset DUT; initialize inputs."""
    clock = Clock(dut.clk, PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    dut.bitstream_ch1.value = 0
    dut.bitstream_ch2.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 20)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # Check that output is 0 after reset
    assert dut.pwm_out.value == 0, f"Expected 0, got {dut.pwm_out.value.integer}"
    dut._log.info("Reset test passed")

async def wait_for_low8(dut, target: int):
    """Wait until subsample_phase[7:0] == target."""
    while (dut.subsample_phase.value.integer & 0xFF) != (target & 0xFF):
        await ClockCycles(dut.clk, 1)
    # aligned exactly at the matching phase edge
    return

@cocotb.test()
async def test_phase_counter_counts_and_wraps(dut):
    """phase_counter: after reset -> 0; increments each clk; wraps at 1024."""
    await test_setup(dut)

    # After reset, should be 0
    assert dut.subsample_phase.value.integer == 0, f"Expected subsample_phase=0 after reset, got {dut.subsample_phase.value.integer}"

    # After N cycles, value should equal N (mod 1024)
    N = random.randint(0, 1023)
    dut._log.info(f"Testing phase counter with {N} cycles")
    await ClockCycles(dut.clk, N)
    assert dut.subsample_phase.value.integer == (N % 1024), f"Expected {N % 1024}, got {dut.subsample_phase.value.integer}"

    # Advance to wrap to 0
    current = dut.subsample_phase.value.integer
    dut._log.info(f"Current phase: {current}")
    to_wrap = 1024 - current
    await ClockCycles(dut.clk, to_wrap)
    assert dut.subsample_phase.value.integer == 0, f"Expected wrap to 0, got {dut.subsample_phase.value.integer}"

@cocotb.test()
async def test_pwm_duty_matches_sample_sum(dut):
    """pwm: duty over a 256-cycle period == bitstream_ch1 + bitstream_ch2."""
    await test_setup(dut)

    # A range of test vectors covering min/mid/max
    test_vectors = [
        (0, 0),
        (10, 5),
        (50, 20),
        (127, 0),
        (100, 100),
        (127, 127), # max sum = 254 (max 8-bit value)
    ]

    for ch1, ch2 in test_vectors:
        dut._log.info(f"Testing with ch1={ch1}, ch2={ch2}")
        dut.bitstream_ch1.value = ch1
        dut.bitstream_ch2.value = ch2

        # aligned exactly at the matching phase edge
        await wait_for_low8(dut, 0)
        # Wait two cycles: one for PWM to observe phase==0, one for comparator to use new sample
        await ClockCycles(dut.clk, 2)

        # count highs over exactly one PWM period (256 cycles, starting at phase==0)
        highs = 0
        for _ in range(256): # 0-255
            await ReadOnly()
            if dut.pwm_out.value.integer == 1:
                highs += 1
            await ClockCycles(dut.clk, 1)

        expected = ch1 + ch2 # 7b + 7b -> [0..254] (max 8-bit value)
        assert highs == expected, f"Duty mismatch: expected {expected} highs, got {highs} (ch1={ch1}, ch2={ch2})"

@cocotb.test()
async def test_pwm_phase_threshold_behavior(dut):
    """pwm: within a period, pwm_out=1 iff subsample_phase < current_sample."""
    await test_setup(dut)

    # test 256 random samples
    for _ in range(256):
        sample = random.randint(0, 255) & 0xFF
        # splits the random test_sample into two 7-bit values for ch1 and ch2
        ch1 = min(sample, 127)
        ch2 = sample - ch1
        ch2 = min(max(ch2, 0), 127)
        dut.bitstream_ch1.value = ch1
        dut.bitstream_ch2.value = ch2

        # wait until phase 255, then advance to phase 0 where sample gets captured
        await wait_for_low8(dut, 255)
        # advance to phase 0 - current_sample gets latched on this edge
        await ClockCycles(dut.clk, 1)
        # advance to phase 1 - pwm_out now reflects comparison with phase 0
        await ClockCycles(dut.clk, 1)
        
        # walk through PWM period and check threshold behavior
        # start at phase 2 (due to the 2-cycle wait) and check through phase 254 (253 phases total)
        # phase 255 wraps to 0 where the sample is recaptured
        # pwm_out lags by one cycle: at phase X, pwm_out reflects the comparison from phase (X-1)
        for _ in range(253):
            await ReadOnly()
            subsample_phase = dut.subsample_phase.value.integer & 0xFF
            
            # pwm_out reflects comparison from previous cycle
            prev_phase = (subsample_phase - 1) & 0xFF
            expected_out = 1 if prev_phase < sample else 0
            
            assert dut.pwm_out.value.integer == expected_out, \
                f"At phase {subsample_phase} with sample {sample}: expected pwm_out={expected_out}, got {dut.pwm_out.value.integer} (based on prev_phase={prev_phase})"
            
            await ClockCycles(dut.clk, 1)
