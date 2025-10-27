// LITERALLY just an 8-bit counter.

`default_nettype none

module phase_counter (
    output reg [7:0] subsample_phase,
    input  wire      clk,      // clock
    input  wire      rst_n     // reset_n - low to reset
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            subsample_phase <= 8'b0;
        end else begin
            subsample_phase <= subsample_phase + 8'b1;
        end
    end
endmodule