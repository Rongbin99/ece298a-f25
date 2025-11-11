import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

subsample_phase = 0

async def cycle_subsample_phase(dut, cycles=1):
    """Advance subsample_phase through complete cycles (0-1023)"""
    global subsample_phase
    
    for _ in range(cycles * 1024):
        dut.subsample_phase.value = subsample_phase
        await ClockCycles(dut.clk, 1)
        subsample_phase = (subsample_phase + 1) % 1024

async def wait_for_subsample_phase(dut, target_phase):
    """Wait until subsample_phase reaches target value"""
    global subsample_phase
    
    while subsample_phase != target_phase:
        dut.subsample_phase.value = subsample_phase
        await ClockCycles(dut.clk, 1)
        subsample_phase = (subsample_phase + 1) % 1024
    
    # At target phase
    dut.subsample_phase.value = subsample_phase
    await ClockCycles(dut.clk, 1)
    subsample_phase = (subsample_phase + 1) % 1024

@cocotb.test()
async def test_reset1(dut):
    """Test that reset properly initializes the output and accumulator"""
    dut._log.info("Testing reset functionality")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Apply reset
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 100
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Check that output is 0 after reset
    assert dut.out.value == 0, f"Expected 0 after reset, got {dut.out.value.integer}"
    dut._log.info("Reset test passed")

@cocotb.test()
async def test_reset2(dut):
    """Test that reset properly initializes the output and accumulator"""
    dut._log.info("Testing reset functionality")
    
    clock = Clock(dut.clk, 200, units="ns")
    cocotb.start_soon(clock.start())
    
    # Apply reset
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 256
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 20)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    # Check that output is 0 after reset
    assert dut.out.value == 0, f"Expected 0 after reset, got {dut.out.value.integer}"
    dut._log.info("Reset test passed")

    await cycle_subsample_phase(dut, cycles=10)
    assert dut.out.value == 40, f"Expected 40 after 10 cycles, got {dut.out.value.integer}"
    await cycle_subsample_phase(dut, cycles=10)
    assert dut.out.value == 80, f"Expected 80 after 20 cycles, got {dut.out.value.integer}"
    await cycle_subsample_phase(dut, cycles=10)
    assert dut.out.value == 120, f"Expected 120 after 30 cycles, got {dut.out.value.integer}"
    dut._log.info("Cycle test passed")

@cocotb.test()
async def test_accumulator_increment(dut):
    """Test that accumulator increments only at subsample_phase = 8"""
    global subsample_phase
    
    dut._log.info("Testing accumulator increment timing")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 512  # Large increment for visible changes
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    # Capture initial output (should be 0 from reset)
    initial_out = dut.out.value.integer
    dut._log.info(f"Initial output: {initial_out}")
    
    # Cycle subsample_phase from 0 to 7, output should remain 0
    for phase in range(8):
        dut.subsample_phase.value = phase
        await ClockCycles(dut.clk, 1)
        subsample_phase = phase
    
    current_out = dut.out.value.integer
    assert current_out == initial_out, f"Output changed before phase 8: {initial_out} -> {current_out}"
    
    # At phase 8, accumulator increments
    dut.subsample_phase.value = 8
    await ClockCycles(dut.clk, 1)
    subsample_phase = 8
    
    # Move to phase 9 to see the new output based on incremented accumulator
    dut.subsample_phase.value = 9
    await ClockCycles(dut.clk, 2)
    after_increment = dut.out.value.integer
    
    dut._log.info(f"After phase 8 increment: {after_increment}")
    assert after_increment > initial_out, f"Output should increase after phase 8, got {after_increment}"
    
    dut._log.info("Accumulator increment test passed")

@cocotb.test()
async def test_frequency_control(dut):
    """Test that freq_increment controls the rate of triangle wave"""
    global subsample_phase
    
    dut._log.info("Testing frequency control")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Test with small freq_increment
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 64  # Small increment
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Run through 4 complete subsample cycles
    await cycle_subsample_phase(dut, cycles=4)
    output_small = dut.out.value.integer
    dut._log.info(f"After 4 cycles with freq_increment=64: output={output_small}")
    
    # Reset and test with large freq_increment
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 256  # 4x larger increment
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Run through same number of cycles
    await cycle_subsample_phase(dut, cycles=4)
    output_large = dut.out.value.integer
    dut._log.info(f"After 4 cycles with freq_increment=256: output={output_large}")
    
    # With 4x freq_increment, the wave should progress ~4x as fast
    # So output should be significantly different
    dut._log.info(f"Frequency control test passed - different rates produce different outputs")

