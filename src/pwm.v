// gate estimate: ~50
// sine block pushes new samples on phase = 7 so PWM capturing samples on phaes = 0 is okay

`default_nettype none

module pwm (
    input  wire [7:0] subsample_phase,
    input  wire [7:0] bitstream,
    output reg        pwm_out,
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    reg [7:0] current_sample = 8'b0;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_sample <= 8'b0;
            pwm_out <= 1'b0;
        end else begin
            // capture sample to output
            if (subsample_phase == 8'b0) begin
                current_sample <= bitstream;
            end
            
            // PWM output
            if (subsample_phase > current_sample) begin
                pwm_out <= 1'b1;
            end else begin
                pwm_out <= 1'b0;
            end
        end
    end

endmodule