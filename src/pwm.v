`default_nettype none

module pwm (
    input  wire [7:0] bitstream,
    output reg        pwm_out,
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    reg [7:0] bitstream_sync1;
    reg [7:0] bitstream_sync2;
    reg [7:0] subsample_counter = 8'b0; // counts with clk from 0 to 255; we expect a new sample in bitstream upon every reset
    reg [7:0] current_sample = 8'b0;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            bitstream_sync1 <= 8'b0;
            bitstream_sync2 <= 8'b0;
            subsample_counter <= 8'b0;
            current_sample <= 8'b0;
            pwm_out <= 1'b0;
        end else begin
            // double sync
            bitstream_sync1 <= bitstream;
            bitstream_sync2 <= bitstream_sync1;
            
            // increment counter
            subsample_counter <= subsample_counter + 8'b1;

            // capture sample to output
            if (subsample_counter == 8'b0) begin
                current_sample <= bitstream_sync2;
            end
            
            // PWM output
            if (subsample_counter > current_sample) begin
                pwm_out <= 1'b1;
            end else begin
                pwm_out <= 1'b0;
            end
        end
    end

endmodule