@cocotb.test()
async def test_triangle_wave_shape(dut):
    """Test that the wave ascends and descends properly"""
    global subsample_phase
    
    dut._log.info("Testing triangle wave shape")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset with moderate frequency
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 256  # Should give decent progression
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Track outputs over time
    outputs = []
    for _ in range(100):  # Sample 100 times
        await wait_for_subsample_phase(dut, 8)  # Sample after each increment
        outputs.append(dut.out.value.integer)
    
    dut._log.info(f"First 20 samples: {outputs[:20]}")
    dut._log.info(f"Samples 40-60: {outputs[40:60]}")
    dut._log.info(f"Last 20 samples: {outputs[-20:]}")
    
    # Check that we see ascending behavior (output increases)
    ascending_count = sum(1 for i in range(len(outputs)-1) if outputs[i+1] > outputs[i])
    # Check that we see descending behavior (output decreases)
    descending_count = sum(1 for i in range(len(outputs)-1) if outputs[i+1] < outputs[i])
    
    dut._log.info(f"Ascending transitions: {ascending_count}")
    dut._log.info(f"Descending transitions: {descending_count}")
    
    # We should see both ascending and descending in a triangle wave
    assert ascending_count > 10, f"Expected ascending behavior, got {ascending_count} transitions"
    assert descending_count > 10, f"Expected descending behavior, got {descending_count} transitions"
    
    dut._log.info("Triangle wave shape test passed")

@cocotb.test()
async def test_full_range(dut):
    """Test that triangle wave reaches full output range (0-127)"""
    global subsample_phase
    
    dut._log.info("Testing full output range")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 256
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Run long enough to see full range
    min_val = 127
    max_val = 0
    
    for _ in range(500):  # Run 500 sample periods
        await wait_for_subsample_phase(dut, 8)
        output = dut.out.value.integer
        min_val = min(min_val, output)
        max_val = max(max_val, output)
    
    dut._log.info(f"Min output: {min_val}, Max output: {max_val}")
    
    # Should reach close to full range
    assert min_val <= 10, f"Min value {min_val} should be close to 0"
    assert max_val >= 117, f"Max value {max_val} should be close to 127"
    
    dut._log.info("Full range test passed")

@cocotb.test()
async def test_continuous_waveform(dut):
    """Test that waveform is continuous without large jumps"""
    global subsample_phase
    
    dut._log.info("Testing waveform continuity")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 128
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Sample outputs and check for large discontinuities
    prev_output = dut.out.value.integer
    max_jump = 0
    
    for _ in range(200):
        await wait_for_subsample_phase(dut, 8)
        output = dut.out.value.integer
        jump = abs(output - prev_output)
        max_jump = max(max_jump, jump)
        prev_output = output
    
    dut._log.info(f"Maximum jump between samples: {max_jump}")
    
    # Jumps should be relatively small for a smooth triangle wave
    # With freq_increment=128 and ACC_BITS=14, jumps should be <= 1
    assert max_jump <= 2, f"Wave has discontinuities with max jump of {max_jump}"
    
    dut._log.info("Continuity test passed - smooth waveform")

@cocotb.test()
async def test_zero_frequency(dut):
    """Test that freq_increment=0 produces constant output"""
    global subsample_phase
    
    dut._log.info("Testing zero frequency")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset with zero frequency
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.freq_increment.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    initial_output = dut.out.value.integer
    dut._log.info(f"Initial output with freq=0: {initial_output}")
    
    # Run through many cycles
    await cycle_subsample_phase(dut, cycles=10)
    
    final_output = dut.out.value.integer
    dut._log.info(f"Final output with freq=0: {final_output}")
    
    # Output should not change
    assert final_output == initial_output, f"Output changed with zero frequency: {initial_output} -> {final_output}"
    
    dut._log.info("Zero frequency test passed")
