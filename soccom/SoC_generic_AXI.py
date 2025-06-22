import os
import extract_IO
import interfaceIP_NA
import json
import SoC_generic
import gen_define

def soc_generator_AXI(base_dir, in_json_file):
    soc_connections = None
    soc_connections_hybrid = None
    wb_dict = None
    copy = None
    wb_top_module = []
    wb_is_router = []
    wb_is_master = []
    wb_is_slave = []
    wb_config = []
    endpoint = []
    endpoint_axi = []
    dict_list = []
    AXI_dict = None
    dict_list_axi = []
    soc_connections_axi = None
    axi_dict = []
    axi_ip_name = []
    axi_config = []
    axi_ip_type = []
    axi_size = []

    with open(os.path.join(base_dir, in_json_file)) as file:
        try:
            soc_connections_hybrid = json.load(file)
        except ValueError as e:
            print(e)
  
    for val in soc_connections_hybrid:
        for i in soc_connections_hybrid[val]:
        
            if (i == 'bus_type'):
                if (soc_connections_hybrid[val][i] == 'Wishbone'):
                    wb_top_module.append(soc_connections_hybrid[val]['IP_name'])
              
                if(soc_connections_hybrid[val][i] == 'AXI'):
                    axi_ip_name.append(soc_connections_hybrid[val]['IP_name'])
                    axi_config.append(soc_connections_hybrid[val]['config'])
                    axi_ip_type.append(soc_connections_hybrid[val]['IP_type'])
                    axi_size.append(soc_connections_hybrid[val]['size'])
                  
    string_axi = ''
    counter_axi = 0
    count_axi = 0

    for value in axi_ip_name:
        string_axi = 'EP_'+ str(counter_axi)
        counter_axi+=1
        endpoint_axi.append(string_axi)
    
    for j in endpoint_axi:
        dict_list_axi.append({"IP_name":axi_ip_name[count_axi],"config":axi_config[count_axi],
                    "IP_type":axi_ip_type[count_axi],
                    "size":axi_size[count_axi]
                })
        count_axi+=1
    
    AXI_dict = dict(zip(endpoint_axi,dict_list_axi))
    soc_connections = AXI_dict.copy()
    ip_list= [] # This list contains the filenames of the IPs.
    
    for i in soc_connections:
        for j in soc_connections[i]:
            if (j=='IP_name'):
                ip_list.append(soc_connections[i]['IP_name'])           

    generated_ip_filename = 'axi_soc.v'
    generated_ip_top_module_name = 'axisoc'
    sys_clk = ['sys_clk_in_p','sys_clk_in_n']
    core = ['core_clk', 'core_rst']
    reset = ['rst_pad_i','rst_n_pad_i']
    rst = []

    with open(os.path.join(base_dir, generated_ip_filename), 'w') as file:
        string = '`include "orpsoc-defines.sv"'
        file.write(str(string))
        file.write('\n')
        file.write(f"{'import axi_pkg::*;'}\n")
        file.write('\n')
        file.write(f"{'`timescale 1 ns / 1 ps'}\n")
        file.write(f"{'`ifdef FORMAL'}\n")
        file.write(f"{'    `define FORMAL_KEEP (* keep *)'}\n")
        file.write(f"{'    `define assert(assert_expr) assert(assert_expr)'}\n")
        file.write(f"{'`else'}\n")
        file.write(f"{'    `ifdef DEBUGNETS'}\n")
        file.write(f"{'       `define FORMAL_KEEP (* keep *)'}\n")
        file.write(f"{'    `else'}\n")
        file.write(f"{'       `define FORMAL_KEEP'}\n")
        file.write(f"{'    `endif'}\n")
        file.write(f"{'    `define assert(assert_expr) empty_statement'}\n")
        file.write(f"{'    `endif'}\n")
        file.write('\n\n')
        file.write(f"{'`define PICORV32_V'}\n")
        file.write('\n\n')
        file.write(f"{'module '}{generated_ip_top_module_name}{'_top ('}\n")
        file.write('\n')
        
        for i in sys_clk:
            file.write(str(i))
            file.write(',')
            file.write('\n')

        for i in ip_list:
            if ('uart' in i):
                uart = extract_IO.ExtractRtl(base_dir, i)
                uart.extract_io()
                uart_input = list(uart.inputs)
                uart_output = list(uart.outputs)
                
                for j in uart_input:
                    if ('srx_pad_i' in j[1]):
                        file.write(f"{'uart_'}{j[1]}{','}\n")
                    if ('cts_pad_i' in j[1]):
                        file.write(f"{'uart_'}{j[1]}{','}\n")
                
                for k in uart_output:
                    if ('stx_pad_o' in k[1]):
                        file.write(f"{'uart_'}{k[1]}{','}\n")
                    if ('rts_pad_o' in k[1]):
                        file.write(f"{'uart_'}{k[1]}{','}\n")    

        file.write('\n')
        file.write(f"{'`ifdef RESET_HIGH'}\n")
        file.write(f"{'    rst_pad_i'}\n")
        file.write(f"{'`else'}\n")
        file.write(f"{'    rst_n_pad_i'}\n")
        file.write(f"{'`endif'}\n")
        file.write(f"{');'}")  

        file.write('\n\n')    
        for i in sys_clk:
            file.write(f"{'input    '}{i}{';'}\n")

        file.write('\n')
        file.write(f"{'`ifdef RESET_HIGH'}\n")
        file.write(f"{'    input    '}{reset[0]}{';'}\n")
        file.write(f"{'`else'}\n")
        file.write(f"{'    input    '}{reset[1]}{';'}\n")
        file.write(f"{'`endif'}\n")
        file.write('\n\n')
        
        for i in ip_list:
            if ('uart' in i):
                uart = extract_IO.ExtractRtl(base_dir, i)
                uart.extract_io()
                uart_input = list(uart.inputs)
                uart_output = list(uart.outputs)
                
                for j in uart_input:
                    if ('srx_pad_i' in j[1]):
                        file.write(f"{'input    '}{'uart_'}{j[1]}{';'}\n")
                    if ('cts_pad_i' in j[1]):
                        file.write(f"{'input    '}{'uart_'}{j[1]}{';'}\n")
                
                for k in uart_output:
                    if ('stx_pad_o' in k[1]):
                        file.write(f"{'output    '}{'uart_'}{k[1]}{';'}\n")
                    if ('rts_pad_o' in k[1]):
                        file.write(f"{'output    '}{'uart_'}{k[1]}{';'}\n")

        file.write('\n\n')
        
        for i in core:
            file.write(f"{'wire    '}{i}{';'}\n")
        
        f=open('axi_init.txt')  
        for x in f.readlines():
            file.write(x)
        f.close()
        file.write('\n\n')
        
        # Clock generator module
        clock = extract_IO.ExtractRtl(base_dir, 'clkgen.v')
        clock.extract_io()
        clock_input = list(clock.inputs)
        clock_output = list(clock.outputs)
        
    # Instantiate the AXI Crossbar 
        # Hardcoding this because this will never change and always exist
        file.write('\n')
        file.write(f"{'// Instantiate the AXI4-Lite crossbar'}\n")
        file.write('\n')
        file.write(f"{'axi_lite_xbar #('}\n")
        file.write(f"{'    .ADDR_WIDTH     (`CEP_AXI_ADDR_WIDTH ),'}\n")
        file.write(f"{'    .DATA_WIDTH     (`CEP_AXI_DATA_WIDTH ),'}\n")
        file.write(f"{'    .NUM_MASTER     (`CEP_NUM_OF_MASTERS ),'}\n")
        file.write(f"{'    .NUM_SLAVE      (`CEP_NUM_OF_SLAVES  ),'}\n")
        file.write(f"{'    .NUM_RULES      (1)'}\n")
        file.write(f"{') axi_lite_xbar_inst ('}\n")
        file.write(f"{'    .clk_i          ( core_clk          ),'}\n")
        file.write(f"{'    .rst_ni         ( ~core_rst         ),'}\n")
        file.write(f"{'    .master         ( master            ),'}\n")
        file.write(f"{'    .slave          ( slave             ),'}\n")
        file.write(f"{'    .rules          ( routing           )'}\n")
        file.write(f"{');'}\n")
        file.write('\n\n')

        #Instantiating the master IP
        master_list = []  #contains only the names of IPs that are in master configuration
        for i in soc_connections:
            for j in soc_connections[i]:
                if (j=='config'):
                    if(soc_connections[i][j]=='MASTER'):
                        #print(soc_connections[i]['IP_name'])
                        if(soc_connections[i]['IP_name'].endswith('.sv')):
                            master_list.append(soc_connections[i]['IP_name'].split('_')[0])
    
        ip_print_name= []
        # Instantiating the IP Modules
        for name_of_ip in ip_list:
            if name_of_ip.endswith('.v'):
                ip_print_name.append(name_of_ip[0:-2].upper())
            elif name_of_ip.endswith('sv'):
                ip_print_name.append(name_of_ip[0:-3].upper())
            else:
                print('Please provide IPs in .v or .sv!')
        
            ipname=name_of_ip   
            ip_val = extract_IO.ExtractRtl(base_dir, ipname)
            ip_val.extract_io()
            ip_val.extract_param()
            ipval_ip = list(ip_val.inputs)
            ipval_op = list(ip_val.outputs)
            cores = []
            ip_clk = []
            ip_rst = []
            name = ''          
        
            # Clock generator module
            if ('clkgen' in name_of_ip):
                display = []
                file.write(f"{'// Instantiating Clock and Reset Generator IP'}\n")
                file.write(f"{name_of_ip[:-2]}{' '}{name_of_ip[:-2]}{'_inst'}{' ('}\n")
                file.write('\n')
                for i in ipval_ip:
                    if ('clk' in i[1]):
                        file.write(f"{'.'}{i[1]}{'    '}{'('}{i[1]}{'),'}\n")
                for j in ipval_op:
                    if ('core' in j[1]):
                        cores.append(j[1])   
                        core_final = sorted(cores)
                for z in ipval_ip:
                    if ('rst' in z[1]):
                        rst.append(z[1])
                counter = 0
                for x,y in zip(core_final,core):
                    display_str = '.' + x + '    ' + '(' + y + ')'
                    if (counter == 0):
                        file.write(f"{display_str}{','}\n")
                        counter+=1
                    else:
                        file.write(f"{display_str}\n")
                file.write(');')
                file.write('\n\n')
            # Clock generator module ends

    # Instantiating the AXI_2_Wishbone Bridge IP.
            elif('2_wb' in name_of_ip):
                file.write(f"{'// Instantiating AXI4Lite_2_Wishbone Bridge IP'}\n")
                file.write(f"{name_of_ip[:-3]}{' '}{name_of_ip[:-3]}{'_inst'}{' ('}\n")
                for i in ipval_ip:
                    if ('clk' in i[1]):
                        ip_clk.append(i[1])
                    if ('rst' in i[1]):
                        ip_rst.append(i[1])
                file.write(f"{'.'}{ip_clk[0]}{'    '}{'(core_clk),'}\n")
                file.write(f"{'.'}{ip_rst[0]}{'    '}{'(~core_rst),'}\n")                         
                file.write(f"{'.'}{'slave'}{'    '}{'(slave[`IDFT_SLAVE_NUMBER])'}\n")
                file.write(f"{');'}\n")
                file.write('\n\n')
     
    # Instantiating the other IP Blocks.
            # First instantiate the master IP (PICORV_32)
            elif ('pico' in name_of_ip):
                file.write(f"{'// Instantiating PICORV IP'}\n")
                file.write(f"{name_of_ip[:-3]}{' '}{name_of_ip[:-3]}{'_inst'}{' ('}\n")
                for i in ipval_ip:
                    if ('clk' in i[1]):
                        ip_clk.append(i[1])
                    if ('rst' in i[1]):
                        ip_rst.append(i[1])
                file.write(f"{'.'}{ip_clk[0]}{'    '}{'(core_clk),'}\n")
                file.write(f"{'.'}{ip_rst[0]}{'    '}{'(core_rst),'}\n")                         
                file.write(f"{'.'}{'master_d'}{'    '}{'(master [0])'}\n")
                file.write(f"{');'}\n")
                file.write('\n\n')
                    
        # Instantiating slave blocks       
               # Instantiate the RAM Block
            elif ('ram' in name_of_ip):
                name = (name_of_ip.split('_')[0]).upper() 
                file.write(f"{'// Instantiating RAM IP'}\n")                       
                file.write(f"{name_of_ip[:-3]}{' # ('}\n")
                file.write(f"{'    .MEMORY_SIZE(`CEP_RAM_SIZE)'}\n")
                file.write(f"{') '}{name_of_ip[0:-3]}{'_inst'}{' ('}\n")
                for i in ipval_ip:
                    if ('clk' in i[1]):
                        ip_clk.append(i[1])
                    if ('rst' in i[1]):
                        ip_rst.append(i[1])
                file.write(f"{'.'}{ip_clk[0]}{'    '}{'(core_clk),'}\n")
                file.write(f"{'.'}{ip_rst[0]}{'    '}{'(~core_rst),'}\n")
                file.write(f"{'.'}{'slave'}{'    '}{'(slave[`'}{name}{'_SLAVE_NUMBER])'}\n")
                file.write(f"{');'}\n")
                file.write('\n\n')
                    
            # Instantiating the UART Block
            elif ('uart' in name_of_ip):
                name = (name_of_ip.split('_')[0]).upper() 
                file.write(f"{'// Instantiating UART IP'}\n")
                file.write(f"{'wire    uart_irq;'}\n")
                file.write(f"{name_of_ip[:-3]}{' '}{name_of_ip[:-3]}{'_inst'}{' ('}\n")
                for i in ipval_ip:
                    if ('clk' in i[1]):
                        ip_clk.append(i[1])
                    if ('rst' in i[1]):
                        ip_rst.append(i[1])
                file.write('\n')
                file.write(f"{'// UART Signals'}\n")
                file.write(f"{'.'}{ip_clk[0]}{'    '}{'(core_clk),'}\n")
                file.write(f"{'.'}{ip_rst[0]}{'    '}{'(~core_rst),'}\n")
                file.write(f"{'.'}{'slave'}{'    '}{'(slave[`'}{name}{'_SLAVE_NUMBER]),'}\n")
                
                file.write('\n')
                file.write(f"{'.srx_pad_i      (uart_srx_pad_i ),'}\n")
                file.write(f"{'.stx_pad_o      (uart_stx_pad_o ),'}\n")
                file.write(f"{'.rts_pad_o      (uart_rts_pad_o ),'}\n")
                file.write(f"{'.cts_pad_i      (uart_cts_pad_i ),'}\n")
                file.write(f"{'.dtr_pad_o      (               ),'}\n")
                str_1 = ".dsr_pad_i      (1'b0           ),"
                str_2 = ".ri_pad_i       (1'b0           ),"
                str_3 = ".dcd_pad_i      (1'b0           ),"                
                file.write(str(str_1))
                file.write('\n')
                file.write(str(str_2))
                file.write('\n')
                file.write(str(str_3))
                file.write('\n')
                file.write(f"{'// Processor Interrupt'}\n")
                file.write(f"{'.int_o          (uart_irq       )'}\n")
                file.write(f"{');'}\n")
                file.write('\n\n')
    
    # Instantiating all the other IP blocks
                
            else:
                name = (name_of_ip.split('_')[0]).upper() 
                file.write(f"{'// Instantiating '}{name}{' IP'}\n")
                file.write(f"{'generate'}\n")
                file.write(f"{'if(cep_routing_rules[`'}{name}{'_SLAVE_NUMBER][0] == `CEP_SLAVE_ENABLED)'}\n")
                file.write(f"{name_of_ip[:-3]}{' '}{name_of_ip[:-3]}{'_inst'}{' ('}\n")
                for i in ipval_ip:
                    if ('clk' in i[1]):
                        ip_clk.append(i[1])
                    if ('rst' in i[1]):
                        ip_rst.append(i[1])

                file.write(f"{'.'}{ip_clk[0]}{'    '}{'(core_clk),'}\n")
                file.write(f"{'.'}{ip_rst[0]}{'    '}{'(~core_rst),'}\n")
                file.write(f"{'.'}{'slave'}{'    '}{'(slave[`'}{name}{'_SLAVE_NUMBER])'}\n")
                file.write('\n')
                file.write(f"{');'}\n")
                file.write('endgenerate')
                file.write('\n\n')
        file.write('endmodule')
        print('AXI4-Lite successfully compiled')
        print('***************************************************')
        return(AXI_dict)
            

# if __name__ == '__main__':
#     SoC_generic.soc_generator_wb('D:\Code\SoC Compiler Tool', 'hybrid_wb.json')
#     soc_generator_AXI('D:\Code\SoC Compiler Tool', 'hybrid_wb.json')
    