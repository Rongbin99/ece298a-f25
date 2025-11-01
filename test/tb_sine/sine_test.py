import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

HALF_STEP_RATIO = pow(2, 1/12)

subsample_phase = 0

async def inc_subsample_phase(dut, inc):
    global subsample_phase

    for _ in range(inc):
        subsample_phase = (subsample_phase + 1) % 256
        dut.subsample_phase.value = subsample_phase
        await ClockCycles(dut.clk, 1)

def calculate_step(freq_hz):
    sample_rate = 28160
    return round((freq_hz * (2 ** 14)) / sample_rate)

# test reset
# test

@cocotb.test()
async def test_project(dut):
    global subsample_phase

    dut._log.info("Start")

    # approx 7208960 Hz
    clock = Clock(dut.clk, 139, units="ns")
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

    await inc_subsample_phase(dut, 254)
    
    dut._log.info("Starting 0 Hz sample")
    await inc_subsample_phase(dut, 1 + 7)
    assert dut.out.value == 64, f"Expected 64, got {dut.out.value.integer}"
    await inc_subsample_phase(dut, 254-7)

    dut._log.info("Starting 400 Hz tone")
    dut.freq_increment.value = calculate_step(400)
    await inc_subsample_phase(dut, 256*300)