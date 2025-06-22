import os
import extract_IO
import interfaceIP_NA
import json
import SoC_generic_AXI


def soc_generator_wb(base_dir, in_json_file):
    wb_soc_connections = None
    soc_connections_hybrid = None
    wb_dict = None
    copy = None
    wb_top_module = []
    wb_neighbors = []
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
    temp = None
    count = 0
    stub_list = []
    with open(os.path.join(base_dir, in_json_file)) as file:
        try:
            soc_connections_hybrid = json.load(file)
        except ValueError as e:
            print(e)
    
    for val in soc_connections_hybrid:
        print(val)
        for i in soc_connections_hybrid[val]:
            # print(i, sep = '\n')
            if (i == 'bus_type'):
                if (soc_connections_hybrid[val][i] == 'Wishbone'):
                    wb_top_module.append(soc_connections_hybrid[val]['IP_name'])
                    wb_is_router.append(soc_connections_hybrid[val]['is_Router'])
                    wb_config.append(soc_connections_hybrid[val]['config'])
                    wb_neighbors.append(soc_connections_hybrid[val]['neighbors'])

                if(soc_connections_hybrid[val][i] == 'AXI'):
                    axi_ip_name.append(soc_connections_hybrid[val]['IP_name'])
           
        # if (val == 'stub'):
        #         print(soc_connections_hybrid[val])
                # stub_list.append(soc_connections_hybrid[val])
        # print(stub_list)
    #print(wb_top_module)
    for entry in wb_config:
        if (entry == 'SLAVE'):
            wb_is_slave.append(True)
            wb_is_master.append(False)
        else:
            wb_is_master.append(True)
            wb_is_slave.append(False)
    # print(wb_is_slave)
    index = 0
    for k in wb_top_module:
        index+=1
        if (k == 'wb_bus_b3.v'):
            wb_is_master[index-1] = False
            wb_is_slave[index-1] = False
    string_wb = ''
    string_axi = ''
    counter_wb = 0
    counter_axi = 0
    count_wb = 0
    count_axi = 0
