import os
import extract_IO
import interfaceIP_NA
import json



def soc_generator(base_dir, in_json_file):
    soc_connections = None
    with open(os.path.join(base_dir, in_json_file)) as file:
        try:
            soc_connections = json.load(file) # main dictionary that takes values from he json file
        except ValueError as e:
            print(e)

    

     #counting the number of masters & slaves in the json file
    Master_count=0
    Slave_Bus_count=0
    for i in soc_connections:
        for j in soc_connections[i]:
            if(j=='is_Master'):
                if (soc_connections[i][j]==True):
                    Master_count=Master_count+1
                else:
                    Slave_Bus_count=Slave_Bus_count+1
    if(Slave_Bus_count==0):
        Slave_count=0
    else:
        Slave_count = Slave_Bus_count-1
    
    print("Number of Masters : ", Master_count)
    print("Number of Slaves : ", Slave_count)

    router_details = {} #empty dictionary for routers
    ip = None 
    for key, value in soc_connections.items():
        if value['is_Router']: #check if IP is router or not
            router_details[key] = {}
            router_details[key]['r_wire'] = {} #another dictionary with key= 'wire'
     #when interfacing one router with another, connection is done through wires
     #the names of those wires are stored in dictionary 'r_wire' 
            #print(router_details.keys())
            router_details[key]['r_neighbors'] = [] #for each router, which neigbours are routers as well, stored in list 'r_neighbours'
            # router_neighbors = []
            count_ports = 0 #input an doutput ports required for that router
            count_ep_neighbors = 0
            for neighbors in value['neighbors']: #populating all dictionaries present above
                if soc_connections[neighbors]['is_Router']:
                    router_details[key]['r_neighbors'].append(neighbors)
                    count_ports += 1
                    a = int(key.split('_')[1])
                    b = int(neighbors.split('_')[1])
                    if a > b:
                        router_details[key]['r_wire'][neighbors] = f"{neighbors.split('_')[0]}_{b}_{a}" #router wires
                    else:
                        router_details[key]['r_wire'][neighbors] = f"{neighbors.split('_')[0]}_{a}_{b}"
                else:
                    count_ports += 2 #why using two ports for non router IP and one for router IP
                    count_ep_neighbors += 1
                    router_details[key]['ep_wire'] = f"{key}_EP"
                # router_neighbors.append(value['top_module_fname'])
            router_details[key]['top_module_fname'] = value['top_module_fname']   #below are other dictionary parameters
            router_details[key]['no_of_ports'] = count_ports
            router_details[key]['no_of_EPs'] = count_ep_neighbors
        else:
            ip = value['top_module_fname'] #filename for any IP top module
 
   

    # create router object to parse info of the router
    router_fname = "wb_bus_b3.v" 
    router = extract_IO.ExtractRtl(base_dir, router_fname)
    router.extract_headers()
    router.extract_io()
    router.extract_param()
    router.extract_module()

    

    #extracting clock and reset from inputs of router.sv in a list
    index_clk_rst = []
    router_clk_rst = []
    orig_router_inputs_temp = list(router.inputs) #router.inputs list that contains all inputs related to the router
    for i in range(len(orig_router_inputs_temp)): #copying and changing the values
        temp = orig_router_inputs_temp[i]
        if temp[temp[-1]] == 'clk' or temp[temp[-1]] == 'rst':
            index_clk_rst.append(i)
    count = 0
    for i in index_clk_rst:
        router_clk_rst.append(orig_router_inputs_temp[i - count][orig_router_inputs_temp[i - count][-1]])
        orig_router_inputs_temp.remove(orig_router_inputs_temp[i - count])
        count += 1

    router_inputs_dict = {} #dictionary that contains the router inputs
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

    in_from_noc = []
    in_from_noc_dict = {}
    out_to_noc = []
    out_to_noc_dict = {}
    resets = []
    clk = []

    router_inputs = []
    router_outputs = []    

    for inputs in compute_tile.inputs:
        if '_i' in inputs[inputs[-1]]:
            in_from_noc.append(inputs[inputs[-1]])
            in_from_noc_dict[inputs[inputs[-1]]] = inputs
            if inputs[inputs[-1]][4:] in router_inputs_dict:
                router_inputs.append(inputs[inputs[-1]][4:])
        elif ('rst' in inputs[inputs[-1]]) and ('dbg' not in inputs[inputs[-1]]):
            resets.append(inputs[inputs[-1]])
        elif 'clk' in inputs[inputs[-1]]:
            clk.append(inputs[inputs[-1]])
    for outputs in compute_tile.outputs:
        if '_o' in outputs[outputs[-1]]:
            out_to_noc.append(outputs[outputs[-1]])
            out_to_noc_dict[outputs[outputs[-1]]] = outputs
            if outputs[outputs[-1]][4:] in router_outputs_dict:
                router_outputs.append(outputs[outputs[-1]][4:])

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


