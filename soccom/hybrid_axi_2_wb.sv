//
// Copyright (C) 2018 Massachusetts Institute of Technology
//
// File         : idft_top_axi4lite.v
// Project      : Common Evaluation Platform (CEP)
// Description  : This file provides an axi4-lite wrapper for the wishbone based-IDFT core
//

module axi4lite_2_wb (
										  
  

    // Clock & Reset
    input logic     clk_i,
    input logic     rst_ni,    

    // AXI4-Lite Slave Interface
    AXI_LITE.Slave     slave

);
localparam NR_MASTERS = 2;
localparam NR_SLAVES = 1;
localparam SLAVE_AES_TOP = 0;
    // AES wishbone slave wires
    wire                                wb_clk;
    wire                                wb_rst;
    wire [slave.AXI_ADDR_WIDTH - 1:0]   wbs_d_idft_adr_i;
    wire [slave.AXI_DATA_WIDTH - 1:0]   wbs_d_idft_dat_i;
    wire [3:0]                          wbs_d_idft_sel_i;
    wire                                wbs_d_idft_we_i;
    wire                                wbs_d_idft_cyc_i;
    wire                                wbs_d_idft_stb_i;
    wire [slave.AXI_DATA_WIDTH - 1:0]   wbs_d_idft_dat_o;
    wire                                wbs_d_idft_ack_o;

/////

wire [31:0]   busms_adr_o[0:NR_MASTERS-1];
wire          busms_cyc_o[0:NR_MASTERS-1];
wire [31:0]   busms_dat_o[0:NR_MASTERS-1];
wire [3:0]    busms_sel_o[0:NR_MASTERS-1];
wire          busms_stb_o[0:NR_MASTERS-1];
wire          busms_we_o[0:NR_MASTERS-1];
wire          busms_cab_o[0:NR_MASTERS-1];
wire [2:0]    busms_cti_o[0:NR_MASTERS-1];
wire [1:0]    busms_bte_o[0:NR_MASTERS-1];
wire          busms_ack_i[0:NR_MASTERS-1];
wire          busms_rty_i[0:NR_MASTERS-1];
wire          busms_err_i[0:NR_MASTERS-1];
wire [31:0]   busms_dat_i[0:NR_MASTERS-1];
wire [31:0]   bussl_adr_i[0:NR_SLAVES-1];
wire          bussl_cyc_i[0:NR_SLAVES-1];
wire [31:0]   bussl_dat_i[0:NR_SLAVES-1];
wire [3:0]    bussl_sel_i[0:NR_SLAVES-1];
wire          bussl_stb_i[0:NR_SLAVES-1];
wire          bussl_we_i[0:NR_SLAVES-1];
wire          bussl_cab_i[0:NR_SLAVES-1];
wire [2:0]    bussl_cti_i[0:NR_SLAVES-1];
wire [1:0]    bussl_bte_i[0:NR_SLAVES-1];
wire          bussl_ack_o[0:NR_SLAVES-1];
wire          bussl_rty_o[0:NR_SLAVES-1];
wire          bussl_err_o[0:NR_SLAVES-1];
wire [31:0]   bussl_dat_o[0:NR_SLAVES-1];


wire          snoop_enable;
wire [31:0]   snoop_adr;
wire [31:0]   pic_ints_i [0:1];
assign pic_ints_i[0][31:4] = 28'h0;
assign pic_ints_i[0][1:0] = 2'b00;
genvar        c, m, s;
wire [32*NR_MASTERS-1:0] busms_adr_o_flat;
wire [NR_MASTERS-1:0]    busms_cyc_o_flat;
wire [32*NR_MASTERS-1:0] busms_dat_o_flat;
wire [4*NR_MASTERS-1:0]  busms_sel_o_flat;
wire [NR_MASTERS-1:0]    busms_stb_o_flat;
wire [NR_MASTERS-1:0]    busms_we_o_flat;
wire [NR_MASTERS-1:0]    busms_cab_o_flat;
wire [3*NR_MASTERS-1:0]  busms_cti_o_flat;
wire [2*NR_MASTERS-1:0]  busms_bte_o_flat;
wire [NR_MASTERS-1:0]    busms_ack_i_flat;
wire [NR_MASTERS-1:0]    busms_rty_i_flat;
wire [NR_MASTERS-1:0]    busms_err_i_flat;
wire [32*NR_MASTERS-1:0] busms_dat_i_flat;
wire [32*NR_SLAVES-1:0] bussl_adr_i_flat;
wire [NR_SLAVES-1:0]    bussl_cyc_i_flat;
wire [32*NR_SLAVES-1:0] bussl_dat_i_flat;
wire [4*NR_SLAVES-1:0]  bussl_sel_i_flat;
wire [NR_SLAVES-1:0]    bussl_stb_i_flat;
wire [NR_SLAVES-1:0]    bussl_we_i_flat;
wire [NR_SLAVES-1:0]    bussl_cab_i_flat;
wire [3*NR_SLAVES-1:0]  bussl_cti_i_flat;
wire [2*NR_SLAVES-1:0]  bussl_bte_i_flat;
wire [NR_SLAVES-1:0]    bussl_ack_o_flat;
wire [NR_SLAVES-1:0]    bussl_rty_o_flat;
wire [NR_SLAVES-1:0]    bussl_err_o_flat;
wire [32*NR_SLAVES-1:0] bussl_dat_o_flat;


