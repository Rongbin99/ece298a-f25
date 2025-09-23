<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

3-channel square wave sound chip with support for amplitude, frequency, and duty cycle updates per channel.

### Block diagram
![Block diagram](./block_diagram_v1.png)

### Register map
| Register    | Description                  |
|-------------|------------------------------|
| 0b0000      | Channel enable               |
| 0b0001      | Trigger update*              |
| 0b0010      | Ch1 freq                     |
| 0b0011      | Ch2 freq                     |
| 0b0100      | Ch3 freq                     |
| 0b0101      | Amplitudes (3x 5-bit fields) |
| 0b0110      | Duty cycles (3 5-bit fields) |
| 0b0111-1111 | Reserved/unused              |

*Trigger update: Inputted register values are only applied on the falling edge of the LSB of this register.
This ensures all changes apply at the same time - otherwise may cause audio glitches/delays, for instance when
changing the pitch of two channels at the same time.

## How to test

play a tune!

### Bus details

TBD

## External hardware

Audio Pmod required: [store.tinytapeout.com/products/Audio-Pmod-p716541601]()

## Pin assignments
| # | Input                   | Output     | Bidirectional        |
|---|-------------------------|------------|----------------------|
| 0 | Register bus address[0] | -          | Register bus data[0] |
| 1 | Register bus address[1] | -          | Register bus data[1] |
| 2 | Register bus address[2] | -          | Register bus data[2] |
| 3 | Register bus address[3] | -          | Register bus data[3] |
| 4 | Transfer enable         | -          | Register bus data[4] |
| 5 | Transfer phase**        | -          | Register bus data[5] |
| 6 | -                       | -          | Register bus data[6] |
| 7 | -                       | PDM output | Register bus data[7] |

**Transfer phase: 0 if transferring lower/least significant 8 bits of 16 bit register, 1 if transferring higher/most significant 8 bits.  
