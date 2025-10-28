/*
 * Copyright (c) 2025 Rongbin Gu, Evan Li
 * SPDX-License-Identifier: MIT
 */

// synchronizes the input by using a FF chain to avoid metastability

`default_nettype none

module sync (
    input  wire in,         // input to sync
    input  wire clk,        // clock
    input  wire rst_n,      // reset_n - low to reset
    output reg  out         // output of sync (1 bit)
);

    reg sync1; 
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sync1 <= 1'b0;
            out <= 1'b0;
        end else begin
            sync1 <= in;
            out <= sync1;
        end
    end

endmodule
