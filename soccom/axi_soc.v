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
// AXI4-Lite declarations for both the Instruction and Data Buses

// Master Bus defininitions
// Master 0 - Instruction Bus
// Master 1 - Data Bus

AXI_LITE #(
    .AXI_ADDR_WIDTH (`CEP_AXI_ADDR_WIDTH),
    .AXI_DATA_WIDTH (`CEP_AXI_DATA_WIDTH)
) master[1:0]();


// Slave Bus Declaration (see orpsoc-defines.sv for additional info including slave assignment)

AXI_LITE #(
    .AXI_ADDR_WIDTH (`CEP_AXI_ADDR_WIDTH),
    .AXI_DATA_WIDTH (`CEP_AXI_DATA_WIDTH)
) slave[11:0]();

// Declaration the routing rules for the AXI4-Lite Crossbar

AXI_ROUTING_RULES #(
    .AXI_ADDR_WIDTH (`CEP_AXI_ADDR_WIDTH),
    .NUM_SLAVE      (`CEP_NUM_OF_SLAVES),
    .NUM_RULES      (1)
) routing();

// Assign the routing rules (cep_routing_rules is declared and explained in orpsoc-defines.v)

for (genvar i = 0; i < `CEP_NUM_OF_SLAVES; i++) begin
    assign routing.rules[i][0].enabled  = cep_routing_rules[i][0][0];
    assign routing.rules[i][0].mask     = cep_routing_rules[i][1];
    assign routing.rules[i][0].base     = cep_routing_rules[i][2];
end // for (genvar i = 0; i < CEP_NUM_OF_SLAVES; i++)



// Instantiate the AXI4-Lite crossbar

axi_lite_xbar #(
    .ADDR_WIDTH     (`CEP_AXI_ADDR_WIDTH ),
    .DATA_WIDTH     (`CEP_AXI_DATA_WIDTH ),
    .NUM_MASTER     (`CEP_NUM_OF_MASTERS ),
    .NUM_SLAVE      (`CEP_NUM_OF_SLAVES  ),
    .NUM_RULES      (1)
) axi_lite_xbar_inst (
    .clk_i          ( core_clk          ),
    .rst_ni         ( ~core_rst         ),
    .master         ( master            ),
    .slave          ( slave             ),
    .rules          ( routing           )
);


endmodule