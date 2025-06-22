import os
import extract_IO
import interfaceIP_NA
import json

def soc_generator(base_dir, in_json_file):
    soc_connections = None
    with open(os.path.join(base_dir, in_json_file)) as file:
        try:
            soc_connections = json.load(file)
        except ValueError as e:
            print(e)
    
    config = (soc_connections.get('config')).lower()
    IP_type = (soc_connections.get('IP_type'))
    mem_size = (soc_connections.get('size'))
    
    # create ip object to parse info of the ip
    
    ip_fname = soc_connections.get('IP_name')
    ip = extract_IO.ExtractRtl(base_dir, ip_fname)
    ip.extract_headers()
    ip.extract_io()
    ip.extract_param()
    ip.extract_module()
    for i in ip.module_names:
        module_name = i
        top_module = i.split('_')[0]
    ip_param = [x[0] for x in ip.parameters]
    
    #declaring lists for ip inputs and outputs
    ip_input = list(ip.inputs)
    ip_output = list(ip.outputs)
    ip_parameters = list(ip.parameters)
    wishbone_input = []
    wishbone_output = []
    parsed_ip_input = []
    parsed_ip_output = []
    split_ip_input = []
    split_ip_output = []

     
    for i in ip_input:
        try:
            istring = i[1].split("_")[1]
            str_ival = i[1]
            split_ip_input.append(istring)
            wishbone_input.append(str_ival)
        except Exception:
            pass
    parsed_ip_input = sorted(split_ip_input)

    for i in ip_output:
        try:
            ostring = i[1].split("_")[1]
            str_oval = i[1]
            split_ip_output.append(ostring)
            wishbone_output.append(str_oval)
        except Exception:
            pass
    parsed_ip_output = sorted(split_ip_output)
    
    op_val = ['ack','dat']

    #keeping only required signals for AXI interface and deleting the rest
    while 'bte' in parsed_ip_input: parsed_ip_input.remove('bte')
    while 'cti' in parsed_ip_input: parsed_ip_input.remove('cti')
    
    #list containing Wishbone signals
    wb_input = []
    wb_output = []

    for i in parsed_ip_input:
        string = 'wb_' + i + '_o'
        wb_input.append(string)

    for i in op_val:
        string = 'wb_' + i + '_i'
        wb_output.append(string)
    
    generated_ip_filename = input('Enter the filename for the AXI IP\n')
    generated_ip_top_module_name = input('Enter the top module name for the AXI IP\n')
    with open(os.path.join(base_dir, generated_ip_filename), 'w') as file:
        file.write(f'module {generated_ip_top_module_name}{"# ("}\n')
        file.write(f"{'parameter MEMORY_SIZE = '}{mem_size}\n")
        file.write(')\n')
        file.write('(\n')
        file.write(f"{'// Clock and reset signals'}\n")
        file.write(f'input logic  clk_i,\n')
        file.write(f'input logic  rst_ni,\n')
        file.write('\n')
        file.write(f"{'// AXI4-Lite Slave Interface'}\n")
        file.write(f'axi_lite.' + config + '   ' + config)
        file.write('\n')
        file.write(f') ;\n')
        file.write('\n\n')

