/*
 * Copyright (c) 2025 Rongbin Gu, Evan Li
 * SPDX-License-Identifier: MIT
 */

// LITERALLY just an 8-bit counter.

`default_nettype none

module phase_counter (
    output reg [7:0] subsample_phase,  // subsample phase output
    input  wire      clk,              // clock
    input  wire      rst_n             // reset_n - low to reset
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            subsample_phase <= 8'b0; // reset to 0
        end else begin
            subsample_phase <= subsample_phase + 8'b1; // increment by 1 on each clock edge
        end
    end

endmodule
