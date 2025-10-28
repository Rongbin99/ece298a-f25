import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

subsample_phase = 0

## some generated tests for the triangle wave

async def inc_subsample_phase(dut, inc):
    """Increment the subsample phase and wait for clock cycles"""
    global subsample_phase
    
    for _ in range(inc):
        subsample_phase = (subsample_phase + 1) % 256
        dut.subsample_phase.value = subsample_phase
        await ClockCycles(dut.clk, 1)

async def set_phase_and_wait(dut, phase):
    """Set phase to specific value and wait for output to update"""
    global subsample_phase
    subsample_phase = phase
    dut.subsample_phase.value = phase
    await ClockCycles(dut.clk, 2)  # Wait 2 cycles: 1 to latch input, 1 to read output

@cocotb.test()
async def test_reset(dut):
    """Test that reset properly initializes the output"""
    dut._log.info("Testing reset functionality")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Apply reset
    dut.subsample_phase.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)  # Wait for output to stabilize
    
    # Check that output is 0 after reset
    assert dut.out.value == 0, f"Expected 0 after reset, got {dut.out.value.integer}"
    dut._log.info("Reset test passed")

@cocotb.test()
async def test_ascending_ramp(dut):
    """Test the ascending portion of the triangle wave (phase 0-127)"""
    global subsample_phase
    
    dut._log.info("Testing ascending ramp (phase 0-127)")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Test key points in ascending ramp
    test_points = [0, 1, 32, 64, 100, 127]
    
    for phase in test_points:
        await set_phase_and_wait(dut, phase)
        expected = phase  # Output should equal phase in ascending portion
        actual = dut.out.value.integer
        assert actual == expected, f"Phase {phase}: Expected {expected}, got {actual}"
        dut._log.info(f"Phase {phase}: Output = {actual} ✓")
    
    dut._log.info("Ascending ramp test passed")

@cocotb.test()
async def test_descending_ramp(dut):
    """Test the descending portion of the triangle wave (phase 128-255)"""
    global subsample_phase
    
    dut._log.info("Testing descending ramp (phase 128-255)")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Test key points in descending ramp
    test_cases = [
        (128, 127),  # phase 128 -> output 127 (peak)
        (129, 126),  # phase 129 -> output 126
        (192, 63),   # phase 192 -> output 63 (midpoint)
        (224, 31),   # phase 224 -> output 31
        (255, 0),    # phase 255 -> output 0 (trough)
    ]
    
    for phase, expected in test_cases:
        await set_phase_and_wait(dut, phase)
        actual = dut.out.value.integer
        assert actual == expected, f"Phase {phase}: Expected {expected}, got {actual}"
        dut._log.info(f"Phase {phase}: Output = {actual} ✓")
    
    dut._log.info("Descending ramp test passed")

@cocotb.test()
async def test_full_cycle(dut):
    """Test a complete triangle wave cycle (phase 0-255)"""
    global subsample_phase
    
    dut._log.info("Testing full triangle wave cycle")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    subsample_phase = 0
    dut.subsample_phase.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    # Test every value in a full cycle
    errors = []
    for phase in range(256):
        dut.subsample_phase.value = phase
        await ClockCycles(dut.clk, 2)  # Wait for output to update
        
        # Calculate expected value
        if phase < 128:
            expected = phase  # Ascending
        else:
            expected = 255 - phase  # Descending (inverted)
        
        actual = dut.out.value.integer
        
        if actual != expected:
            errors.append(f"Phase {phase}: Expected {expected}, got {actual}")
    
    # Report results
    if errors:
        dut._log.error(f"Found {len(errors)} errors in full cycle test")
        for error in errors[:10]:  # Show first 10 errors
            dut._log.error(error)
        assert False, f"Full cycle test failed with {len(errors)} errors"
    else:
        dut._log.info("Full cycle test passed - all 256 phases correct!")

@cocotb.test()
async def test_peak_continuity(dut):
    """Test that the triangle wave is continuous at the peak (phase 127-128)"""
    global subsample_phase
    
    dut._log.info("Testing peak continuity")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.subsample_phase.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Test around the peak
    await set_phase_and_wait(dut, 126)
    out_126 = dut.out.value.integer
    
    await set_phase_and_wait(dut, 127)
    out_127 = dut.out.value.integer
    
    await set_phase_and_wait(dut, 128)
    out_128 = dut.out.value.integer
    
    await set_phase_and_wait(dut, 129)
    out_129 = dut.out.value.integer
    
    dut._log.info(f"Phase 126: {out_126}, Phase 127: {out_127}, Phase 128: {out_128}, Phase 129: {out_129}")
    
    # Check values are as expected
    assert out_126 == 126, f"Expected 126, got {out_126}"
    assert out_127 == 127, f"Expected 127 at peak, got {out_127}"
    assert out_128 == 127, f"Expected 127 at peak, got {out_128}"
    assert out_129 == 126, f"Expected 126, got {out_129}"
    
    dut._log.info("Peak continuity test passed - smooth transition at peak!")

@cocotb.test()
async def test_trough_continuity(dut):
    """Test that the triangle wave is continuous at the trough (phase 255->0)"""
    global subsample_phase
    
    dut._log.info("Testing trough continuity")
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.subsample_phase.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Test around the trough
    await set_phase_and_wait(dut, 254)
    out_254 = dut.out.value.integer
    
    await set_phase_and_wait(dut, 255)
    out_255 = dut.out.value.integer
    
    await set_phase_and_wait(dut, 0)
    out_0 = dut.out.value.integer
    
    await set_phase_and_wait(dut, 1)
    out_1 = dut.out.value.integer
    
    dut._log.info(f"Phase 254: {out_254}, Phase 255: {out_255}, Phase 0: {out_0}, Phase 1: {out_1}")
    
    # Check values are as expected
    assert out_254 == 1, f"Expected 1, got {out_254}"
    assert out_255 == 0, f"Expected 0 at trough, got {out_255}"
    assert out_0 == 0, f"Expected 0 at trough, got {out_0}"
    assert out_1 == 1, f"Expected 1, got {out_1}"
    
    dut._log.info("Trough continuity test passed - smooth transition at trough!")
