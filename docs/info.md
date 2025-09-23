<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

TBD

### Block diagram

## How to test

TBD

## External hardware

Audio Pmmod required: store.tinytapeout.com/products/Audio-Pmod-p716541601

## Pin assignments
| # | Input                   | Output     | Bidirectional        |
|---|-------------------------|------------|----------------------|
| 0 | Register bus address[0] | -          | Register bus data[0] |
| 1 | Register bus address[1] | -          | Register bus data[1] |
| 2 | Register bus address[2] | -          | Register bus data[2] |
| 3 | Register bus address[3] | -          | Register bus data[3] |
| 4 | Transfer enable         | -          | Register bus data[4] |
| 5 | Transfer phase*         | -          | Register bus data[5] |
| 6 | -                       | -          | Register bus data[6] |
| 7 | -                       | PDM output | Register bus data[7] |

*Transfer phase: 0 if transferring lower/least significant 8 bits of 16 bit register, 1 if transferring higher/most significant 8 bits.  
