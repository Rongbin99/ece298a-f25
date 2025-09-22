/*
 * Copyright (c) 2025 Rongbin Gu
 * SPDX-License-Identifier: Apache-2.0
 */
`default_nettype none

module tt_um_counter (
    input  wire [7:0] ui_in,    // [7]=load_en (sync), [6]=count_en, [0]=tri_en
    output wire [7:0] uo_out,   // Dedicated outputs (always driven)
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path (drives current count when enabled)
    output wire [7:0] uio_oe,   // IOs: Output enable path (active high)
    input  wire       ena,      
    input  wire       clk,      
    input  wire       rst_n     // reset (async active low)
);

  // 8-bit counter value
  reg [7:0] counter_register;

  // async reset, load sync and count++
  // on falling edge of rst_n, reset to 0 (bc active low)
  // on rising edge of clk, if enable, sync load or increment counter
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin // async reset
      counter_register <= 8'h00; // reset value to 0
    end else if (ena) begin // enable == 1, begin
      if (ui_in[7]) begin // load_en == 1, load value from uio_in
        // sync load from uio_in
        counter_register <= uio_in;
      end else if (ui_in[6]) begin // count_en == 1, begin counting
        // count++
        counter_register <= counter_register + 8'h01;
      end
    end
  end

  // output the current count
  assign uo_out = counter_register;

  // tri-state outputs on the uio bus: drive count when ui_in[0] is asserted
  assign uio_out = counter_register;
  assign uio_oe  = {8{ui_in[0]}}; // uio_oe == 1: drive, 0: Z (tri-state)

endmodule