///////////




    // Instantiate the AXI4Lite to Wishbone bridge
    bonfire_axi4l2wb #(
        .ADRWIDTH       (slave.AXI_ADDR_WIDTH),
        .FAST_READ_TERM (1'd0)
    ) bonfire_axi4l2wb_inst (
        .S_AXI_ACLK     (clk_i),
        .S_AXI_ARESETN  (rst_ni),
        .S_AXI_AWADDR   (slave.aw_addr),
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
        .wb_clk_o       (clk_i),
        .wb_rst_o       (wb_rst),
        .wb_addr_o      (busms_adr_i_flat),
        .wb_dat_o       (busms_dat_o_flat),
        .wb_we_o        (busms_we_i_flat),
        .wb_sel_o       (busms_sel_i_flat),
        .wb_stb_o       (busms_stb_i_flat),
        .wb_cyc_o       (busms_cyc_i_flat),
        .wb_dat_i       (busms_dat_i_flat),
        .wb_ack_i       ()
    );
         
 /*   // Instantiate the wishbone-based IDFT Core
    idft_top_top idft_top_top_inst (
        // Wishbone Slave interface
        .wb_clk_i       (clk_i),
        .wb_rst_i       (rst_ni),
        .wb_dat_i       (wbs_d_idft_dat_i),
        .wb_adr_i       (wbs_d_idft_adr_i),
        .wb_sel_i       (wbs_d_idft_sel_i[3:0]),
        .wb_we_i        (wbs_d_idft_we_i),
        .wb_cyc_i       (wbs_d_idft_cyc_i),
        .wb_stb_i       (wbs_d_idft_stb_i),
        .wb_dat_o       (wbs_d_idft_dat_o),
        .wb_err_o       (),
        .wb_ack_o       (wbs_d_idft_ack_o),

        // Processor interrupt
        .int_o          ()
        
    );    */




generate
for (m = 0; m < NR_MASTERS; m = m + 1) begin : gen_busms_flat
assign busms_adr_o_flat[32*(m+1)-1:32*m] = busms_adr_o[m];
assign busms_cyc_o_flat[m] = busms_cyc_o[m];
assign busms_dat_o_flat[32*(m+1)-1:32*m] = busms_dat_o[m];
assign busms_sel_o_flat[4*(m+1)-1:4*m] = busms_sel_o[m];
assign busms_stb_o_flat[m] = busms_stb_o[m];
assign busms_we_o_flat[m] = busms_we_o[m];
assign busms_cab_o_flat[m] = busms_cab_o[m];
assign busms_cti_o_flat[3*(m+1)-1:3*m] = busms_cti_o[m];
assign busms_bte_o_flat[2*(m+1)-1:2*m] = busms_bte_o[m];
assign busms_ack_i[m] = busms_ack_i_flat[m];
assign busms_rty_i[m] = busms_rty_i_flat[m];
assign busms_err_i[m] = busms_err_i_flat[m];
assign busms_dat_i[m] = busms_dat_i_flat[32*(m+1)-1:32*m];
end
for (s = 0; s < NR_SLAVES; s = s + 1) begin : gen_bussl_flat
assign bussl_adr_i[s] = bussl_adr_i_flat[32*(s+1)-1:32*s];
assign bussl_cyc_i[s] = bussl_cyc_i_flat[s];
assign bussl_dat_i[s] = bussl_dat_i_flat[32*(s+1)-1:32*s];
assign bussl_sel_i[s] = bussl_sel_i_flat[4*(s+1)-1:4*s];
assign bussl_stb_i[s] = bussl_stb_i_flat[s];
assign bussl_we_i[s] = bussl_we_i_flat[s];
assign bussl_cab_i[s] = bussl_cab_i_flat[s];
assign bussl_cti_i[s] = bussl_cti_i_flat[3*(s+1)-1:3*s];
assign bussl_bte_i[s] = bussl_bte_i_flat[2*(s+1)-1:2*s];
assign bussl_ack_o_flat[s] = bussl_ack_o[s];
assign bussl_rty_o_flat[s] = bussl_rty_o[s];
assign bussl_err_o_flat[s] = bussl_err_o[s];
assign bussl_dat_o_flat[32*(s+1)-1:32*s] = bussl_dat_o[s];
end
endgenerate


 aes_top aes_top_inst
