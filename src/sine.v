// written with the help of some YouTube videos & ChatGPT describing the algorithm on a high level 
// as well as this example for some implementation details:
// https://github.com/cebarnes/cordic/blob/master/cordic.v

// output sent on clock edge where subsample_phase = 8

`default_nettype none

module sine #(
    parameter ACC_BITS = 16
) (
    input  wire [7:0] subsample_phase,
    input  wire [ACC_BITS-4:0] freq_increment, // from freq register
    input  wire rst_n,
    input  wire clk,
    output reg [7:0] out
);
    localparam CORDIC_ITER = 8;

    reg [7:0] x, y, t;

    // cordic atan table (in 8-bit 0-255)
    wire [7:0] atan_table [0:7];
    assign atan_table[0] = 8'd64;   // 45°
    assign atan_table[1] = 8'd38;   // atan(2^-1)
    assign atan_table[2] = 8'd20;   // atan(2^-2)
    assign atan_table[3] = 8'd10;   // atan(2^-3)
    assign atan_table[4] = 8'd5;    // atan(2^-4)
    assign atan_table[5] = 8'd2;    // atan(2^-5)
    assign atan_table[6] = 8'd1;    // atan(2^-6)
    assign atan_table[7] = 8'd1;    // atan(2^-7)

    // (ACC_BITS-4)-bit frequency resolution. using the most significant 4 bits will
    // create a really distorted output wave
    reg [ACC_BITS-1:0] accumulator;

    // Scale factor pre-applied to x (approx K = 0.607, product of sines)
    localparam [7:0] X_INIT = 8'd77; // 0.607 * 127 ≈ 77
    
    // s_p = 255: start sine calculation on t=accumulator
    // s_p = 0-7: sine calculation
    // s_p = 8: send to output, increment accumulator
    // otherwise idle
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x <= 8'b0;
            y <= 8'b0;
            t <= 8'b0;
            accumulator <= {ACC_BITS{1'b0}};
        end else begin
            if (subsample_phase == 255) begin
                x <= X_INIT;
                y <= 8'd0;
                case (accumulator[ACC_BITS-1:ACC_BITS-2])
                    2'b11,
                    2'b00: t <= accumulator[ACC_BITS-2:ACC_BITS-9];
                    2'b01,
                    2'b10: t <= 8'd255 - accumulator[ACC_BITS-2:ACC_BITS-9];
                endcase
            end else if (subsample_phase < 8) begin
                if (t[7] == 0) begin
                    // Rotate positive
                    x <= x - (y >> subsample_phase);
                    y <= y + (x >> subsample_phase);
                    t <= t - atan_table[subsample_phase];
                end else begin
                    // Rotate negative
                    x <= x + (y >> subsample_phase);
                    y <= y - (x >> subsample_phase);
                    t <= t + atan_table[subsample_phase];
                end
            end else if (subsample_phase == 8) begin
                out <= y + 8'd128;
                accumulator <= accumulator + freq_increment;
            end
        end
    end
endmodule