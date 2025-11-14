/*
 * Copyright (c) 2025 Rongbin Gu, Evan Li
 * SPDX-License-Identifier: MIT
 */

`default_nettype none

module register_interface #(
    parameter NUM_REGS = 2 // number of registers
) (
    input  wire                   enable,           // enable input
    input  wire                   phase,            // phase input
    input  wire [3:0]             address,          // address input
    input  wire [7:0]             reg_value,        // register value input
    input  wire                   clk,              // clock
    input  wire                   rst_n,            // reset_n - low to reset
    output wire [NUM_REGS*16-1:0] registers_flat    // flattened registers output
);
    reg [15:0] registers [NUM_REGS-1:0];
    
    // flatten registers 2d array to output
    assign registers_flat[15:0] = registers[0];
    assign registers_flat[31:16] = registers[1];

    wire enable_sync;
    wire phase_sync;
    reg enable_prev;
    reg phase_prev;

    reg [1:0] state;
    reg [15:0] temp;

    sync enable_sync_inst (
        .in (enable),
        .clk (clk),
        .rst_n (rst_n),
        .out (enable_sync)
    );

    sync phase_sync_inst (
        .in (phase),
        .clk (clk),
        .rst_n (rst_n),
        .out (phase_sync)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            registers[0] <= 16'b0;
            registers[1] <= 16'b0;
            enable_prev <= 1'b0;
            phase_prev <= 1'b0;
            state <= 2'b0;
            temp <= 16'b0;
        end else begin
            enable_prev <= enable_sync;
            phase_prev <= phase_sync;

            /**
            state 0: default, enabled = 0, phase = x
                enabled rising & phase = 1: state 1, temp MSB set to value
                enabled rising & phase = 0: state error
            state 1: enabled = 1, phase = 1
                phase falling: state 2, temp LSB set to value
                enabled falling: state 0 (is an error)
            state 2: enabled = 1, phase = 0
                enabled falling: state 0, i_regs[address] set to temp
                phase rising: state error
            state 3: error, enabled = 1, phase = x
                enabled falling: state 0
            */

            case (state)
                2'b00: begin // State 0: default, enabled = 0
                    if (enable_sync & !enable_prev) begin
                        if (phase_sync) begin
                            state <= 2'b01; // Go to state 1
                            temp[15:8] <= reg_value; // Set MSB
                        end else begin
                            state <= 2'b11; // Go to error state
                        end
                    end
                end
                
                2'b01: begin // State 1: enabled = 1, phase = 1
                    if (!phase_sync & phase_prev) begin
                        state <= 2'b10; // Go to state 2
                        temp[7:0] <= reg_value; // Set LSB
                    end else if (!enable_sync & enable_prev) begin
                        state <= 2'b00; // Error: go back to state 0
                    end
                end
                
                2'b10: begin // State 2: enabled = 1, phase = 0
                    if (!enable_sync & enable_prev) begin
                        state <= 2'b00; // Go back to state 0
                        if (address < NUM_REGS) begin
                            registers[address[0]] <= temp; // Write complete 16-bit value
                        end
                    end else if (phase_sync & !phase_prev) begin
                        state <= 2'b11; // Error: go to error state
                    end
                end
                
                2'b11: begin // State 3: error state
                    if (!enable_sync & enable_prev) begin
                        state <= 2'b00; // Go back to state 0
                    end
                end
            endcase
        end
    end

endmodule
