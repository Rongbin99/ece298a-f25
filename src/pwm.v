/*
 * Copyright (c) 2025 Rongbin Gu, Evan Li
 * SPDX-License-Identifier: MIT
 */

// gate estimate: ~50
// sine block pushes new samples on phase = 7 so PWM capturing samples on phaes = 0 is okay

`default_nettype none

module pwm (
    input  wire [7:0] subsample_phase,  // subsample phase input
    input  wire [7:0] bitstream,        // bitstream input
    input  wire       clk,              // clock
    input  wire       rst_n,            // reset_n - low to reset
    output reg        pwm_out           // pwm output
);
    reg [7:0] current_sample = 8'b0; // current sample output

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_sample <= 8'b0; // reset to 0
            pwm_out <= 1'b0; // reset to 0
        end else begin
            // capture sample to output
            if (subsample_phase == 8'b0) begin
                current_sample <= bitstream;
            end
            
            // PWM output
            if (subsample_phase < current_sample) begin
                pwm_out <= 1'b1;
            end else begin
                pwm_out <= 1'b0;
            end
        end
    end

endmodule
