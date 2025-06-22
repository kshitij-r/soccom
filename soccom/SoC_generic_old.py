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

    # soc_connections = {'EP_1': {'neighbors': ['R_1'], 'is_Router': False, 'top_module_fname': 'EP_1.v'},
    #                    'EP_2': {'neighbors': ['R_1'], 'is_Router': False, 'top_module_fname': 'EP_2.v'},
    #                    'EP_3': {'neighbors': ['R_1'], 'is_Router': False, 'top_module_fname': 'EP_3.v'},
    #                    'R_1': {'neighbors': ['EP_1', 'EP_2', 'EP_3', 'R_2'], 'is_Router': True,
    #                            'top_module_fname': 'R_1.v'},
    #                    'R_2': {'neighbors': ['EP_4', 'EP_5', 'EP_6', 'R_1'], 'is_Router': True,
    #                            'top_module_fname': 'R_2.v'},
    #                    'EP_4': {'neighbors': ['R_2'], 'is_Router': False, 'top_module_fname': 'EP_4.v'},
    #                    'EP_5': {'neighbors': ['R_2'], 'is_Router': False, 'top_module_fname': 'EP_5.v'},
    #                    'EP_6': {'neighbors': ['R_2'], 'is_Router': False, 'top_module_fname': 'EP_6.v'}
    #                    }

    # soc_connections = {'EP_1': {'neighbors': ['R_1'], 'is_Router': False, 'top_module_fname': 'fft_top.v'},
    #                    'R_1': {'neighbors': ['EP_1', 'R_4', 'R_2'], 'is_Router': True,
    #                            'top_module_fname': 'noc_router.sv'},
    #                    'EP_2': {'neighbors': ['R_2'], 'is_Router': False, 'top_module_fname': 'aes_top.v'},
    #                    'R_2': {'neighbors': ['EP_2', 'R_1', 'R_3'], 'is_Router': True,
    #                            'top_module_fname': 'noc_router.sv'},
    #                    'EP_3': {'neighbors': ['R_3'], 'is_Router': False, 'top_module_fname': 'md5_top.v'},
    #                    'R_3': {'neighbors': ['EP_3', 'R_2', 'R_4'], 'is_Router': True,
    #                            'top_module_fname': 'noc_router.sv'},
    #                    'EP_4': {'neighbors': ['R_4'], 'is_Router': False, 'top_module_fname': 'spi_topMY1.v'},
    #                    'R_4': {'neighbors': ['EP_4', 'R_3', 'R_1'], 'is_Router': True,
    #                            'top_module_fname': 'noc_router.sv'}
    #                    }
    # soc_connections = {'EP_1': {'neighbors': ['R_1'], 'is_Router': False, 'top_module_fname': 'fft_top.v'},
    #                    'R_1': {'neighbors': ['EP_1', 'EP_2', 'R_2'], 'is_Router': True,
    #                            'top_module_fname': 'noc_router.sv'},
    #                    'EP_2': {'neighbors': ['R_1'], 'is_Router': False, 'top_module_fname': 'aes_top.v'},
    #                    'R_2': {'neighbors': ['EP_3', 'R_1', 'EP_4'], 'is_Router': True,
    #                            'top_module_fname': 'noc_router.sv'},
    #                    'EP_3': {'neighbors': ['R_2'], 'is_Router': False, 'top_module_fname': 'md5_top.v'},
    #
    #                    'EP_4': {'neighbors': ['R_2'], 'is_Router': False, 'top_module_fname': 'spi_topMY1.v'}
    #                    }

    router_details = {}
    ip = None
    for key, value in soc_connections.items():
        if value['is_Router']:
            router_details[key] = {}
            router_details[key]['r_wire'] = {}
            router_details[key]['r_neighbors'] = []
            # router_neighbors = []
            count_ports = 0
            count_ep_neighbors = 0
            for neighbors in value['neighbors']:
                if soc_connections[neighbors]['is_Router']:
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
                # router_neighbors.append(value['top_module_fname'])
            router_details[key]['top_module_fname'] = value['top_module_fname']
            router_details[key]['no_of_ports'] = count_ports
            router_details[key]['no_of_EPs'] = count_ep_neighbors
        else:
            ip = value['top_module_fname']

    # for routers, details in router_details.items():
    #     if not details['no_of_ports'] == 5:
    #         new_router_filename = details['top_module_fname'] + f'_{routers}'
    #         # with open(os.path.join(base_dir, details['top_module_fname'])) as file:
    #         #     router_contents = file.read()
    #
    #         # router_contents = re.sub(r'parameter\s+INPUTS\s+=\s+5', r'\s*parameter\s+INPUTS\s+=\s+' +
    #         #                          str(details['no_of_ports']), router_contents)
    #         # router_contents = re.sub(r'\s*parameter\s+OUTPUTS\s+=\s+5', r'\s*parameter\s+OUTPUTS\s+=\s+' +
    #         #                          str(details['no_of_ports']), router_contents)
    #         # router_contents = re.sub(r'module\s+noc_router', r'module\s+noc_router_' + routers.split('_')[1],
    #         #                          router_contents)
    #         # with open(os.path.join(base_dir, new_router_filename), 'w') as file2:
    #         #     file2.write(router_contents)
    #
    #         details['top_module_fname'] = new_router_filename

    # create router object to parse info of the router
    router_fname = "noc_router.sv"
    router = extract_IO.ExtractRtl(base_dir, router_fname)
    router.extract_headers()
    router.extract_io()
    router.extract_param()
    router.extract_module()

    # noc_VCHANNELS = 2
    # noc_INPUTS = 4
    # noc_OUTPUTS = 4
    # fname_ip_router = f'top_{ip_mod_name}_router.sv'

    index_clk_rst = []
    router_clk_rst = []
    orig_router_inputs_temp = list(router.inputs)
    for i in range(len(orig_router_inputs_temp)):
        temp = orig_router_inputs_temp[i]
        if temp[temp[-1]] == 'clk' or temp[temp[-1]] == 'rst':
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

    in_from_noc = []
    in_from_noc_dict = {}
    out_to_noc = []
    out_to_noc_dict = {}
    resets = []
    clk = []

    router_inputs = []
    router_outputs = []

    for inputs in compute_tile.inputs:
        if 'noc' in inputs[inputs[-1]]:
            in_from_noc.append(inputs[inputs[-1]])
            in_from_noc_dict[inputs[inputs[-1]]] = inputs
            if inputs[inputs[-1]][4:] in router_inputs_dict:
                router_inputs.append(inputs[inputs[-1]][4:])
        elif ('rst' in inputs[inputs[-1]]) and ('dbg' not in inputs[inputs[-1]]):
            resets.append(inputs[inputs[-1]])
        elif 'clk' in inputs[inputs[-1]]:
            clk.append(inputs[inputs[-1]])
    for outputs in compute_tile.outputs:
        if 'noc' in outputs[outputs[-1]]:
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
            # have to define wires for router router connections

    param_channels = 2
    param_flit_width = 32
    generated_soc_filename = input('Enter the filename of generated SoC\n')
    generated_soc_top_module_name = input('Enter the top module name of generated SoC\n')
    with open(os.path.join(base_dir, generated_soc_filename), 'w') as file:
        for includes in total_includes:
            file.write(f'`include "{includes}"\n')
        file.write(f'module {generated_soc_top_module_name}\n')
        for packages in total_packages:
            file.write(f"import {packages[0]}::{','.join(packages[1:])};\n")
        file.write('\n')
        file.write('#(\n')

        file.write('parameter USE_DEBUG = 0,\n')
        file.write('parameter ENABLE_VCHANNELS = 0,\n')
        file.write('parameter integer NUM_CORES = 1 * 1,\n')
        file.write('parameter integer LMEM_SIZE = 32 * 1024\n')
        file.write(' )\n')

        file.write('(\n')
        file.write('input clk,\n')
        file.write('input rst\n')
        file.write(');\n')
        file.write('\n\n')

        for rsts in resets:
            if rsts != 'rst':
                file.write(f'logic {rsts};\n')

        file.write(f'localparam CHANNELS = {param_channels};\n')
        file.write(f'localparam VCHANNELS = {param_channels};\n')
        file.write(f'localparam FLIT_WIDTH = {param_flit_width};\n')

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
                    # temp = list(out_to_noc_dict[out_to_noc[i]])
                    # temp[temp[-1]] = router_wires[module][f'{module}_EP'][1][i]
                    # file.write(f"wire [{router_details[module]['no_of_EPs'] - 1}:0]{''.join(temp[:-1])};\n")
                # for wires in router_wires[module][f'{module}_EP'][0]:
                #     file.write(wires)
                #     # f"wire [{router_details[module]['no_of_EPs'] - 1}:0]{''.join(inputs[:-1])}_"
                #     #                        f"{router_details[module]['ep_wire']};\n")
                # for wires in router_wires[module][f'{module}_EP'][1]:
                #     file.write(wires)

                # instantiating the endpoints
                file.write('\n\n')
                count_ep = router_details[module]['no_of_EPs'] - 1
                neighbor_router_wires = []
                for neighbors in connections['neighbors']:
                    if not soc_connections[neighbors]['is_Router']:
                        ip_na_connection = interfaceIP_NA.interface_ip_na\
                            (base_dir, soc_connections[neighbors]['top_module_fname'])
                        ip_na_obj = extract_IO.ExtractRtl(base_dir, ip_na_connection)
                        ip_na_obj.extract_module()
                        ip_na_top_module = ip_na_obj.module_names[0]
                        file.write(f'{ip_na_top_module}\n')
                        file.write('#(.CONFIG(CONFIG),\n')
                        file.write('.ID(1),\n')
                        file.write('.COREBASE(1*CONFIG.CORES_PER_TILE),\n')
                        file.write('.DEBUG_BASEID((CONFIG.DEBUG_LOCAL_SUBNET << (16 - CONFIG.DEBUG_SUBNET_BITS))'
                                   '+ 1 + (1*CONFIG.DEBUG_MODS_PER_TILE)))\n')
                        file.write('\n')
                        file.write(f'{ip_na_top_module}_inst(\n')
                        for clks in clk:
                            file.write(f'.{clks} ({clks}),\n')
                        for rsts in resets:
                            file.write(f'.{rsts} ({rsts}),\n')

                        for i in range(len(in_from_noc)):
                            file.write(f".{in_from_noc[i]} ({router_wires[module][f'{module}_EP'][0][i]}[{count_ep}]),"
                                       f"\n")
                        for i in range(len(out_to_noc) - 1):
                            file.write(f".{out_to_noc[i]} ({router_wires[module][f'{module}_EP'][1][i]}[{count_ep}]),"
                                       f"\n")
                        file.write(f".{out_to_noc[-1]} ({router_wires[module][f'{module}_EP'][1][-1]}[{count_ep}]));\n")
                        file.write('\n\n')
                        count_ep -= 1

                    else:
                        temp_r_wire = module.split('_')
                        if router_details[module]['r_wire'][neighbors] == f"{temp_r_wire[0]}_" \
                                f"{temp_r_wire[1]}_{neighbors.split('_')[1]}":
                            neighbor_router_wires.append(neighbors)

                # declaring wires for router-router connections
                neighbor_r_wire = {}
                for neighbor_router_wire in neighbor_router_wires:
                    neighbor_r_wire[neighbor_router_wire] = {}
                    for inputs in router_inputs:
                        temp = list(router_inputs_dict[inputs])
                        temp[temp[-1]] = f"{temp[temp[-1]]}_{router_details[module]['r_wire'][neighbor_router_wire]}"
                        neighbor_r_wire[neighbor_router_wire]['inputs'] = temp[temp[-1]]
                        file.write(f"wire {''.join(temp[1:-1])};\n")

                    for outputs in router_outputs:
                        temp = list(router_outputs_dict[outputs])
                        temp[temp[-1]] = f"{temp[temp[-1]]}_{router_details[module]['r_wire'][neighbor_router_wire]}"
                        neighbor_r_wire[neighbor_router_wire]['outputs'] = temp[temp[-1]]
                        file.write(f"wire {''.join(temp[1:-1])};\n")

                file.write('\n')

                r_obj = extract_IO.ExtractRtl(base_dir, connections['top_module_fname'])
                r_obj.extract_module()
                mod_name = r_obj.module_names[0]
                # count_ep = router_details[module]['no_of_EPs'] - 1
                mod_inst_name = f"{mod_name}_{module}_inst"

                file.write(f"{mod_name}\n")
                file.write('#(.VCHANNELS (CHANNELS),\n')
                file.write(f".INPUTS ({router_details[module]['no_of_ports']}),\n")
                file.write(f".OUTPUTS ({router_details[module]['no_of_ports']}),\n")
                file.write(f".DESTS ({param_flit_width}))\n")
                # file.write(".ROUTES ({32*OUTPUTS{1'b0}}))\n")
                file.write('\n')
                file.write(f"{mod_inst_name}(\n")
                for clk_rst in router_clk_rst:
                    file.write(f'.{clk_rst} ({clk_rst}),\n')
                for i in range(len(router_inputs)):
                    count_ep = router_details[module]['no_of_EPs'] - 1
                    file.write(f".{router_inputs[i]} ({{")
                    # router_details[key]['no_of_EPs'] = count_ep_neighbors
                    for j in range(router_details[module]['no_of_EPs']):
                        # router_wires[module][f'{module}_EP'][0][i]
                        file.write(f"{router_wires_in_order[module][f'{module}_EP'][1][i]}[{count_ep}],")
                        # tmp2 = router_inputs[i].split('_')
                        # temp_set = set(router_wires[module][f'{module}_EP'][1])
                        # if tmp2[0] == 'in':
                        #     tmp2[0] = 'out'
                        # else:
                        #     tmp2[0] = 'in'
                        # tmp2 = '_'.join(tmp2)
                        # tmp = f"noc_{tmp2}_{module}_EP"
                        # if tmp in temp_set:
                        #     file.write(f"{tmp}[{count_ep}],")
                        count_ep -= 1

                    # tmp = set(router_outputs)
                    for j in range(len(router_details[module]['r_neighbors']) - 1):
                        neighbor_name = router_details[module]['r_neighbors'][j]
                        if router_details[module]['r_wire'][neighbor_name] == f"{module.split('_')[0]}_" \
                                f"{module.split('_')[1]}_{neighbor_name.split('_')[1]}":
                            file.write(f"{router_inputs[i]}_{router_details[module]['r_wire'][neighbor_name]},")
                        else:
                            file.write(f"{router_outputs_in_order[i]}_"
                                       f"{router_details[module]['r_wire'][neighbor_name]},")
                            # tmp2 = router_inputs[i].split('_')
                            # if tmp2[0] == 'in':
                            #     tmp2[0] = 'out'
                            # else:
                            #     tmp2[0] = 'in'
                            # tmp2 = '_'.join(tmp2)
                            # if tmp2 in tmp:
                            #     file.write(f"{tmp2}_{router_details[module]['r_wire'][neighbor_name]},")

                    neighbor_name = router_details[module]['r_neighbors'][-1]
                    if router_details[module]['r_wire'][neighbor_name] == f"{module.split('_')[0]}_" \
                            f"{module.split('_')[1]}_{neighbor_name.split('_')[1]}":
                        file.write(f"{router_inputs[i]}_{router_details[module]['r_wire'][neighbor_name]}}}),\n")
                    else:
                        file.write(f"{router_outputs_in_order[i]}_{router_details[module]['r_wire'][neighbor_name]}}})"
                                   f",\n")
                        # tmp2 = router_inputs[-1].split('_')
                        # if tmp2[0] == 'in':
                        #     tmp2[0] = 'out'
                        # else:
                        #     tmp2[0] = 'in'
                        # tmp2 = '_'.join(tmp2)
                        # if tmp2 in tmp:
                        #     file.write(f"{tmp2}_{router_details[module]['r_wire'][neighbor_name]}}}),\n")

                # instantiating router outputs
                # temp_set = set(router_wires[module][f'{module}_EP'][0])
                for i in range(len(router_outputs_in_order) - 1):
                    count_ep = router_details[module]['no_of_EPs'] - 1
                    file.write(f".{router_outputs_in_order[i]} ({{")
                    # router_details[key]['no_of_EPs'] = count_ep_neighbors
                    for j in range(router_details[module]['no_of_EPs']):
                        file.write(f"{router_wires_in_order[module][f'{module}_EP'][0][i]}[{count_ep}],")
                        # tmp2 = router_outputs[i].split('_')
                        # if tmp2[0] == 'in':
                        #     tmp2[0] = 'out'
                        # else:
                        #     tmp2[0] = 'in'
                        # tmp2 = '_'.join(tmp2)
                        # tmp = f"noc_{tmp2}_{module}_EP"
                        # if tmp in temp_set:
                        #     file.write(f"{tmp}[{count_ep}],")
                        # router_wires[module][f'{module}_EP'][0][i]
                        # file.write(f"{router_wires[module][f'{module}_EP'][0][i]}[{count_ep}],")
                        count_ep -= 1

                    # tmp = set(router_inputs)
                    for j in range(len(router_details[module]['r_neighbors']) - 1):
                        neighbor_name = router_details[module]['r_neighbors'][j]
                        if router_details[module]['r_wire'][neighbor_name] == f"{module.split('_')[0]}_" \
                                f"{module.split('_')[1]}_{neighbor_name.split('_')[1]}":
                            file.write(f"{router_outputs_in_order[i]}_"
                                       f"{router_details[module]['r_wire'][neighbor_name]},")
                        else:
                            file.write(f"{router_inputs[i]}_{router_details[module]['r_wire'][neighbor_name]},")
                            # tmp2 = router_outputs[i].split('_')
                            # if tmp2[0] == 'in':
                            #     tmp2[0] = 'out'
                            # else:
                            #     tmp2[0] = 'in'
                            # tmp2 = '_'.join(tmp2)
                            # if tmp2 in tmp:
                            #     file.write(f"{tmp2}_{router_details[module]['r_wire'][neighbor_name]},")
                            # file.write(f"{router_inputs[i]}_{router_details[module]['r_wire'][neighbor_name]},")

                    neighbor_name = router_details[module]['r_neighbors'][-1]
                    if router_details[module]['r_wire'][neighbor_name] == f"{module.split('_')[0]}_" \
                            f"{module.split('_')[1]}_{neighbor_name.split('_')[1]}":
                        file.write(f"{router_outputs_in_order[i]}_"
                                   f"{router_details[module]['r_wire'][neighbor_name]}}}),\n")
                    else:
                        file.write(f"{router_inputs[i]}_{router_details[module]['r_wire'][neighbor_name]}}}),\n")
                        # tmp2 = router_inputs[-1].split('_')
                        # if tmp2[0] == 'in':
                        #     tmp2[0] = 'out'
                        # else:
                        #     tmp2[0] = 'in'
                        # tmp2 = '_'.join(tmp2)
                        # if tmp2 in tmp:
                        #     file.write(f"{tmp2}_{router_details[module]['r_wire'][neighbor_name]}}}),\n")

                count_ep = router_details[module]['no_of_EPs'] - 1
                file.write(f".{router_outputs_in_order[-1]} ({{")
                for j in range(router_details[module]['no_of_EPs']):
                    file.write(f"{router_wires_in_order[module][f'{module}_EP'][0][-1]}[{count_ep}],")
                    # router_wires[module][f'{module}_EP'][0][i]
                    # tmp2 = router_outputs[-1].split('_')
                    # if tmp2[0] == 'in':
                    #     tmp2[0] = 'out'
                    # else:
                    #     tmp2[0] = 'in'
                    # tmp2 = '_'.join(tmp2)
                    # tmp = f"noc_{tmp2}_{module}_EP"
                    # if tmp in temp_set:
                    #     file.write(f"{tmp}[{count_ep}],")
                    count_ep -= 1

                # tmp = set(router_inputs)
                for j in range(len(router_details[module]['r_neighbors']) - 1):
                    neighbor_name = router_details[module]['r_neighbors'][j]
                    if router_details[module]['r_wire'][neighbor_name] == f"{module.split('_')[0]}_" \
                            f"{module.split('_')[1]}_{neighbor_name.split('_')[1]}":
                        file.write(f"{router_outputs_in_order[-1]}_{router_details[module]['r_wire'][neighbor_name]},")
                    else:
                        file.write(f"{router_inputs[-1]}_{router_details[module]['r_wire'][neighbor_name]},")
                        # tmp2 = router_outputs[-1].split('_')
                        # if tmp2[0] == 'in':
                        #     tmp2[0] = 'out'
                        # else:
                        #     tmp2[0] = 'in'
                        # tmp2 = '_'.join(tmp2)
                        # if tmp2 in tmp:
                        #     file.write(f"{tmp2}_{router_details[module]['r_wire'][neighbor_name]},")
                        # file.write(f"{router_inputs[-1]}_{router_details[module]['r_wire'][neighbor_name]},")

                neighbor_name = router_details[module]['r_neighbors'][-1]
                if router_details[module]['r_wire'][neighbor_name] == f"{module.split('_')[0]}_" \
                        f"{module.split('_')[1]}_{neighbor_name.split('_')[1]}":
                    file.write(f"{router_outputs_in_order[-1]}_"
                               f"{router_details[module]['r_wire'][neighbor_name]}}}));\n")
                else:
                    file.write(f"{router_inputs[-1]}_{router_details[module]['r_wire'][neighbor_name]}}}));\n")
                    # tmp2 = router_inputs[-1].split('_')
                    # if tmp2[0] == 'in':
                    #     tmp2[0] = 'out'
                    # else:
                    #     tmp2[0] = 'in'
                    # tmp2 = '_'.join(tmp2)
                    # if tmp2 in tmp:
                    #     file.write(f"{tmp2}_{router_details[module]['r_wire'][neighbor_name]}}}),\n")

                    # file.write(f"{router_inputs[-1]}_{router_details[module]['r_wire'][neighbor_name]}}}));\n")
                file.write('\n\n')

        file.write('endmodule\n')


if __name__ == '__main__':
    soc_generator('/Users/kshitijraj/Study /SoC Compiler Tool', 'SoC_Compiler_input_tree.json')