# check line 187 to line 215 in soc_generic.py and add to this code
    router_wires = {}
    router_wires_in_order = {}
    for module, connections in soc_connections.items():
        if connections['is_Router']:
            router_wires[module] = {}
            router_wires_in_order[module] = {}
            # declaring wires for endpoint and router connections
            # router_wires[module][]
            r_ep = f'{module}_EP'
            # temp_out_t = []
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

###########################
    param_channels = 2
    param_flit_width = 32
    generated_soc_filename = input('Enter the filename of generated SoC\n')
    generated_soc_top_module_name = input('Enter the top module name of generated SoC\n')
    with open(os.path.join(base_dir, generated_soc_filename), 'w') as file:
        
        file.write(f'module {generated_soc_top_module_name}\n')
        for packages in total_packages:
            file.write(f"import {packages[0]}::{','.join(packages[1:])};\n")
        file.write('\n')
        file.write('(\n')

        

        #file.write('(\n')
        file.write('input clk,\n')
        file.write('input rst\n')
        file.write(');\n')
        file.write('\n\n')

        for rsts in resets:
            if rsts != 'rst':
                file.write(f'logic {rsts};\n')

        file.write(f'NR_MASTERS = ' ,int(Master_count),'str(;)''\n')
        file.write(f'NR_SLAVES = ' ,Slave_count,';''\n')
        for i in soc_connections:
            for j in soc_connections[i]:
                if(j=='is_Slave'):
                    if (soc_connections[i][j]==True):
                        slave_name=soc_connections[i]['top_module_fname']
                        file.write(f'localparam SLAVE_'+(soc_connections[i]['brand'])[0:-2])
      #  file.write(f'SLAVE_AES = 0;\n')

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

        file.write(f'wire [31:0]   pic_ints_i [0:CONFIG.CORES_PER_TILE-1];\n')
        file.write(f"assign pic_ints_i[0][31:4] = 28'h0;\n")
        file.write(f"assign pic_ints_i[0][1:0] = 2'b00;\n")

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

        with open(extract_IO.os.path.join(base_dir, "optimsoc_config_call.sv")) as file2:
            file.write(file2.read())
        file.write('\n\n')
        
        # start instantiating the endpoints and routers
        # router_wires_in_order[module][r_ep] = [temp_in, temp_out_in_order]
        for module, connections in soc_connections.items():
            if connections['is_Router']:
                # declaring wires for router-endpoint connections
                for i in range(len(router_wires_in_order[module][f"{module}_EP"][0])):
                    # temp = in_from_noc[i]
                    # router_details[module]['ep_wire']
                    temp1 = router_wires_in_order[module][f"{module}_EP"][0][i]
                    temp2 = temp1.split('_')[:3]
                    temp = list(in_from_noc_dict['_'.join(temp2)])
                    temp[temp[-1]] = temp1
                    file.write(f"wire [{router_details[module]['no_of_EPs'] - 1}:0]{''.join(temp[:-1])};\n")

                for i in range(len(router_wires_in_order[module][f"{module}_EP"][1])):
                    # temp = out_to_noc[i]
                    temp1 = router_wires_in_order[module][f"{module}_EP"][1][i]
                    temp2 = temp1.split('_')[:3]
                    temp = list(out_to_noc_dict['_'.join(temp2)])
                    temp[temp[-1]] = temp1
                    file.write(f"wire [{router_details[module]['no_of_EPs'] - 1}:0]{''.join(temp[:-1])};\n")
                   
                
                file.write('\n')
                r_obj = extract_IO.ExtractRtl(base_dir, connections['top_module_fname'])
                r_obj.extract_module()
                mod_name = r_obj.module_names[0]
                # count_ep = router_details[module]['no_of_EPs'] - 1
                mod_inst_name = f"{mod_name}_{module}_inst"

                #instantiating the ips and bus elements in the top module file
                file.write(f"{mod_name}\n")
                
                
                #unnecassary but keep for now to get reference in future
                file.write('#(.VCHANNELS (CHANNELS),\n')
                file.write(f".MASTERS ({router_details[module]['no_of_ports']}),\n")
                file.write(f".INPUTS ({router_details[module]['no_of_ports']}),\n")
                file.write(f".OUTPUTS ({router_details[module]['no_of_ports']}),\n")
                file.write(f".DESTS ({param_flit_width}))\n")

if __name__ == '__main__':
    soc_generator('D:\Code\SoC Compiler Tool', 'SoC_Compiler_input_ring.json')