# Declaring wires for the AXI Bridge connections
    # declaring slave input wires
        input_axi = []
        output_axi = []
        file.write(f"{'// Wire declarations'}\n")
        for i in parsed_ip_input:
            if i == 'clk':
                file.write(f"{'wire                              wb_'}{i}{';'}\n")
                string = 'wb_'+i
                input_axi.append(string)
            elif i == 'rst':
                file.write(f"{'wire                              wb_'}{i}{';'}\n")
                string = 'wb_'+i
                input_axi.append(string)
            elif i == 'adr':
                file.write(f"{'wire [slave.AXI_ADDR_WIDTH - 1:0] wbs_'} {top_module}{'_'}{i}{'_i;'}\n")
                string = 'wbs_' + top_module + '_' + i + '_i'
                input_axi.append(string)
            elif i == 'dat':
                file.write(f"{'wire [slave.AXI_DATA_WIDTH - 1:0] wbs_'} {top_module}{'_'}{i}{'_i;'}\n")
                string = 'wbs_' + top_module + '_' + i + '_i'
                input_axi.append(string)
            elif i == 'sel':
                file.write(f"{'wire [3:0]                        wbs_'}{top_module}{'_'}{i}{'_i;'}\n")
                string = 'wbs_' + top_module + '_' + i + '_i'
                input_axi.append(string)
            else:
                file.write(f"{'wire                              wbs_'}{top_module}{'_'}{i}{'_i;'}\n")
                string = 'wbs_' + top_module + '_' + i + '_i'
                input_axi.append(string)
        

        #declaring slave output wires
        for i in op_val:
            if i == 'dat':
                file.write(f"{'wire [slave.AXI_DATA_WIDTH - 1:0] wbs_'}{top_module}{'_'}{i}{'_o;'}\n")
                string = 'wbs_' + top_module + '_' + i + '_o'
                output_axi.append(string)       
            elif i =='ack':
                file.write(f"{'wire                              wbs_'}{top_module}{'_'}{i}{'_o;'}\n")
                string = 'wbs_' + top_module + '_' + i + '_o'
                output_axi.append(string)
        file.write('\n\n')

    # Dealing with final instantiation of the wishbone IP
        wb_ip_input = list(ip.inputs)
        wb_ip_output = list(ip.outputs)
        wb_ip_input_list = []
        wb_ip_output_list = []
        for z in wb_ip_input:
            str_input_val = z[1]
            wb_ip_input_list.append(str_input_val)
        for y in wb_ip_output:
            str_output_val = y[1]
            wb_ip_output_list.append(str_output_val)
        
        wb_sorted_ip = sorted(wb_ip_input_list)
        wb_sorted_op = sorted(wb_ip_output_list)
        
        ip_list = []
        op_list = []
        for s in wb_sorted_ip:
            if s[0:2]=='wb':
                ip_list.append(s)
        for r in wb_sorted_op:
            if r[0:2]=='wb':
                op_list.append(r)
        
        file.write(f"{'// Instantiate the AXI4Lite to Wishbone bridge'}\n")
    # file write for bonfire instantiation  
        file.write(f'bonfire_axi4l2wb # (\n')
        file.write(f'       .ADRWIDTH     (slave.AXI_ADDR_WIDTH),\n')
        file.write(f"       .FAST_READ_TERM  (1'd0) \n")
        file.write(f') bonfire_axi4l2wb_inst  (\n')
        file.write(f'       .S_AXI_ACLK    (clk_i),\n')
        file.write(f'       .S_AXI_ARESETN    (rst_ni),\n')
        file.write(f'       .S_AXI_AWADDR    (slave.aw_addr),\n')
        file.write(f'       .S_AXI_AWVALID  (slave.aw_valid),\n')
        file.write(f'       .S_AXI_AWREADY  (slave.aw_ready),\n')
        file.write(f'       .S_AXI_WDATA    (slave.w_data),\n')
        file.write(f'       .S_AXI_WSTRB    (slave.w_strb),\n')
        file.write(f'       .S_AXI_WVALID   (slave.w_valid),\n')
        file.write(f'       .S_AXI_WREADY   (slave.w_ready),\n')
        file.write(f'       .S_AXI_ARADDR   (slave.ar_addr),\n')
        file.write(f'       .S_AXI_ARVALID  (slave.ar_valid),\n')
        file.write(f'       .S_AXI_ARREADY  (slave.ar_ready),\n')
        file.write(f'       .S_AXI_RDATA    (slave.r_data),\n')
        file.write(f'       .S_AXI_RRESP    (slave.r_resp),\n')
        file.write(f'       .S_AXI_RVALID   (slave.r_valid),\n')
        file.write(f'       .S_AXI_RREADY   (slave.r_ready),\n')
        file.write(f'       .S_AXI_BRESP    (slave.b_resp),\n')
        file.write(f'       .S_AXI_BVALID   (slave.b_valid),\n')
        file.write(f'       .S_AXI_BREADY   (slave.b_ready),\n')
        
        #intitializing for input signals
        for x,y in zip(wb_input,input_axi):
            file.write(f"{'.'}{x} {'('} {y} {'),'} \n")
        
        #initializing for output signals
        size = len(wb_output)
        conn = ''
        connection = ''
        connection_list = []
        for x,y in zip(wb_output,output_axi):
            connection = '.'+ x + '('+ y + ')' + ','
            connection_list.append(connection)
        j = 0 
        while (j != size-1):
            conn = connection_list[j]
            j+=1
            file.write(str(conn))
            file.write("\n")
        if (j == size-1):
            conn = connection_list[j].rstrip(',')
            file.write(str(conn))
            file.write("\n")
    
    # Instantiate the AXI IP
        # Only write this section to output file if the IP is a memory type IP   
        if(IP_type == 'memory'):        
            file.write(f') ;\n')
            file.write('\n\n')
            file.write(f"{'// Instantiate the SRAM block'}\n")  
            file.write(f'`ifndef SRAM_INITIALIZATION_FILE\n')
            file.write(f'   `define SRAM_INITIALIZATION_FILE     "sram.vmem"\n')
            file.write(f'`endif')  
            file.write('\n\n')
            
            parameters = []
            while ip_param:
                parameters.extend(ip_param.pop(0))
            file.write(f"{module_name}{' #('}\n")
            for x in parameters:
                if (x == 'memory_file'):
                    file.write(f"{'.'}{x}{'      (`SRAM_INITIALIZATION_FILE),'}\n")
                elif (x == 'aw'):
                    file.write(f"{'.'}{x}{'      (slave.AXI_ADDR_WIDTH),'}\n")
                elif (x == 'dw'):
                    file.write(f"{'.'}{x}{'      (slave.AXI_DATA_WIDTH),'}\n")
                elif (x == 'mem_size_bytes'):
                    file.write(f"{'.'}{x}{'      (MEMORY_SIZE)'}\n")
                elif (x == 'mem_adr_width'):
                    file.write(f"{'.'}{x}{'      ($clog2(MEMORY_SIZE))'}\n")
                else:
                    pass
        else:
            pass

    # IP Instantiation
        file.write("\n\n")    
        file.write(f"{') '}{module_name}{'_inst'}{' ('}\n")
        
        # Instantiating inputs of IP 
        file.write(f"{'// Instantiate the Input signals'}\n")
        axi_sig_in = ''
        axi_signal_in = []    
        for i in wishbone_input:
            if (i[3:6] == 'bte'):
                axi_sig_in = '.' + i + '       ' + "(2'b00),"
                axi_signal_in.append(axi_sig_in)
            elif (i[3:6] == 'cti'):
                axi_sig_in = '.' + i + '       ' + "(3'b000),"
                axi_signal_in.append(axi_sig_in)
            elif (i[3:6] == 'clk'):
                axi_sig_in = '.' + i + '       ' + '(wb_' + i[3:6] + '),' 
                axi_signal_in.append(axi_sig_in)
            elif (i[3:6] == 'rst'):
                axi_sig_in = '.' + i + '       ' + '(wb_' + i[3:6] + '),'
                axi_signal_in.append(axi_sig_in)
            else:
                axi_sig_in = '.' + i + '       ' + '(wbs_' + top_module + '_' + i[3:6] + '_i),'
                axi_signal_in.append(axi_sig_in)

        for i in axi_signal_in:
            file.write(f"{i}\n")
        
        
        # Instantiating outputs of IP
        length_op = len(wishbone_output)
        file.write(f"{'// Instantiate the Output signals'}\n")
        axi_sig_op = ''
        axi_signal_op = []    
        for i in wishbone_output:
            if (i[3:6] == 'err'):
                axi_sig_op = '.' + i + '       ' + '(),'
                axi_signal_op.append(axi_sig_op)
            else:
                axi_sig_op = '.' + i + '       ' + '(wbs_' + top_module + '_' + i[3:6] + '_o),'
                axi_signal_op.append(axi_sig_op)
        print(*axi_signal_op, sep = '\n')

        count = 0
        axi = ''
        while (count != length_op-1):
            axi = axi_signal_op[count]
            count+=1
            file.write(str(axi))
            file.write("\n")
        if (count == length_op-1):
            axi = axi_signal_op[count].rstrip(',')
            file.write(str(axi))
            file.write("\n")
        file.write(f"{');'}\n")
        file.write('\n')    
        file.write(f"{'endmodule'}")


if __name__ == '__main__':
    soc_generator('D:\Code\SoC Compiler Tool', 'axi_ip.json')