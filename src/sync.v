module sync (
    input  wire in,
    input  wire clk,
    input  wire rst_n,
    output reg  out
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