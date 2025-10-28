/*
 * Copyright (c) 2025 Rongbin Gu, Evan Li
 * SPDX-License-Identifier: MIT
 */

`default_nettype none

module triangle #(
    parameter ACC_BITS = 14
) (
    input wire [7:0] subsample_phase,
    input wire [ACC_BITS-3:0] freq_increment, // from freq register
    input wire rst_n,
    input wire clk,
    output reg[6:0] out
);

    // internal accumulator based on freq_increment
    reg [ACC_BITS-1:0] accumulator;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out <= 7'b0; // reset to 0
            accumulator <= {ACC_BITS{1'b0}};
        end else begin
            // generate triangle wave from accumulator
            if (accumulator[ACC_BITS-1] == 1'b0) begin
                out <= accumulator[ACC_BITS-2:ACC_BITS-8]; // ascending ramp up from 0-127 (MSB = 0)
            end else begin
                out <= ~accumulator[ACC_BITS-2:ACC_BITS-8]; // descending ramp down from 127-0 (MSB = 1)
            end
            
            // increment accumulator once per sample period (synced with PWM)
            if (subsample_phase == 8'd8) begin
                accumulator <= accumulator + {2'b0, freq_increment};
            end
        end
    end

endmodule
