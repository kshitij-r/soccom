

module compute_tile_dm_idft_top_top
   import dii_package::dii_flit;
   import opensocdebug::mor1kx_trace_exec;
   import optimsoc_config::*;
  #(
    parameter config_t CONFIG = 'x,

    parameter ID       = 'x,
    parameter COREBASE = 'x,

    parameter DEBUG_BASEID = 'x,

    parameter MEM_FILE = 'x,

    localparam CHANNELS = CONFIG.NOC_CHANNELS,
    localparam FLIT_WIDTH = CONFIG.NOC_FLIT_WIDTH
    )
   (
   input                                 dii_flit [1:0] debug_ring_in,
   output [1:0]                          debug_ring_in_ready,
   output                                dii_flit [1:0] debug_ring_out,
   input [1:0]                           debug_ring_out_ready,

   output [31:0]                         wb_ext_adr_i,
   output                                wb_ext_cyc_i,
   output [31:0]                         wb_ext_dat_i,
   output [3:0]                          wb_ext_sel_i,
   output                                wb_ext_stb_i,
   output                                wb_ext_we_i,
   output                                wb_ext_cab_i,
   output [2:0]                          wb_ext_cti_i,
   output [1:0]                          wb_ext_bte_i,
   input                                 wb_ext_ack_o,
   input                                 wb_ext_rty_o,
   input                                 wb_ext_err_o,
   input [31:0]                          wb_ext_dat_o,

   input                                 clk,
   input                                 rst_cpu, rst_sys, rst_dbg,

   input [CHANNELS-1:0][FLIT_WIDTH-1:0]  noc_in_flit,
   input [CHANNELS-1:0]                  noc_in_last,
   input [CHANNELS-1:0]                  noc_in_valid,
   output [CHANNELS-1:0]                 noc_in_ready,
   output [CHANNELS-1:0][FLIT_WIDTH-1:0] noc_out_flit,
   output [CHANNELS-1:0]                 noc_out_last,
   output [CHANNELS-1:0]                 noc_out_valid,
   input [CHANNELS-1:0]                  noc_out_ready
   );

   import optimsoc_functions::*;

   
   localparam NR_SLAVES = 4;
   localparam SLAVE_DM   = 0;
   localparam SLAVE_PGAS = 1;
   localparam SLAVE_NA   = 2;
   localparam SLAVE_BOOT = 3;


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

   wire [31:0]   pic_ints_i [0:CONFIG.CORES_PER_TILE-1];
   assign pic_ints_i[0][31:4] = 28'h0;
   assign pic_ints_i[0][1:0] = 2'b00;

   genvar        c, m, s;



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

   generate


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



wire         wbm_cyc_o, wbm_stb_o, wbm_we_o, wbm_ack_i, wbm_err_i;
wire [31:0]  wbm_dat_o, wb_dat_i;
wire [31:0]   wb_dat_o, wbm_dat_i;
wire [31:0]   wbm_adr_o, wb_adr_i;
wire [3:0]   wbm_sel_o, wb_sel_i;
 
 
wire  wb_clk_i, wb_rst_i, wb_we_i, wb_stb_i, wb_cyc_i,  wb_ack_o;
  
 assign wb_cyc_i = wbm_cyc_o;
 assign wb_ack_o = wbm_ack_i;
 assign wb_dat_o = wbm_dat_i;
 assign wb_stb_i = wbm_stb_o;
 assign wb_we_i = wbm_we_o;
 assign wb_dat_i = wbm_dat_o;
 assign wb_adr_i = wbm_adr_o;





   
   
   
  idft_top_top idft_top_top_inst
     (
        
        .wb_clk_i(clk),
        .wb_rst_i(rst_sys),
        .wb_dat_i(wbm_dat_o),
        .wb_adr_i(wbm_adr_o),
       
        .wb_we_i (wbm_we_o),
        .wb_cyc_i(wbm_cyc_o),
        .wb_stb_i(wbm_stb_o),
        .wb_dat_o(wbm_dat_i),
        .wb_err_o(wbm_err_i),
        .wb_ack_o(wbm_ack_i)
   
      );   
     

   
networkadapter_ct
      #(.CONFIG(CONFIG),
        .TILEID(ID),
        .COREBASE(COREBASE))
      idft_top_top_na(
`ifdef OPTIMSOC_CLOCKDOMAINS
`ifdef OPTIMSOC_CDC_DYNAMIC
           .cdc_conf                     (cdc_conf[2:0]),
           .cdc_enable                   (cdc_enable),
`endif
`endif
           
           .noc_in_ready                (noc_in_ready),
           .noc_out_flit                (noc_out_flit),
           .noc_out_last                (noc_out_last),
           .noc_out_valid               (noc_out_valid),
           .wbm_adr_o                   (wbm_adr_o),
           .wbm_cyc_o                   (wbm_cyc_o),
           .wbm_dat_o                   (wbm_dat_o),
           .wbm_sel_o                   (wbm_sel_o),
           .wbm_stb_o                   (wbm_stb_o),
           .wbm_we_o                    (wbm_we_o),
           
          
          
           .wbs_ack_o                   (bussl_ack_o[SLAVE_NA]),
           .wbs_rty_o                   (bussl_rty_o[SLAVE_NA]),
           .wbs_err_o                   (bussl_err_o[SLAVE_NA]),
           .wbs_dat_o                   (bussl_dat_o[SLAVE_NA]),
           .irq                         (pic_ints_i[0][3:2]),
           
           .clk                         (clk),
           .rst                         (rst_sys),
           .noc_in_flit                 (noc_in_flit),
           .noc_in_last                 (noc_in_last),
           .noc_in_valid                (noc_in_valid),
           .noc_out_ready               (noc_out_ready),
           .wbm_ack_i                   (wbm_ack_i),
           
           .wbm_err_i                   (wbm_err_i),
           .wbm_dat_i                   (wbm_dat_i),
           .wbs_adr_i                   (bussl_adr_i[SLAVE_NA]),
           .wbs_cyc_i                   (bussl_cyc_i[SLAVE_NA]),
           .wbs_dat_i                   (bussl_dat_i[SLAVE_NA]),
           .wbs_sel_i                   (bussl_sel_i[SLAVE_NA]),
           .wbs_stb_i                   (bussl_stb_i[SLAVE_NA]),
           .wbs_we_i                    (bussl_we_i[SLAVE_NA]),
           .wbs_cab_i                   (bussl_cab_i[SLAVE_NA]),
           .wbs_cti_i                   (bussl_cti_i[SLAVE_NA]),
           .wbs_bte_i                   (bussl_bte_i[SLAVE_NA])
           );

   
endmodule
