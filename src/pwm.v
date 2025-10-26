// gate estimate: <150

`default_nettype none

module pwm (
    input  wire [7:0] bitstream,
    output reg        pwm_out,
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    reg [7:0] subsample_phase = 8'b0; // counts with clk from 0 to 255; we expect a new sample in bitstream upon every reset
    reg [7:0] current_sample = 8'b0;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            subsample_phase <= 8'b0;
            current_sample <= 8'b0;
            pwm_out <= 1'b0;
        end else begin            
            // increment counter
            subsample_phase <= subsample_phase + 8'b1;

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