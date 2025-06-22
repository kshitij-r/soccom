import os
import json
import SoC_generic_AXI
from SoC_generic_AXI import *

def define_generator(base_dir, in_json_file):
    soc_connections_gen = None
    slave_count = 0
    master_count = 0
    val_count = 0
    ram_size = 0
    CEP_ADDRESS_MASK   = "32'hFF00_0000"
    CEP_SLAVE_ENABLED  = "32'h0000_0001"
    CEP_SLAVE_DISABLED = "32'h0000_0000"
    slave_list = []
    base_address = []
    val_spec = "'{"
    slave = ""
    
    with open(os.path.join(base_dir, in_json_file)) as file:
        try:
            soc_connections_gen = json.load(file)
        except ValueError as e:
            print(e) 
    
    for key in soc_connections_gen.keys():
        value = soc_connections_gen[key]
        if(value['config'] == 'MASTER' and value['bus_type']=='AXI'):
            master_count+=1

        if(value['config']=='SLAVE' and value['bus_type']=='AXI'):
            slave = value['IP_name']
            if ('ram' in slave):
                ram_size = value['size']
            base_address.append(value['base_address'])
            if('clkgen' in slave):
                slave_list.append(slave.split('.')[0])    
            else:
                slave_list.append(slave.split('_')[0])          
    slave_count = len(slave_list)
           
    generated_defines_filename = "orpsoc_defines_latest.v"
    
    with open(os.path.join(base_dir, generated_defines_filename), 'w') as file:
        file.write(f"{'`ifdef SYNTHESIS'}\n")
        file.write(f"{'    `define RESET_HIGH'}\n")
        file.write(f"{'`endif'}\n")
        file.write('\n')
        file.write(f"{'// Define the Address and Data widths'}\n")
        file.write(f"{'`define CEP_AXI_ADDR_WIDTH  32'}\n")
        file.write(f"{'`define CEP_AXI_DATA_WIDTH  32'}\n")
        file.write('\n')
        file.write(f"{'// Define the numnber of AXI4-Lite slaves (cores) in the CEP'}\n")
        file.write(f"{'`define CEP_NUM_OF_SLAVES   '}{slave_count}\n")
        file.write(f"{'`define CEP_NUM_OF_MASTERS  '}{master_count}\n")
        file.write('\n')
        file.write(f"{'// Set the default address mask for the AXI4-Lite Arbiter'}\n")
        file.write(f"{'`define CEP_ADDRESS_MASK    '}{CEP_ADDRESS_MASK}\n")
        file.write('\n')
        file.write(f"{'// Constants used to increase readbility'}\n")
        file.write(f"{'`define CEP_SLAVE_ENABLED   '}{CEP_SLAVE_ENABLED}\n")
        file.write(f"{'`define CEP_SLAVE_DISABLED   '}{CEP_SLAVE_DISABLED}\n")
        file.write("\n")
        file.write(f"{'parameter [31:0] cep_routing_rules [`CEP_NUM_OF_SLAVES - 1:0][0:2] = '}{val_spec}\n")
        file.write("\n")

        for x,y in zip(base_address,slave_list):
            if (val_count<slave_count-1):
                assignment = ""
                assignment = "    {" + "'`CEP_SLAVE_ENABLED, `CEP_ADDRESS_MASK, " + x + "}," + "    // Slave  " + str(val_count) + "   - " + y 
                val_count+=1
                file.write(str(assignment))
                file.write("\n") 

            elif (val_count == slave_count-1) :
                assignment = ""
                assignment = "    {" + "'`CEP_SLAVE_ENABLED, `CEP_ADDRESS_MASK, " + x + "}" + "     // Slave  " + str(val_count) + "   - " + y 
                file.write(str(assignment))
                file.write("\n")

        file.write("\n") 
        val_count=0
        file.write(f"{'};'}\n")
        file.write('\n\n')
        
        for i in slave_list:
            file.write(f"{'`define '}{i}{'_SLAVE_NUMBER   '}{'    '}{val_count}\n")
            val_count+=1
        
        file.write("\n")
        file.write(f"{'`define CEP_RAM_SIZE        '}{ram_size}{' // Size of RAM'}\n")
        file.write("\n")
        print('Configuration file generation successfull.')

if __name__ == '__main__':
    define_generator('/Users/kshitijraj/Study /SoC Compiler Tool', 'hybrid_wb.json')
