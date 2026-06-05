// Stub DUT — intentionally incomplete for agent benchmark.
// Agent should implement per docs/RTL_SPEC.md

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

    // TODO: Implement byte counting, header capture, activity signaling per RTL_SPEC.md

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            packet_count <= 32'd0;
            byte_count   <= 32'd0;
        end else if (s_axis_tvalid && s_axis_tready && s_axis_tlast) begin
            packet_count <= packet_count + 32'd1;
        end
    end

    assign header_capture = '0;
    assign header_valid   = 1'b0;
    assign activity       = 1'b0;

endmodule
