// amplitude = 0: no output
// amplitude = 1: quartered
// amplitude = 2: halved
// amplitude = 3: full
// gate count estimate: <50
// output is time-delayed by 1 clock cycle

`default_nettype none

module digital_amp_control (
    input  wire [7:0] in,
    input  wire [1:0] amplitude,
    input  wire       clk,
    input  wire       rst_n,
    output reg  [7:0] out
);    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out <= 8'b0;
        end else begin
            case (amplitude)
                2'd0: out <= 8'd0;
                2'd1: out <= in >> 2;
                2'd2: out <= in >> 1;
                2'd3: out <= in;
            endcase
        end
    end
endmodule