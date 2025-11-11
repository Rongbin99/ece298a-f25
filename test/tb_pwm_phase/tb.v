`default_nettype none
`timescale 1ns / 1ps

module tb ();

  // Dump the signals to a VCD file. You can view it with gtkwave or surfer.
  initial begin
    $dumpfile("tb.vcd");
    $dumpvars(0, tb);
    #1;
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  wire [9:0] subsample_phase;
  reg [6:0] bitstream_ch1;
  reg [6:0] bitstream_ch2;
  wire pwm_out;

  phase_counter phase_counter_inst (
      subsample_phase,
      clk,
      rst_n
  );

  pwm pwm_inst (
      subsample_phase[7:0],
      bitstream_ch1,
      bitstream_ch2,
      clk,
      rst_n,
      pwm_out
  );
  
endmodule
