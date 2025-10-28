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
  reg [11:0] freq_increment;
  wire [6:0] out;

  triangle triangle_inst (
      subsample_phase,
      freq_increment,
      rst_n,
      clk,
      out
  );  
  
endmodule
