/*
 * Copyright (c) 2025 Rongbin Gu, Evan Li
 * SPDX-License-Identifier: MIT
 */

`default_nettype none

module tt_um_audio_chip (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    wire  [7:0] bitstream;
    wire [16:0] registers [1:0];
    wire  [7:0] subsample_phase;

    assign bitstream[7] = 1'b0;

    phase_counter counter (
        subsample_phase,
        clk,
        rst_n
    );

    register_interface reg_block (
        ui_in[5],
        ui_in[4],
        ui_in[3:0],
        uio_in,
        clk,
        rst_n,
        registers
    );

    sine sine_gen (
        subsample_phase,
        registers[0][11:0],
        rst_n,
        clk,
        bitstream[6:0]
    );  

    pwm pwm_out (
        subsample_phase,
        bitstream,
        uo_out[7],
        clk,
        rst_n 
    );

    assign uio_out = 8'b0;
    wire _unused = &{ena, 1'b0};

endmodule