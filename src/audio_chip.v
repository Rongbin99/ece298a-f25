/*
 * Copyright (c) 2025 Rongbin Gu, Evan Li
 * SPDX-License-Identifier: MIT
 */

`default_nettype none

module tt_um_rongbin99_happyredmapleleaf_audio_chip (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    assign uio_oe = 8'b0;

    wire  [6:0] bitstream_ch1;
    wire  [6:0] bitstream_ch2;
    wire  [9:0] subsample_phase;

    wire [15:0] registers [1:0]; // other modules use this
    wire [31:0] registers_flat; // register interface outputs into this

    // route between flattened and array-form registers
    assign registers[0] = registers_flat[15:0];
    assign registers[1] = registers_flat[31:16];

    phase_counter counter (
        .subsample_phase(subsample_phase),
        .clk(clk),
        .rst_n(rst_n)
    );

    register_interface reg_block (
        .enable(ui_in[5]),
        .phase(ui_in[4]),
        .address(ui_in[3:0]),
        .reg_value(uio_in),
        .clk(clk),
        .rst_n(rst_n),
        .registers_flat(registers_flat)
    );

    sine sine_gen (
        .subsample_phase(subsample_phase),
        .freq_increment(registers[0][11:0]),
        .rst_n(rst_n),
        .clk(clk),
        .out(bitstream_ch1)
    );  

    triangle triangle_gen (
        .subsample_phase(subsample_phase),
        .freq_increment(registers[1][11:0]),
        .rst_n(rst_n),
        .clk(clk),
        .out(bitstream_ch2)
    );

    pwm pwm_gen (
        .subsample_phase(subsample_phase[7:0]),
        .bitstream_ch1(bitstream_ch1),
        .bitstream_ch2(bitstream_ch2),
        .clk(clk),
        .rst_n(rst_n),
        .pwm_out(uo_out[7])
    );

    assign uo_out[6:0] = 7'b0;
    assign uio_out = 8'b0;
    wire _unused = &{ui_in[7:6], ena, 1'b0};

endmodule