################################################
    for value in wb_top_module:
         if ('wb_bus_b3' in value):
             string = 'R_1'
             endpoint.append(string)
         else:
             string = 'EP_'+ str(counter_wb)
             counter_wb+=1
             endpoint.append(string)
    
    for i in endpoint:
        dict_list.append({"neighbors":wb_neighbors[count_wb],
            "is_Router":wb_is_router[count_wb],"top_module_fname":wb_top_module[count_wb],
                      "is_Master":wb_is_master[count_wb],
                      
                      "is_Slave":wb_is_slave[count_wb]
                  })
        count_wb+=1
    wb_dict = dict(zip(endpoint,dict_list))
    wb_soc_connections = wb_dict.copy()
    
    #counting the number of masters & slaves in the json file
    Master_count=0
    Slave_Bus_count=0
    for i in wb_soc_connections:
        for j in wb_soc_connections[i]:
            if(j=='is_Master'):
                if (wb_soc_connections[i][j]==True):
                    Master_count=Master_count+1
                else:
                    Slave_Bus_count=Slave_Bus_count+1
    if(Slave_Bus_count==0):
        Slave_count=0
    else:
        Slave_count = Slave_Bus_count-1
    
    ##########################
    slave_names=[]
    master_names=[]
    for i in wb_soc_connections:
            for j in wb_soc_connections[i]:
                if(j=='is_Slave'):
                    if (wb_soc_connections[i][j]==True):
                        slave_names.append(wb_soc_connections[i]['top_module_fname'])
    # print(slave_names)              
    for i in wb_soc_connections:
            for j in wb_soc_connections[i]:
                if(j=='is_Master'):
                    if (wb_soc_connections[i][j]==True):
                        master_names.append(wb_soc_connections[i]['top_module_fname'])

    slave_list=[]
    master_list=[]
    slave_list=[w[:-2] for w in slave_names]
    master_list=[w[:-2] for w in master_names]
   
    router_details = {}
    ip = None
    for key, value in wb_soc_connections.items():
        if value['is_Router']:
            router_details[key] = {}
            router_details[key]['r_wire'] = {}
            router_details[key]['r_neighbors'] = []
            count_ports = 0
            count_ep_neighbors = 0
            for neighbors in value['neighbors']:
              
                if wb_soc_connections[neighbors]['is_Router']:
                    router_details[key]['r_neighbors'].append(neighbors)
                    count_ports += 1
                    a = int(key.split('_')[1])
                    b = int(neighbors.split('_')[1])
                    if a > b:
                        router_details[key]['r_wire'][neighbors] = f"{neighbors.split('_')[0]}_{b}_{a}"
                    else:
                        router_details[key]['r_wire'][neighbors] = f"{neighbors.split('_')[0]}_{a}_{b}"
                else:
                    count_ports += 2
                    count_ep_neighbors += 1
                    router_details[key]['ep_wire'] = f"{key}_EP"
            router_details[key]['top_module_fname'] = value['top_module_fname']
            router_details[key]['no_of_ports'] = count_ports
            router_details[key]['no_of_EPs'] = count_ep_neighbors
        else:
            ip = value['top_module_fname']

    # create router object to parse info of the router
    router_fname = "wb_bus_b3.v"
    router = extract_IO.ExtractRtl(base_dir, router_fname)
    router.extract_headers()
    router.extract_io()
    router.extract_param()
    router.extract_module()

    index_clk_rst = []
    router_clk_rst = []
    orig_router_inputs_temp = list(router.inputs)
    
    for i in range(len(orig_router_inputs_temp)):
        temp = orig_router_inputs_temp[i]
        if (temp[temp[-1]] == 'clk_i' or temp[temp[-1]] == 'rst_i'):
            index_clk_rst.append(i)
    count = 0
    for i in index_clk_rst:
        router_clk_rst.append(orig_router_inputs_temp[i - count][orig_router_inputs_temp[i - count][-1]])
        orig_router_inputs_temp.remove(orig_router_inputs_temp[i - count])
        count += 1
   
    router_inputs_dict = {}
    for inputs in orig_router_inputs_temp:
        router_inputs_dict[inputs[inputs[-1]]] = inputs
   
    router_outputs_dict = {}
    for outputs in router.outputs:
        router_outputs_dict[outputs[outputs[-1]]] = outputs
  
    # create compute_tile object to parse info of the compute_tile
    ip = interfaceIP_NA.interface_ip_na(base_dir, ip)
    compute_tile = extract_IO.ExtractRtl(base_dir, ip)
    compute_tile.extract_param()
    compute_tile.extract_headers()
    compute_tile.extract_io()
    compute_tile.extract_module()

    total_packages = list(set(compute_tile.packages).union(set(router.packages)))
    total_includes = list(set(compute_tile.includes).union(set(router.includes)))
  

    in_from_noc = [] # input to IP/ output from bus
    in_from_noc_dict = {}
    out_to_noc = [] # output from ip to bus
    out_to_noc_dict = {}
    resets = []
    clk = []
    #all above are completed wrt wishbone bus
    router_inputs = []
    router_outputs = []
   
    #router_input_dict & router_output_dict are coming from the noc_router_sv file
    #################################################################################
    #populating dictionaries for bus inputs and bus outputs
    for inputs in compute_tile.inputs:
        if 'wb' in inputs[inputs[-1]]:
            in_from_noc.append(inputs[inputs[-1]])
            in_from_noc_dict[inputs[inputs[-1]]] = inputs
            
            router_inputs = list(router_inputs_dict.keys())
            
        elif ('rst' in inputs[inputs[-1]]) and ('dbg' not in inputs[inputs[-1]]):
            resets.append(inputs[inputs[-1]])
        elif 'clk' in inputs[inputs[-1]]:
            clk.append(inputs[inputs[-1]])

    for outputs in compute_tile.outputs:
        if 'wb' in outputs[outputs[-1]]:
            out_to_noc.append(outputs[outputs[-1]])
            out_to_noc_dict[outputs[outputs[-1]]] = outputs
            router_outputs = list(router_outputs_dict.keys())
    
    #######################################
    router_outputs_in_order = []
    router_outputs_set = set(router_outputs)
    
    for inputs in router_inputs:
        temp = inputs.split('_')
        if temp[0] == 'in':
            temp[0] = 'out'
        else:
            temp[0] = 'in'
        temp = '_'.join(temp)
        if temp in router_outputs_set:
            router_outputs_in_order.append(temp)
  
