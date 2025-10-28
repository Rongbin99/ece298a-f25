// written with the help of some YouTube videos & ChatGPT describing the algorithm on a high level 
// as well as this example for some implementation details:
// https://github.com/cebarnes/cordic/blob/master/cordic.v

// output sent on clock edge where subsample_phase = 7

// time input: 8 bit extended to 14 (DDS frequency control)
// cordic algorithm takes 8-bit input representing -90 to +90 degrees
// extended 14-bit accumulator: 1st bit extends angle range to -180 to 180 degrees
//                              next 8 bits are inputted to CORDIC (sometimes inverted)
//                              last 5 bits are used to improve output resolution
// output: 7-bit
// if gate-limited, change to 6-bit bit shifted left. Based on testing,
// audio quality suffers little for notes between A3 (220Hz) and A6 (1760Hz) with a sample rate of 28160

`default_nettype none

module sine #(
    parameter ACC_BITS = 14
) (
    input  wire [7:0] subsample_phase,
    input  wire [ACC_BITS-3:0] freq_increment, // from freq register
    input  wire rst_n,
    input  wire clk,
    output reg [6:0] out
);
    reg signed [7:0] t;
    reg signed [6:0] x, y;

    // cordic atan table (in 8-bit 0-255)
    wire [7:0] atan_table [0:7];
    assign atan_table[0] = 8'd64;   // 45
    assign atan_table[1] = 8'd38;   // atan(2^-1)
    assign atan_table[2] = 8'd20;   // atan(2^-2)
    assign atan_table[3] = 8'd10;   // atan(2^-3)
    assign atan_table[4] = 8'd5;    // atan(2^-4)
    assign atan_table[5] = 8'd3;    // atan(2^-5)
    assign atan_table[6] = 8'd1;    // atan(2^-6)
    assign atan_table[7] = 8'd1;    // atan(2^-7)

    // (ACC_BITS-4)-bit frequency resolution. using the most significant 4 bits will
    // create a really distorted output wave
    reg [ACC_BITS-1:0] accumulator;

    // alias used in cordic algo
    wire [7:0] acc_slice;
    assign acc_slice = accumulator[ACC_BITS-2:ACC_BITS-9];

    // Scale factor pre-applied to x (approx K = 0.607, product of cosines)
    localparam [6:0] X_INIT = 7'd38; // 0.607 * 63 ~= 39
    
    // s_p = 255: start sine calculation on t=accumulator
    // s_p = 0-7: sine calculation
    // s_p = 8: send to output, increment accumulator
    // otherwise idle
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x <= 7'b0;
            y <= 7'b0;
            t <= 8'b0;
            accumulator <= {ACC_BITS{1'b0}};
        end else begin
            if (subsample_phase == 255) begin
                x <= X_INIT;
                y <= 7'd0;

                // TODO: explain this
                // reassigning 0 to 511 (top 9 bits of acc)
                // into 127 to -128 (input angle of cordic)
                case (accumulator[ACC_BITS-1:ACC_BITS-2])
                    2'b11,
                    2'b00: t <= acc_slice;
                    2'b10,
                    2'b01: t <= ~acc_slice;
                endcase
            end else if (subsample_phase < 8) begin
                if (t[7] == 0) begin
                    // Rotate positive
                    x <= x - (y >>> subsample_phase);
                    y <= y + (x >>> subsample_phase);
                    t <= t - atan_table[subsample_phase[2:0]];
                end else begin
                    // Rotate negative
                    x <= x + (y >>> subsample_phase);
                    y <= y - (x >>> subsample_phase);
                    t <= t + atan_table[subsample_phase[2:0]];
                end
            end else if (subsample_phase == 8) begin
                out <= y + 7'd64;
                accumulator <= accumulator + {2'b0,freq_increment};
            end
        end
    end
endmodule