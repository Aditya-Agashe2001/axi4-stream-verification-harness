`timescale 1ns/1ps

module tb_top;

    logic                  clk;
    logic                  rst_n;
    logic                  s_axis_tvalid;
    logic                  s_axis_tready;
    logic [31:0]           s_axis_tdata;
    logic [3:0]            s_axis_tkeep;
    logic                  s_axis_tlast;
    logic [31:0]           packet_count;
    logic [31:0]           byte_count;
    logic [31:0]           header_capture;
    logic                  header_valid;
    logic                  activity;

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

`ifdef USE_REFERENCE_DUT
    axi4_stream_packet_monitor dut (
        .clk            (clk),
        .rst_n          (rst_n),
        .s_axis_tvalid  (s_axis_tvalid),
        .s_axis_tready  (s_axis_tready),
        .s_axis_tdata   (s_axis_tdata),
        .s_axis_tkeep   (s_axis_tkeep),
        .s_axis_tlast   (s_axis_tlast),
        .packet_count   (packet_count),
        .byte_count     (byte_count),
        .header_capture (header_capture),
        .header_valid   (header_valid),
        .activity       (activity)
    );
`else
    axi4_stream_packet_monitor dut (
        .clk            (clk),
        .rst_n          (rst_n),
        .s_axis_tvalid  (s_axis_tvalid),
        .s_axis_tready  (s_axis_tready),
        .s_axis_tdata   (s_axis_tdata),
        .s_axis_tkeep   (s_axis_tkeep),
        .s_axis_tlast   (s_axis_tlast),
        .packet_count   (packet_count),
        .byte_count     (byte_count),
        .header_capture (header_capture),
        .header_valid   (header_valid),
        .activity       (activity)
    );
`endif

endmodule
