`include "orpsoc-defines.sv"
import axi_pkg::*;

`timescale 1 ns / 1 ps
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


`define PICORV32_V


module axisoc_top (

sys_clk_in_p,
sys_clk_in_n,

`ifdef RESET_HIGH
    rst_pad_i
`else
    rst_n_pad_i
`endif
);

input    sys_clk_in_p;
input    sys_clk_in_n;

`ifdef RESET_HIGH
    input    rst_pad_i;
`else
    input    rst_n_pad_i;
`endif




wire    core_clk;
wire    core_rst;