##############################################################################
    #creating a list of wired for different signals for master and slave
    
    m_input_wires =  ['busms_ack_i_flat','busms_rty_i_flat','busms_err_i_flat','busms_dat_i_flat']


    
    m_output_wires = ['busms_adr_o_flat','busms_cyc_o_flat','busms_dat_o_flat','busms_sel_o_flat','busms_stb_o_flat',
                           'busms_we_o_flat','busms_cab_o_flat','busms_cti_o_flat','busms_bte_o_flat']
    
    s_input_wires =   ['bussl_adr_i','bussl_cyc_i','bussl_dat_i','bussl_sel_i','bussl_stb_i',
                           'bussl_we_i','bussl_cab_i','bussl_cti_i','bussl_bte_i']
    
    s_output_wires =  ['bussl_ack_o','bussl_rty_o', 'bussl_err_o','bussl_dat_o']
    
    master_input_wires = sorted(m_input_wires)
    master_output_wires = sorted(m_output_wires)
    slave_input_wires = sorted(s_input_wires)
    slave_output_wires = sorted(s_output_wires)
   
    
    ##########################################################################
    router_wires = {}
    router_wires_in_order = {}
    for module, connections in wb_soc_connections.items():
        if connections['is_Router']:
            router_wires[module] = {}
            router_wires_in_order[module] = {}
            r_ep = f'{module}_EP'
            temp_in = []
            temp_out = []
            temp_out_in_order = []
            for outputs in out_to_noc:
                temp_out.append(f"{outputs}_{router_details[module]['ep_wire']}")
            temp_out_set = set(temp_out)
            for inputs in in_from_noc:
                temp_in.append(f"{inputs}_{router_details[module]['ep_wire']}")
                temp = inputs.split('_')
                if temp[1] == 'in':
                    temp[1] = 'out'
                else:
                    temp[1] = 'in'
                temp = f"{'_'.join(temp)}_{router_details[module]['ep_wire']}"
                if temp in temp_out_set:
                    temp_out_in_order.append(temp)

            router_wires[module][r_ep] = [temp_in, temp_out]
            router_wires_in_order[module][r_ep] = [temp_in, temp_out_in_order]
     ###########################################################################

    param_channels = 2
    
    param_flit_width = 32

    if (len(axi_ip_name) != 0):
        generated_soc_filename = 'axi4lite_2_wb.sv'
        generated_soc_top_module_name = 'axi4lite_2_wb'
    else:
        generated_soc_filename = 'demo_wb.sv'
        generated_soc_top_module_name = 'demo_wb'

    with open(os.path.join(base_dir, generated_soc_filename), 'w') as file:
        file.write(f'module {generated_soc_top_module_name}\n')
        file.write('\n')
        file.write('(\n')
        
        file.write('input logic clk_i,\n')
        
        if ((len(axi_ip_name) != 0) and (len(wb_top_module)!=0)):
            file.write('input logic rst_ni,\n')
        else:
            file.write('input logic rst_ni\n')
        
        if (len(axi_ip_name) != 0):
            file.write('AXI_LITE.Slave    slave\n')
        
        file.write(');\n')
        file.write('\n\n')
        file.write(f"localparam NR_MASTERS = {Master_count};\n")
        file.write(f"localparam NR_SLAVES = {Slave_count};\n")       
        slave_number=0
        stub_count=0
        for i in wb_soc_connections:
            for j in wb_soc_connections[i]:
                if(j=='is_Slave'):
                    if (wb_soc_connections[i][j]==True):
                        slave_name=wb_soc_connections[i]['top_module_fname']
                        slave_write='SLAVE_' + slave_name[:-6].upper()
                        file.write(f"localparam {slave_write} = {slave_number};\n")
                        slave_number+=1    
        print(slave_number)
        file.write('\n\n')
        file.write(f'wire                                wb_clk;\n')
        file.write(f'wire                                wb_rst;\n')
        
        file.write('\n\n')
        file.write(f'wire [31:0]   busms_adr_o[0:NR_MASTERS-1];\n')
        file.write(f'wire          busms_cyc_o[0:NR_MASTERS-1];\n')
        file.write(f'wire [31:0]   busms_dat_o[0:NR_MASTERS-1];\n')
        file.write(f'wire [3:0]    busms_sel_o[0:NR_MASTERS-1];\n')
        file.write(f'wire          busms_stb_o[0:NR_MASTERS-1];\n')
        file.write(f'wire          busms_we_o[0:NR_MASTERS-1];\n')
        file.write(f'wire          busms_cab_o[0:NR_MASTERS-1];\n')
        file.write(f'wire [2:0]    busms_cti_o[0:NR_MASTERS-1];\n')
        file.write(f'wire [1:0]    busms_bte_o[0:NR_MASTERS-1];\n')
        file.write(f'wire          busms_ack_i[0:NR_MASTERS-1];\n')
        file.write(f'wire          busms_rty_i[0:NR_MASTERS-1];\n')
        file.write(f'wire          busms_err_i[0:NR_MASTERS-1];\n')
        file.write(f'wire [31:0]   busms_dat_i[0:NR_MASTERS-1];\n')

        file.write(f'wire [31:0]   bussl_adr_i[0:NR_SLAVES-1];\n')
        file.write(f'wire          bussl_cyc_i[0:NR_SLAVES-1];\n')
        file.write(f'wire [31:0]   bussl_dat_i[0:NR_SLAVES-1];\n')
        file.write(f'wire [3:0]    bussl_sel_i[0:NR_SLAVES-1];\n')
        file.write(f'wire          bussl_stb_i[0:NR_SLAVES-1];\n')
        file.write(f'wire          bussl_we_i[0:NR_SLAVES-1];\n')
        file.write(f'wire          bussl_cab_i[0:NR_SLAVES-1];\n')
        file.write(f'wire [2:0]    bussl_cti_i[0:NR_SLAVES-1];\n')
        file.write(f'wire [1:0]    bussl_bte_i[0:NR_SLAVES-1];\n')
        file.write(f'wire          bussl_ack_o[0:NR_SLAVES-1];\n')
        file.write(f'wire          bussl_rty_o[0:NR_SLAVES-1];\n')
        file.write(f'wire          bussl_err_o[0:NR_SLAVES-1];\n')
        file.write(f'wire [31:0]   bussl_dat_o[0:NR_SLAVES-1];\n')
        
        file.write('\n\n')

        file.write(f'wire          snoop_enable;\n')
        file.write(f'wire [31:0]   snoop_adr;\n')
        file.write(f'wire [31:0]   pic_ints_i [0:1];\n')
        file.write(f"assign pic_ints_i[0][31:4] = 28'h0;\n")
        file.write(f"assign pic_ints_i[0][1:0] = 2'b00;\n")
        file.write('\n')
        file.write(f'genvar        c, m, s;\n')

        file.write(f'wire [32*NR_MASTERS-1:0] busms_adr_o_flat;\n')
        file.write(f'wire [NR_MASTERS-1:0]    busms_cyc_o_flat;\n')
        file.write(f'wire [32*NR_MASTERS-1:0] busms_dat_o_flat;\n')
        file.write(f'wire [4*NR_MASTERS-1:0]  busms_sel_o_flat;\n')
        file.write(f'wire [NR_MASTERS-1:0]    busms_stb_o_flat;\n')
        file.write(f'wire [NR_MASTERS-1:0]    busms_we_o_flat;\n')
        file.write(f'wire [NR_MASTERS-1:0]    busms_cab_o_flat;\n')
        file.write(f'wire [3*NR_MASTERS-1:0]  busms_cti_o_flat;\n')
        file.write(f'wire [2*NR_MASTERS-1:0]  busms_bte_o_flat;\n')
        file.write(f'wire [NR_MASTERS-1:0]    busms_ack_i_flat;\n')
        file.write(f'wire [NR_MASTERS-1:0]    busms_rty_i_flat;\n')
        file.write(f'wire [NR_MASTERS-1:0]    busms_err_i_flat;\n')
        file.write(f'wire [32*NR_MASTERS-1:0] busms_dat_i_flat;\n')

        file.write(f'wire [32*NR_SLAVES-1:0] bussl_adr_i_flat;\n')
        file.write(f'wire [NR_SLAVES-1:0]    bussl_cyc_i_flat;\n')
        file.write(f'wire [32*NR_SLAVES-1:0] bussl_dat_i_flat;\n')
        file.write(f'wire [4*NR_SLAVES-1:0]  bussl_sel_i_flat;\n')
        file.write(f'wire [NR_SLAVES-1:0]    bussl_stb_i_flat;\n')
        file.write(f'wire [NR_SLAVES-1:0]    bussl_we_i_flat;\n')
        file.write(f'wire [NR_SLAVES-1:0]    bussl_cab_i_flat;\n')
        file.write(f'wire [3*NR_SLAVES-1:0]  bussl_cti_i_flat;\n')
        file.write(f'wire [2*NR_SLAVES-1:0]  bussl_bte_i_flat;\n')
        file.write(f'wire [NR_SLAVES-1:0]    bussl_ack_o_flat;\n')
        file.write(f'wire [NR_SLAVES-1:0]    bussl_rty_o_flat;\n')
        file.write(f'wire [NR_SLAVES-1:0]    bussl_err_o_flat;\n')
        file.write(f'wire [32*NR_SLAVES-1:0] bussl_dat_o_flat;\n')
        file.write('\n\n')
        
        if (len(axi_ip_name) != 0):
    
            fast_read = "    .FAST_READ_TERM (1'd0)"
            
            file.write(f'bonfire_axi4l2wb #(\n')
            file.write(f'    .ADRWIDTH       (slave.AXI_ADDR_WIDTH),\n')
            file.write(str(fast_read))
            file.write('\n')
            
            file.write(f') bonfire_axi4l2wb_inst (\n')

            file.write(f'   .S_AXI_ACLK     (clk_i),\n')
            file.write(f'   .S_AXI_ARESETN  (rst_ni),\n')
            file.write(f'   .S_AXI_AWADDR   (slave.aw_addr),\n')
            file.write(f'   .S_AXI_AWVALID  (slave.aw_valid),\n')
            file.write(f'   .S_AXI_AWREADY  (slave.aw_ready),\n')
            file.write(f'   .S_AXI_WDATA    (slave.w_data),\n')
            file.write(f'   .S_AXI_WSTRB    (slave.w_strb),\n')
            file.write(f'   .S_AXI_WVALID   (slave.w_valid),\n')
            file.write(f'   .S_AXI_WREADY   (slave.w_ready),\n')
            file.write(f'   .S_AXI_ARADDR   (slave.ar_addr),\n')
            file.write(f'   .S_AXI_ARVALID  (slave.ar_valid),\n')
            file.write(f'   .S_AXI_ARREADY  (slave.ar_ready),\n')
            file.write(f'   .S_AXI_RDATA    (slave.r_data),\n')
            file.write(f'   .S_AXI_RRESP    (slave.r_resp),\n')
            file.write(f'   .S_AXI_RVALID   (slave.r_valid),\n')
            file.write(f'   .S_AXI_RREADY   (slave.r_ready),\n')
            file.write(f'   .S_AXI_BRESP    (slave.b_resp),\n')
            file.write(f'   .S_AXI_BVALID   (slave.b_valid),\n')
            file.write(f'   .S_AXI_BREADY   (slave.b_ready),\n')
            file.write(f'   .wb_clk_o       (clk_i),\n')
            file.write(f'   .wb_rst_o       (wb_rst),\n')
            file.write(f'   .wb_addr_o      (busms_adr_i_flat),\n')
            file.write(f'   .wb_dat_o       (busms_dat_o_flat),\n')
            file.write(f'   .wb_we_o        (busms_we_i_flat),\n')
            file.write(f'   .wb_sel_o       (busms_sel_i_flat),\n')
            file.write(f'   .wb_stb_o       (busms_stb_i_flat),\n')
            file.write(f'   .wb_cyc_o       (busms_cyc_i_flat),\n')
            file.write(f'   .wb_dat_i       (busms_dat_i_flat),\n')
            file.write(f'   .wb_ack_i       ()\n')
            file.write(f');\n')
            
        file.write('\n\n')

        file.write(f'generate\n')
        file.write(f'for (m = 0; m < NR_MASTERS; m = m + 1) begin : gen_busms_flat\n')
        file.write(f'assign busms_adr_o_flat[32*(m+1)-1:32*m] = busms_adr_o[m];\n')
        file.write(f'assign busms_cyc_o_flat[m] = busms_cyc_o[m];\n')
        file.write(f'assign busms_dat_o_flat[32*(m+1)-1:32*m] = busms_dat_o[m];\n')
        file.write(f'assign busms_sel_o_flat[4*(m+1)-1:4*m] = busms_sel_o[m];\n')
        file.write(f'assign busms_stb_o_flat[m] = busms_stb_o[m];\n')
        file.write(f'assign busms_we_o_flat[m] = busms_we_o[m];\n')
        file.write(f'assign busms_cab_o_flat[m] = busms_cab_o[m];\n')
        file.write(f'assign busms_cti_o_flat[3*(m+1)-1:3*m] = busms_cti_o[m];\n')
        file.write(f'assign busms_bte_o_flat[2*(m+1)-1:2*m] = busms_bte_o[m];\n')
        file.write(f'assign busms_ack_i[m] = busms_ack_i_flat[m];\n')
        file.write(f'assign busms_rty_i[m] = busms_rty_i_flat[m];\n')
        file.write(f'assign busms_err_i[m] = busms_err_i_flat[m];\n')
        file.write(f'assign busms_dat_i[m] = busms_dat_i_flat[32*(m+1)-1:32*m];\n')
        file.write(f'end\n')

        file.write(f'for (s = 0; s < NR_SLAVES; s = s + 1) begin : gen_bussl_flat\n')
        file.write(f'assign bussl_adr_i[s] = bussl_adr_i_flat[32*(s+1)-1:32*s];\n')
        file.write(f'assign bussl_cyc_i[s] = bussl_cyc_i_flat[s];\n')
        file.write(f'assign bussl_dat_i[s] = bussl_dat_i_flat[32*(s+1)-1:32*s];\n')
        file.write(f'assign bussl_sel_i[s] = bussl_sel_i_flat[4*(s+1)-1:4*s];\n')
        file.write(f'assign bussl_stb_i[s] = bussl_stb_i_flat[s];\n')
        file.write(f'assign bussl_we_i[s] = bussl_we_i_flat[s];\n')
        file.write(f'assign bussl_cab_i[s] = bussl_cab_i_flat[s];\n')
        file.write(f'assign bussl_cti_i[s] = bussl_cti_i_flat[3*(s+1)-1:3*s];\n')
        file.write(f'assign bussl_bte_i[s] = bussl_bte_i_flat[2*(s+1)-1:2*s];\n')
        file.write(f'assign bussl_ack_o_flat[s] = bussl_ack_o[s];\n')
        file.write(f'assign bussl_rty_o_flat[s] = bussl_rty_o[s];\n')
        file.write(f'assign bussl_err_o_flat[s] = bussl_err_o[s];\n')
        file.write(f'assign bussl_dat_o_flat[32*(s+1)-1:32*s] = bussl_dat_o[s];\n')
        file.write(f'end\n')
        file.write(f'endgenerate\n')
        file.write('\n\n')

        # start instantiating the endpoints and routers
        ##############################################        
        for module, connections in wb_soc_connections.items():
            if connections['is_Router']:
             
                # instantiating the endpoints except the wishbone bus
                ########################################
                string=[]
                for endpoint in wb_soc_connections:
                    for val in wb_soc_connections[endpoint]:
                        if(val=='top_module_fname'):
                            if not (wb_soc_connections[endpoint][val]=='wb_bus_b3.v'):
                                string.append(wb_soc_connections[endpoint][val])
                print(string)            
                for ip_name in string:
                        slave_intermediate_input=[]
                        slave_intermediate_output=[]
                        master_intermediate_input=[]
                        master_intermediate_output=[]
                        slave_final_input=[]
                        slave_final_output=[]
                        master_final_input=[]
                        master_final_output=[] 
                        list_1_cut_i = []
                        list_2_slice_i = []
                        list_1_cut_o = []
                        list_2_slice_o = []
                        name=ip_name
                        module_io = extract_IO.ExtractRtl(base_dir, name)
                        module_io.extract_io()
                        input_res = [lis[-2] for lis in module_io.inputs]
                        
                        if (name == "picorv32_top.v"):
                            for i in input_res:                        
                                if(i[0:3]=='wbm'):
                                    master_intermediate_input.append(i)
                        else:
                            for i in input_res:                        
                                if(i[0:2]=='wb'):
                                    slave_intermediate_input.append(i)
                        master_final_input = sorted(master_intermediate_input)
                        slave_final_input = sorted(slave_intermediate_input)
                        output_res = [lis[-2] for lis in module_io.outputs]
                        
                        if(name == "picorv32_top.v"): 
                            
                            for i in output_res:
                                if(i[0:3]=='wbm'):
                                    master_intermediate_output.append(i)
                        else:
                            for i in output_res:
                                if(i[0:2]=='wb'):
                                    slave_intermediate_output.append(i)
                        
                        master_final_output = sorted(master_intermediate_output)
                        slave_final_output = sorted(slave_intermediate_output)
                        # print('slave values')
                        # print(slave_final_output)
                        ip_input = []
                        master_input = []
                        IP_input = []
                        MASTER_input = []
                        ip_output = []
                        master_output = []
                        IP_output = []
                        MASTER_output = []
                        index_val=0
                        
                        #instantiating slave IP 
                        ### Slave inputs
       
                        if (name != 'picorv32_top.v'):
                            for x in slave_final_input:
                                l1 = x[3:6]
                                list_1_cut_i.append(l1)
                            for y in s_input_wires:
                                l1 = y[6:9]
                                list_2_slice_i.append(l1)
                            k=0
                            file.write(f"{name[:-2]} {name[:-2]}{'_inst'}\n" )
                            file.write(f"{'('}\n")
                            file.write(f"{'.wb_clk_i(clk_i),'}\n")
                            file.write(f"{'.wb_rst_i(rst_ni),'}\n")
                            for i,j in enumerate(list_1_cut_i):
                                try:
                                    if j==list_2_slice_i[k]:
                                        file.write(f".{slave_final_input[i]}({s_input_wires[k]}[SLAVE_{name[0:-6].upper()}]),\n")
                                        k+=1
                                except Exception:
                                    pass  
                            
                        ### Slave outputs

                            for x in slave_final_output:
                                l1 = x[3:6]
                                list_1_cut_o.append(l1)
                            for y in slave_output_wires:
                                l1 = y[6:9]
                                list_2_slice_o.append(l1)
                            k=0
                            size_o = len(list_1_cut_o)
                            string_ip=""
                            for i,j in enumerate(list_1_cut_o):
                                try:
                                    if j==list_2_slice_o[k]:
                                        string_ip = "."+slave_final_output[i]+"("+slave_output_wires[k]+"[SLAVE_"+name[0:-6].upper()+"])"+","
                                        # print(string_ip)
                                        f = ""
                                        if i==(size_o-1): 
                                            f = string_ip.rstrip(',')
                                            file.write(str(f))
                                            file.write("\n")
                                        else:
                                            file.write(str(string_ip))
                                            file.write("\n")
                                        k+=1
                                except Exception:
                                    pass
                            file.write(f")") 
                            file.write(f";\n")
                            file.write("\n")
                            file.write("\n")

            ###################################################################################################
                    # instantiating master IP
                        else: 
                            old_ip_i = []
                            old_ip_o = []
                            old_bus_i = []
                            old_bus_o = []
                            ip_i = []
                            ip_o = []
                            bus_i = []
                            bus_o = []
                            # print(master_final_input)

                            for i in master_final_input:
                                ip_i_split = i.split('_')
                                old_ip_i.append(ip_i_split[1])
                            for j in  master_final_output:
                                ip_o_split = j.split('_')
                                old_ip_o.append(ip_o_split[1])
                            for x in m_input_wires:
                                bus_i_split = x.split('_')
                                old_bus_i.append(bus_i_split[1])
                            for y in m_output_wires:
                                bus_o_split = y.split('_')
                                old_bus_o.append(bus_o_split[1])
                            ip_i=sorted(old_ip_i)
                            ip_o=sorted(old_ip_o)
                            bus_i=sorted(old_bus_i)
                            bus_o=sorted(old_bus_o)
                            index_val=0
                            
                            file.write(f"{name[:-2]} {name[:-2]}{'_inst'}\n" )
                            file.write(f"{'('}\n")
                            file.write(f"{'.wb_clk_i(clk_i),'}\n")
                            file.write(f"{'.wb_rst_i(rst_ni),'}\n")
                            
                            #intitializing for input signals
                            for i,j in enumerate(ip_i):
                                try:
                                    if j in bus_i:
                                        index_val = bus_i.index(j)
                                        file.write(f".{master_final_input[i]}({master_input_wires[index_val]}),\n")
                                    else:
                                        pass
                                except Exception:
                                    pass  
                            #intilialising the output signals
                            size_op = len(ip_o)
                            for i,j in enumerate(ip_o):
                                try:
                                    if j in bus_o:
                                        index_val = bus_o.index(j)
                                        string_op = "."+master_final_output[i]+"("+master_output_wires[index_val]+")"+","
                                        fo = ""
                                        if i==(size_op-1): 
                                            fo = string_op.rstrip(',')
                                            file.write(str(fo))
                                            file.write("\n")
                                        else:
                                            file.write(str(string_op))
                                            file.write("\n")
                                    else:
                                        pass
                                except Exception:
                                    pass   
                            file.write(f")") 
                            file.write(f";\n")
                        
                ########################################                
                # Instantiate the Network Adapter if there is a 
                # NoC Router in the json file
                for value in soc_connections_hybrid:
                    for IP in soc_connections_hybrid[value]:
                        if (soc_connections_hybrid[value][IP]=='noc_router.sv'):
                
                            file.write(f"{'networkadapter_ct networkadapter_ct_inst'}\n")
                            file.write(f"{'('}\n")

                            file.write(f"{'.wb_clk_i(clk_i),'}\n")
                            file.write(f"{'.wb_rst_i(rst_ni),'}\n")
                            # Master Signals
                            file.write(f"{'.m_adr_i(wbm_adr_o),'}\n")
                            file.write(f"{'.m_bte_i(wbm_bte_o),'}\n")
                            file.write(f"{'.m_cti_i(wbm_cti_o),'}\n")
                            file.write(f"{'.m_cyc_i(wbm_cyc_o),'}\n")
                            file.write(f"{'.m_dat_i(wbm_dat_o),'}\n")
                            file.write(f"{'.m_sel_i(wbm_sel_o),'}\n")
                            file.write(f"{'.m_stb_i(wbm_stb_o),'}\n")
                            file.write(f"{'.m_we_i(wbm_we_o),'}\n")
                            file.write(f"{'.m_ack_o(wbm_ack_i),'}\n")
                            file.write(f"{'.m_dat_o(wbm_dat_i),'}\n")
                            file.write(f"{'.m_err_o(wbm_err_i),'}\n")
                            file.write(f"{'.m_rty_o(wbm_rty_i),'}\n")
                            file.write("\n")
                            #Slave Signals
                            file.write(f"{'.s_adr_o(wbs_adr_i),'}\n")
                            file.write(f"{'.s_bte_o(wbs_bte_i),'}\n")
                            file.write(f"{'.s_cti_o(wbs_cti_i),'}\n")
                            file.write(f"{'.s_cyc_o(wbs_cyc_i),'}\n")
                            file.write(f"{'.s_dat_o(wbs_dat_i),'}\n")
                            file.write(f"{'.s_sel_o(wbs_sel_i),'}\n")
                            file.write(f"{'.s_stb_o(wbs_stb_i),'}\n")
                            file.write(f"{'.s_we_o(wbs_we_i),'}\n")
                            file.write(f"{'.s_ack_i(wbs_ack_o),'}\n")
                            file.write(f"{'.s_dat_i(wbs_dat_o),'}\n")
                            file.write(f"{'.s_err_i(wbs_err_o),'}\n")
                            file.write(f"{'.s_rty_i(wbs_rty_o)'}\n")
                            file.write(f"{');'}\n")
                            file.write("\n")
                            
                #########################################################################################
                file.write('\n\n')
                # ######################################################################
                # ## ** HERE THE IPs ARE INITIALIZED FINALLY
                # ## ** DO NOT DELETE THIS PART AT ANY COST
                
                for neighbors in connections['neighbors']:
                    if not wb_soc_connections[neighbors]['is_Router']:
                        ip_na_connection = interfaceIP_NA.interface_ip_na\
                            (base_dir, wb_soc_connections[neighbors]['top_module_fname'])
                        #print('IP na connection: ',ip_na_connection)
                        ip_na_obj = extract_IO.ExtractRtl(base_dir, ip_na_connection)
                        ip_na_obj.extract_module()
                        ip_na_top_module = ip_na_obj.module_names[0]
                ##############################################################################     
                file.write('\n')                          
                file.write('\n')

                #Instantiate all stub modules
                # for item in stub_list:
                #     with open(extract_IO.os.path.join(base_dir, "stub_instantiation.v")) as file2:
                #         file.write(f'stub \n')
                #         file.write(file2.read())
                #         file.write('\n\n')


                with open(extract_IO.os.path.join(base_dir, "wishbone.v")) as file2:
                   file.write(file2.read())
                   file.write('\n\n')
        file.write('endmodule\n')
        print('Wishbone successfully compiled')
        print('***************************************************')


if __name__ == '__main__':
    soc_generator_wb('/Users/kshitijraj/Study /SoC Compiler Tool', 'stub.json')