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


module orpsoc_top (

sys_clk_in_p,
sys_clk_in_n,
uart_srx_pad_i,
uart_cts_pad_i,
uart_stx_pad_o,
uart_rts_pad_o,

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


input    uart_srx_pad_i;
input    uart_cts_pad_i;
output    uart_stx_pad_o;
output    uart_rts_pad_o;


wire    core_clk;
wire    core_rst;
// AXI4-Lite declerations for both the Instruction and Data Buses 

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


// Instantiating AXI4Lite_2_Wishbone Bridge IP
axi4lite_2_wb axi4lite_2_wb_inst (
.clk_i    (core_clk),
.rst_ni    (~core_rst),
.slave    (slave[`IDFT_SLAVE_NUMBER])
);


// Instantiating Clock and Reset Generator IP
clkgen clkgen_inst (

.sys_clk_in_p    (sys_clk_in_p),
.sys_clk_in_n    (sys_clk_in_n),
.core_clk_o    (core_clk),
.core_rst_o    (core_rst)
);

// Instantiating RAM IP
ram_top_axi4lite # (
    .MEMORY_SIZE(`CEP_RAM_SIZE)
) ram_top_axi4lite_inst (
.clk_i    (core_clk),
.rst_ni    (~core_rst),
.slave    (slave[`RAM_SLAVE_NUMBER])
);


// Instantiating UART IP
wire    uart_irq;
uart_top_axi4lite uart_top_axi4lite_inst (

// UART Signals
.clk_i    (core_clk),
.rst_ni    (~core_rst),
.slave    (slave[`UART_SLAVE_NUMBER]),

.srx_pad_i      (uart_srx_pad_i ),
.stx_pad_o      (uart_stx_pad_o ),
.rts_pad_o      (uart_rts_pad_o ),
.cts_pad_i      (uart_cts_pad_i ),
.dtr_pad_o      (               ),
.dsr_pad_i      (1'b0           ),
.ri_pad_i       (1'b0           ),
.dcd_pad_i      (1'b0           ),
// Processor Interrupt
.int_o          (uart_irq       )
);


// Instantiating PICORV IP
picorv32_top_axi4lite picorv32_top_axi4lite_inst (
.clk_i    (core_clk),
.rst_i    (core_rst),
.master_d    (master [0])
);


// Instantiating AES IP
generate
if(cep_routing_rules[`AES_SLAVE_NUMBER][0] == `CEP_SLAVE_ENABLED)
aes_top_axi4lite aes_top_axi4lite_inst (
.clk_i    (core_clk),
.rst_ni    (~core_rst),
.slave    (slave[`AES_SLAVE_NUMBER])

);
endgenerate

// Instantiating MD5 IP
generate
if(cep_routing_rules[`MD5_SLAVE_NUMBER][0] == `CEP_SLAVE_ENABLED)
md5_top_axi4lite md5_top_axi4lite_inst (
.clk_i    (core_clk),
.rst_ni    (~core_rst),
.slave    (slave[`MD5_SLAVE_NUMBER])

);
endgenerate

// Instantiating SHA256 IP
generate
if(cep_routing_rules[`SHA256_SLAVE_NUMBER][0] == `CEP_SLAVE_ENABLED)
sha256_top_axi4lite sha256_top_axi4lite_inst (
.clk_i    (core_clk),
.rst_ni    (~core_rst),
.slave    (slave[`SHA256_SLAVE_NUMBER])

);
endgenerate

// Instantiating RSA IP
generate
if(cep_routing_rules[`RSA_SLAVE_NUMBER][0] == `CEP_SLAVE_ENABLED)
rsa_top_axi4lite rsa_top_axi4lite_inst (
.clk_i    (core_clk),
.rst_ni    (~core_rst),
.slave    (slave[`RSA_SLAVE_NUMBER])

);
endgenerate

// Instantiating DES3 IP
generate
if(cep_routing_rules[`DES3_SLAVE_NUMBER][0] == `CEP_SLAVE_ENABLED)
des3_top_axi4lite des3_top_axi4lite_inst (
.clk_i    (core_clk),
.rst_ni    (~core_rst),
.slave    (slave[`DES3_SLAVE_NUMBER])

);
endgenerate

endmodule