// Golden reference DUT for harness validation

module axi4_stream_packet_monitor #(
    parameter int DATA_WIDTH = 32,
    parameter int KEEP_WIDTH = DATA_WIDTH / 8
) (
    input  logic                  clk,
    input  logic                  rst_n,
    input  logic                  s_axis_tvalid,
    output logic                  s_axis_tready,
    input  logic [DATA_WIDTH-1:0] s_axis_tdata,
    input  logic [KEEP_WIDTH-1:0] s_axis_tkeep,
    input  logic                  s_axis_tlast,
    output logic [31:0]           packet_count,
    output logic [31:0]           byte_count,
    output logic [DATA_WIDTH-1:0] header_capture,
    output logic                  header_valid,
    output logic                  activity
);

    assign s_axis_tready = 1'b1;

    logic in_packet;
    logic activity_hold;

    function automatic int popcount(input logic [KEEP_WIDTH-1:0] keep);
        int count;
        count = 0;
        for (int i = 0; i < KEEP_WIDTH; i++)
            if (keep[i])
                count++;
        return count;
    endfunction

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            packet_count   <= 32'd0;
            byte_count     <= 32'd0;
            header_capture <= '0;
            header_valid   <= 1'b0;
            in_packet      <= 1'b0;
            activity_hold  <= 1'b0;
        end else if (s_axis_tvalid && s_axis_tready) begin
            byte_count <= byte_count + popcount(s_axis_tkeep);
            header_valid <= !in_packet;

            if (!in_packet) begin
                header_capture <= s_axis_tdata;
                in_packet      <= 1'b1;
                activity_hold  <= 1'b1;
            end

            if (s_axis_tlast) begin
                packet_count  <= packet_count + 32'd1;
                in_packet     <= 1'b0;
                activity_hold <= 1'b0;
            end
        end else begin
            header_valid <= 1'b0;
        end
    end

    assign activity = activity_hold | (s_axis_tvalid && s_axis_tready && s_axis_tlast);

endmodule
