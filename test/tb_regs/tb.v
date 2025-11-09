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
  reg enable;
  reg phase;
  reg [3:0] address;
  reg [7:0] reg_value;
  wire [31:0] registers_flat;

  register_interface regs_inst (
    enable,           // enable input
    phase,            // phase input
    address,          // address input
    reg_value,        // register value input
    clk,              // clock
    rst_n,            // reset_n - low to reset
    registers_flat    // flattened registers output
  );
  
endmodule
