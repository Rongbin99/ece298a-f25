/*
 * Copyright (c) 2025 Rongbin Gu, Evan Li
 * SPDX-License-Identifier: MIT
 */

`default_nettype none

module triangle (
    input wire [7:0] subsample_phase,
    input wire clk,
    input wire rst_n,
    output reg[6:0] out
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out <= 7'b0; // reset to 0
        end else begin
            if (subsample_phase[7] == 1'b0) begin
                out <= subsample_phase[6:0]; // ascending ramp up from 0-127 (MSB = 0)
            end else begin
                out <= ~subsample_phase[6:0]; // descending ramp down from 127-0 (MSB = 1)
            end
        end
    end

endmodule
