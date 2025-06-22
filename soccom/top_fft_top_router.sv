module top_fft_top_router
import optimsoc_functions::*;
import opensocdebug::mor1kx_trace_exec;
import dii_package::dii_flit;
import optimsoc_config::*;

#(
parameter VCHANNELS = 2,
parameter INPUTS = 4,
parameter OUTPUTS = 4,
parameter FLIT_WIDTH = 32,
parameter USE_DEBUG = 0,
parameter ENABLE_VCHANNELS = 0,
parameter integer NUM_CORES = 1 * 1,
parameter integer LMEM_SIZE = 32 * 1024
 )
(
input clk,
input rst,
input [OUTPUTS-3:0] [VCHANNELS-1:0] out_ready,
input [INPUTS-3:0] [FLIT_WIDTH-1:0] in_flit,
input [INPUTS-3:0]  in_last,
input [INPUTS-3:0] [VCHANNELS-1:0] in_valid,
output [OUTPUTS-3:0] [FLIT_WIDTH-1:0] out_flit,
output [OUTPUTS-3:0]  out_last,
output [OUTPUTS-3:0] [VCHANNELS-1:0] out_valid,
output [INPUTS-3:0] [VCHANNELS-1:0] in_ready
);


logic rst_cpu;
logic rst_sys;


   localparam base_config_t
     BASE_CONFIG = '{ NUMTILES: 'x,
                      NUMCTS: 'x,
                      CTLIST: {{60{16'dx}}, 16'd0, 16'd1, 16'd2, 16'd3, 16'd4, 16'd5, 16'd6, 16'd7, 16'd8},
                      CORES_PER_TILE: NUM_CORES,
                      GMEM_SIZE: 0,
                      GMEM_TILE: 'x,
                      NOC_ENABLE_VCHANNELS: ENABLE_VCHANNELS,
                      LMEM_SIZE: LMEM_SIZE,
                      LMEM_STYLE: PLAIN,
                      ENABLE_BOOTROM: 0,
                      BOOTROM_SIZE: 0,
                      ENABLE_DM: 1,
                      DM_BASE: 32'h0,
                      DM_SIZE: LMEM_SIZE,
                      ENABLE_PGAS: 0,
                      PGAS_BASE: 0,
                      PGAS_SIZE: 0,
                      NA_ENABLE_MPSIMPLE: 1,
                      NA_ENABLE_DMA: 1,
                      NA_DMA_GENIRQ: 1,
                      NA_DMA_ENTRIES: 4,
                      USE_DEBUG: 0'(USE_DEBUG),
                      DEBUG_STM: 0,
                      DEBUG_CTM: 0,
                      DEBUG_SUBNET_BITS: 0,
                      DEBUG_LOCAL_SUBNET: 0,
                      DEBUG_ROUTER_BUFFER_SIZE: 0,
                      DEBUG_MAX_PKT_LEN: 0
                      };

   localparam config_t CONFIG = derive_config(BASE_CONFIG);

wire [OUTPUTS-3:0] [VCHANNELS-1:0] link_out_ready;
wire [INPUTS-3:0] [FLIT_WIDTH-1:0] link_in_flit;
wire [INPUTS-3:0]  link_in_last;
wire [INPUTS-3:0] [VCHANNELS-1:0] link_in_valid;
wire [OUTPUTS-3:0] [FLIT_WIDTH-1:0] link_out_flit;
wire [OUTPUTS-3:0]  link_out_last;
wire [OUTPUTS-3:0] [VCHANNELS-1:0] link_out_valid;
wire [INPUTS-3:0] [VCHANNELS-1:0] link_in_ready;


noc_router
#(.VCHANNELS (2),
.INPUTS (4),
.OUTPUTS (4),
.DESTS (32))

noc_router_compute_tile_dm_fft_top(
.clk (clk),
.rst (rst),
.out_ready ({out_ready,link_out_ready}),
.in_flit ({in_flit,link_in_flit}),
.in_last ({in_last,link_in_last}),
.in_valid ({in_valid,link_in_valid}),
.out_flit ({out_flit,link_out_flit}),
.out_last ({out_last,link_out_last}),
.out_valid ({out_valid,link_out_valid}),
.in_ready ({in_ready,link_in_ready}));


compute_tile_dm_fft_top
#(.CONFIG(CONFIG),
.ID(1),
.COREBASE(1*CONFIG.CORES_PER_TILE),
.DEBUG_BASEID((CONFIG.DEBUG_LOCAL_SUBNET << (16 - CONFIG.DEBUG_SUBNET_BITS))+ 1 + (1*CONFIG.DEBUG_MODS_PER_TILE)))

compute_tile_dm_fft_top_inst(
.clk (clk),
.rst_cpu (rst_cpu),
.rst_sys (rst_sys),
.noc_in_flit (link_out_flit),
.noc_in_last (link_out_last),
.noc_in_valid (link_out_valid),
.noc_out_ready (link_in_ready),
.noc_in_ready (link_out_ready),
.noc_out_flit (link_in_flit),
.noc_out_last (link_in_last),
.noc_out_valid (link_in_valid));


endmodule
