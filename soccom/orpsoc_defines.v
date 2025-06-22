`ifdef SYNTHESIS
    `define RESET_HIGH
`endif

// Define the Address and Data widths
`define CEP_AXI_ADDR_WIDTH  32
`define CEP_AXI_DATA_WIDTH  32

// Define the numnber of AXI4-Lite slaves (cores) in the CEP
`define CEP_NUM_OF_SLAVES   0
`define CEP_NUM_OF_MASTERS  9

// Set the default address mask for the AXI4-Lite Arbiter
`define CEP_ADDRESS_MASK    32'hFF00_0000

// Constants used to increase readbility
`define CEP_SLAVE_ENABLED   32'h0000_0001
`define CEP_SLAVE_DISABLED   32'h0000_0000

parameter [31:0] cep_routing_rules [`CEP_NUM_OF_SLAVES - 1:0][0:2] = '{
};



`define CEP_RAM_SIZE        32'h00000000 // Size of RAM
