//
// Copyright (C) 2018 Massachusetts Institute of Technology
//
// File         : mor1kx_top_axi4lite.v
// Project      : Common Evaluation Platform (CEP)
// Description  : This file provides an axi4-lite wrapper for the wishbone based-MOR1KX processor
//

`timescale 1 ns / 1 ps
// `default_nettype none
// `define DEBUGNETS
// `define DEBUGREGS
// `define DEBUGASM
// `define DEBUG

`ifdef DEBUG
  `define debug(debug_command) debug_command
`else
  `define debug(debug_command)
`endif

`ifdef FORMAL
  `define FORMAL_KEEP (* keep *)
  `define assert(assert_expr) assert(assert_expr)
`else
  `ifdef DEBUGNETS
    `define FORMAL_KEEP (* keep *)
  `else
    `define FORMAL_KEEP
  `endif
  `define assert(assert_expr) empty_statement
`endif

// uncomment this for register file in extra module
// `define PICORV32_REGS picorv32_regs

// this macro can be used to check if the verilog files in your
// design are read in the correct order.
`define PICORV32_V


module picorv32_top_axi4lite (
    
    // Clock and Resets
    input                                   clk_i,
    input                                   rst_i,

    // AXI4-Lite Instruction and Data master interfaces
    AXI_LITE.Master                            master_d 
    

    // MOR1KX Interrupts
   /* input [31:0]                            mor1kx_pic_ints,

    // MOR1KX Debug interface
    input [15:0]                            mor1kx_dbg_adr_i,
    input                                   mor1kx_dbg_stb_i,
    input [master_i.AXI_DATA_WIDTH-1:0]     mor1kx_dbg_dat_i,
    input                                   mor1kx_dbg_we_i,
    output [master_i.AXI_DATA_WIDTH-1:0]    mor1kx_dbg_dat_o,
    output                                  mor1kx_dbg_ack_o,
    input                                   mor1kx_dbg_stall_i,
    output                                  mor1kx_dbg_stall_o   */
 
);

    // mor1kx wishbone instruction bus wires
   /* wire [master_i.AXI_ADDR_WIDTH-1:0]      wbm_i_or1k_adr_o;
    wire [master_i.AXI_DATA_WIDTH-1:0]      wbm_i_or1k_dat_o;
    wire [3:0]                              wbm_i_or1k_sel_o;
    wire                                    wbm_i_or1k_we_o;
    wire                                    wbm_i_or1k_cyc_o;
    wire                                    wbm_i_or1k_stb_o;
    wire [2:0]                              wbm_i_or1k_cti_o;
    wire [1:0]                              wbm_i_or1k_bte_o;
    wire [master_i.AXI_DATA_WIDTH-1:0]      wbm_i_or1k_dat_i;
    wire                                    wbm_i_or1k_ack_i;
    wire                                    wbm_i_or1k_err_i;
    wire                                    wbm_i_or1k_rty_i;
    
    // mor1kx wishbone data bus wires
    wire [master_d.AXI_ADDR_WIDTH-1:0]      wbm_d_or1k_adr_o;
    wire [master_d.AXI_DATA_WIDTH-1:0]      wbm_d_or1k_dat_o;
    wire [3:0]                              wbm_d_or1k_sel_o;
    wire                                    wbm_d_or1k_we_o;
    wire                                    wbm_d_or1k_cyc_o;
    wire                                    wbm_d_or1k_stb_o;
    wire [2:0]                              wbm_d_or1k_cti_o;
    wire [1:0]                              wbm_d_or1k_bte_o;
    wire [master_i.AXI_DATA_WIDTH-1:0]      wbm_d_or1k_dat_i;
    wire                                    wbm_d_or1k_ack_i;
    wire                                    wbm_d_or1k_err_i;
    wire                                    wbm_d_or1k_rty_i;   */

    // Instantiate the PICORV32
    // Parameter overrides are used to force non-bursting WB behavior as
    // bursts are NOT supported by AXI4-Lite
 picoaxi #(
    .ENABLE_COUNTERS (),
	.ENABLE_COUNTERS64 (),
	.ENABLE_REGS_16_31 (),
	.ENABLE_REGS_DUALPORT (),
	.TWO_STAGE_SHIFT(),
	.BARREL_SHIFTER (),
	.TWO_CYCLE_COMPARE (),
	.TWO_CYCLE_ALU (),
	.COMPRESSED_ISA (),
	.CATCH_MISALIGN (),
	.CATCH_ILLINSN (),
	.ENABLE_PCPI (),
	.ENABLE_MUL (),
	.ENABLE_FAST_MUL (),
	.ENABLE_DIV (),
	.ENABLE_IRQ (),
    .ENABLE_IRQ_QREGS (),
	.ENABLE_IRQ_TIMER (),
	.ENABLE_TRACE (),
	.REGS_INIT_ZERO (),
	.MASKED_IRQ (),
	.LATCHED_IRQ (),
	.PROGADDR_RESET (),
	.PROGADDR_IRQ (),
	.STACKADDR ()
    ) 
   
   
picoaxi_inst (

	.clk_i (clk_i),
	.rst_i (rst_i),
	


	// AXI4-lite master memory interface 

	.mem_axi_awvalid (master_d.aw_valid),
	.mem_axi_awready (master_d.aw_ready),
	.mem_axi_awaddr (master_d.aw_addr),
	.mem_axi_awprot(),

	.mem_axi_wvalid (master_d.w_valid),
	.mem_axi_wready (master_d.w_ready),
	.mem_axi_wdata (master_d.w_data),
	.mem_axi_bvalid (master_d.b_valid),
	.mem_axi_bready (master_d.b_ready),

	.mem_axi_arvalid (master_d.ar_valid),
	.mem_axi_arready (master_d.ar_ready),
	.mem_axi_araddr (master_d.ar_addr),
	.mem_axi_arprot (),

	.mem_axi_rvalid (master_d.r_valid),
	.mem_axi_rready (master_d.r_ready),
	.mem_axi_rdata (master_d.r_data)
	
	 
        

/*	// Pico Co-Processor Interface (PCPI) (Unused)
	.pcpi_valid (),
	.pcpi_insn (),
	.pcpi_rs1 (),
	.pcpi_rs2 (),
	.pcpi_wr (),
	.pcpi_rd (),
	.pcpi_wait (),
	.pcpi_ready (),

	// IRQ interface
	.irq (),
	.eoi (),

`ifdef RISCV_FORMAL
	rvfi_valid (),
	rvfi_order (),
	rvfi_insn (),
	rvfi_trap (),
	rvfi_halt (),
	rvfi_intr (),
	rvfi_rs1_addr (),
	rvfi_rs2_addr (),
	rvfi_rs1_rdata (),
	rvfi_rs2_rdata (),
	rvfi_rd_addr (),
	rvfi_rd_wdata (),
	rvfi_pc_rdata (),
	rvfi_pc_wdata (),
	rvfi_mem_addr (), 
	rvfi_mem_rmask (),
	rvfi_mem_wmask (),
	rvfi_mem_rdata (),
	rvfi_mem_wdata ()
`endif

	// Trace Interface
	.trace_valid (),
	.trace_data () */
);
 

endmodule // picorv32_axi4lite