`default_nettype none

module register_interface (
    input  wire       enable,
    input  wire       phase,
    input  wire [3:0] address,
    input  wire [7:0] reg_value,
    input  wire       clk,
    input  wire       rst_n,
    output reg [15:0] registers [0:15]
);

    wire enable_sync;
    wire phase_sync;
    reg enable_prev;
    reg phase_prev;

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

    // writing anything to address 0 will update all output registers
    // (value of address 0 is always 0)
    assign registers[0] = 16'b0;

    reg [15:0] intermediate_regs [1:15];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 1; i < 16; i = i + 1) begin
                registers[i] <= 16'b0;
                intermediate_regs[i] <= 16'b0;
            end
            enable_prev <= 1'b0;
            phase_prev <= 1'b0;
        end else begin
            enable_prev <= enable_sync;
            phase_prev <= phase_sync;

            /**
            ONLY VALID REG WRITE SEQUENCE:
            phase set to 1, address and value set
            enable set to 1. on this edge, i_regs[address] MSB set to value
                if address == 0, regs set to i_regs
            phase set to 0. on this edge, i_regs[address] LSB set to value
                if address == 0, do nothing
            enable set to 0.
            */

            if (enable_sync & !enable_prev & phase_sync) {
                if (address == 4'b0000) begin
                    // regs set to i_regs
                    for (int i = 1; i < 16; i = i + 1) begin
                        registers[i] <= intermediate_regs[i];
                    end
                end else begin
                    // i_regs[address] MSB set to value
                    intermediate_regs[address][15:8] <= reg_value;
                end
            }

            if (!phase_sync & phase_prev & enable_sync) {
                if (address != 4'b0000) begin
                    // i_regs[address] LSB set to value
                    intermediate_regs[address][7:0] <= reg_value;
                end
            }
        end
    end

endmodule