(
.wb_clk_i(clk_i),
.wb_rst_i(rst_ni),
.wb_adr_i(bussl_adr_i[SLAVE_AES_TOP]),
.wb_cyc_i(bussl_cyc_i[SLAVE_AES_TOP]),
.wb_dat_i(bussl_dat_i[SLAVE_AES_TOP]),
.wb_sel_i(bussl_sel_i[SLAVE_AES_TOP]),
.wb_stb_i(bussl_stb_i[SLAVE_AES_TOP]),
.wb_we_i(bussl_we_i[SLAVE_AES_TOP]),
.wb_ack_o(bussl_ack_o[SLAVE_AES_TOP]),
.wb_dat_o(bussl_dat_o[SLAVE_AES_TOP]),
.wb_err_o(bussl_err_o[SLAVE_AES_TOP])
);


  picorv32_wb RV32
(
.wb_clk_i(clk_i),
.wb_rst_i(rst_ni),
.wbm_ack_i(busms_ack_i_flat),
.wbm_dat_i(busms_dat_i_flat),
.wbm_adr_o(busms_adr_o_flat),
.wbm_cyc_o(busms_cyc_o_flat),
.wbm_dat_o(busms_dat_o_flat),
.wbm_sel_o(busms_sel_o_flat),
.wbm_stb_o(busms_stb_o_flat),
.wbm_we_o(busms_we_o_flat)
);




wb_bus_b3
     #(.MASTERS(NR_MASTERS),.SLAVES(NR_SLAVES),
       .S0_ENABLE(1),
       .S0_RANGE_WIDTH(1),.S0_RANGE_MATCH(1'b0)

	  )
   u_bus(
         // Outputs
         .m_dat_o                       (busms_dat_i_flat),      
         .m_ack_o                       (busms_ack_i_flat),      
         .m_err_o                       (busms_err_i_flat),      
         .m_rty_o                       (busms_rty_i_flat),      
         .s_adr_o                       (bussl_adr_i_flat),      
         .s_dat_o                       (bussl_dat_i_flat),      
         .s_cyc_o                       (bussl_cyc_i_flat),      
         .s_stb_o                       (bussl_stb_i_flat),      
         .s_sel_o                       (bussl_sel_i_flat),      
         .s_we_o                        (bussl_we_i_flat),       
         .s_cti_o                       (bussl_cti_i_flat),      
         .s_bte_o                       (bussl_bte_i_flat),      
         .snoop_adr_o                   (snoop_adr),             
         .snoop_en_o                    (snoop_enable),          
         .bus_hold_ack                  (),                      
         // Inputs
         .clk_i                         (clk_i),                   
         .rst_i                         (rst_ni),               
         .m_adr_i                       (busms_adr_o_flat),      
         .m_dat_i                       (busms_dat_o_flat),      
         .m_cyc_i                       (busms_cyc_o_flat),      
         .m_stb_i                       (busms_stb_o_flat),      
         .m_sel_i                       (busms_sel_o_flat),      
         .m_we_i                        (busms_we_o_flat),       
         .m_cti_i                       (busms_cti_o_flat),      
         .m_bte_i                       (busms_bte_o_flat),      
         .s_dat_i                       (bussl_dat_o_flat),      
         .s_ack_i                       (bussl_ack_o_flat),      
         .s_err_i                       (bussl_err_o_flat),      
         .s_rty_i                       (bussl_rty_o_flat),      
         .bus_hold                      (1'b0)
		 );                         

 
    
    

endmodule   // end aes_top_axi4lite
