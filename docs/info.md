<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

2-channel sine/triangle wave sound chip with 8-bit PWM output.

Two 16-bit registers, written to through a parallel bus interface, control the frequencies of channel 1 (sine) and channel 2 (triangle). Register values go to sine and triangle wave modules which use Direct Digital Synthesis (DDS) to generate 7-bit digital samples at varying frequencies with a sample rate of 28160 Hz. The 7-bit values are added together to an 8-bit sample which is converted to a PWM signal. Each 8-bit sample is converted to four 112640 Hz PWM pulses. The base clock is thus 256x the PWM frequency at 28835840 Hz.

Recommended generated frequency range: 220-1960 Hz

The phase_counter module is simply a 9-bit counter that counts up with the clock and outputs the counter value subsample_phase. Each counter period corresponds to one sample.

The sine module uses CORDIC to algorithmically estimate sine values. The stages of estimation and updating outputs are coordinated with subsample_phase. The triangle module uses DDS to create a uniform increasing and decreasing ramp waveform with the specified period.

### Block diagram
![Block diagram](./block_diagram.jpg)

### Register map
| Register    | Description           |
|-------------|-----------------------|
| 0b0000      | freq_ch1* (sine)      |
| 0b0001      | freq_ch2* (triangle)  |
| 0b0010-1111 | Reserved/unused       |

*Least significant 12 bits of frequency registers are read.
To calculate register values from frequency f in Hz, use the following formula:

freq_chX = round((f * 2^14) / f_sample)

where f_sample = 28160 Hz, the output sample rate.

## Pinout
Clock frequency: 28835840 Hz
Reset: active low

| # | Input                   | Output     | Bidirectional        |
|---|-------------------------|------------|----------------------|
| 0 | Register bus address[0] | -          | Register bus data[0] |
| 1 | Register bus address[1] | -          | Register bus data[1] |
| 2 | Register bus address[2] | -          | Register bus data[2] |
| 3 | Register bus address[3] | -          | Register bus data[3] |
| 4 | Transfer phase          | -          | Register bus data[4] |
| 5 | Transfer enable         | -          | Register bus data[5] |
| 6 | -                       | -          | Register bus data[6] |
| 7 | -                       | PWM output | Register bus data[7] |

### Bus details
To write to registers:
0. Start with enable = 0
1. Set address bits, most significant 8 bits of data, and phase to 1 for at least 2 clock cycles.
2. Set enable to 1 for at least 2 cycles. When this edge is detected, the most significant 8 bits will be read.
3. Set phase to 0 for at least 2 cycles. When this edge is detected, the least significant 8 bits will be read.
4. Set enable to 0 for at least 2 cycles. When this edge is detected, the full register value will be written at the specified address.

If any of these steps are violated, the internal state machine will either:
- if enable is 1: transition into an error state which can be reset by toggling enable back to 0
- if enable is 0: discard the ongoing bus transfer and reset to idle state

See src/register_interface.v for the exact details of the bus transfer logic.

## Requirements

- Yosys OSS CAD suite:
  https://github.com/YosysHQ/oss-cad-suite-build
- KiCad (optional, for simulating and exporting DAC frequency response)
- Python modules: numpy, scipy

## How to test
Remember to source OSS CAD suite.
gtkwave can be used to view output waveforms of tests.

### System-Level Tests
`cd test/`

RTL test:
`make -B`

Gate-level test (requires hardening first. see Hardening section):
`TOP_MODULE=$(cd .. && ./tt/tt_tool.py --print-top-module)`
`cp ../runs/wokwi/final/pnl/$TOP_MODULE.pnl.v gate_level_netlist.v`
`make -B GATES=yes`

These tests are also run by the TinyTapeout Github Actions.

### Block-Level Tests
RTL tests only.
There are four block-level test directories:
- test/tb_pwm_phase - for phase_counter and pwm
- test/tb_regs - for register_interface
- test/tb_sine - for sine
- test/tb_triangle - for triangle

For each one, enter the directory and run `make -B`.

### Audio Test
This test runs a really long (around 1s) RTL simulation, exports the data, then simulates the PWM signal being filtered by the Audio Pmod circuit to generate a .wav file that you can listen to!
1. `cd test/ && make -B AUDIO=yes` - this takes 10min on my machine, will vary depending on hardware. It generates three tones of 0.3s each. This will create pwm_edges.log in the `test/` directory.
2. `cd ../pmod-sim/` and run the KiCad ngspice simulation of the Pmod circuit to export the frequency response, or use the pre-simulated freq_response.csv.
3. run filter_pwm.py, which will apply the filter to the pwm_edges.log file and create output.wav.

## Hardening & Viewing
See: https://tinytapeout.com/guides/local-hardening/

## External hardware

Audio Pmod required: [store.tinytapeout.com/products/Audio-Pmod-p716541601]()