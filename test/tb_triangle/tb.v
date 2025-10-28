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
  reg [7:0] subsample_phase;
  wire [6:0] out;

  triangle triangle_inst (
      subsample_phase,
      clk,
      rst_n,
      out
  );  
  
endmodule
