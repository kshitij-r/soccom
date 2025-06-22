module ram_axi# (
parameter MEMORY_SIZE = 32'h0002_0000
) (
input logic  clk_i
input logic  rst_ni
axi_lite.slave   slave) ;


wire [slave.AXI_ADDR_WIDTH - 1:0] wbs_ ram_adr_i;
wire          wb_clk;
wire wbs_ram_cyc_i;
wire [slave.AXI_DATA_WIDTH - 1:0] wbs_ ram_dat_i;
wire          wb_rst;
wire [3:0]   wbs_ram_sel_i;
wire wbs_ram_stb_i;
wire wbs_ram_we_i;
wire    wbs_ram_ack_o;
wire [slave.AXI_DATA_WIDTH - 1:0]   wbs_ram_dat_o;
bonfire_axi4l2wb # (
       .ADRWIDTH     (slave.AXI_ADDR_WIDTH),
       .FAST_READ_TERM  (1'd0) 
) bonfire_axi4l2wb_inst # (
       .S_AXI_ACLK    (clk_i),
       .S_AXI_ARESETN    (rst_ni),
       .S_AXI_AWADDR    (slave.aw_addr),
       .S_AXI_AWVALID  (slave.aw_valid),
       .S_AXI_AWREADY  (slave.aw_ready),
       .S_AXI_WDATA    (slave.w_data),
       .S_AXI_WSTRB    (slave.w_strb),
       .S_AXI_WVALID   (slave.w_valid),
       .S_AXI_WREADY   (slave.w_ready),
       .S_AXI_ARADDR   (slave.ar_addr),
       .S_AXI_ARVALID  (slave.ar_valid),
       .S_AXI_ARREADY  (slave.ar_ready),
       .S_AXI_RDATA    (slave.r_data),
       .S_AXI_RRESP    (slave.r_resp),
       .S_AXI_RVALID   (slave.r_valid),
       .S_AXI_RREADY   (slave.r_ready),
       .S_AXI_BRESP    (slave.b_resp),
       .S_AXI_BVALID   (slave.b_valid),
       .S_AXI_BREADY   (slave.b_ready),
.wb_adr_o ( wbs_ram_adr_i ) 
.wb_clk_o ( wb_clk ) 
.wb_cyc_o ( wbs_ram_cyc_i ) 
.wb_dat_o ( wbs_ram_dat_i ) 
.wb_rst_o ( wb_rst ) 
.wb_sel_o ( wbs_ram_sel_i ) 
.wb_stb_o ( wbs_ram_stb_i ) 
.wb_we_o ( wbs_ram_we_i ) 
.wb_ack_i(wbs_ram_ack_o),
.wb_dat_i(wbs_ram_dat_o)
) ;


`ifndef SRAM_INITIALIZATION_FILE
   `define SRAM_INITIALIZATION_FILE
`endifram_wb #(
) ram_wb_inst (
.wb_ack_o       (wbs_ram_ack_o),
.wb_err_o       (),
.wb_rty_o       (wbs_ram_rty_o),
.wb_dat_o       (wbs_ram_dat_o)
