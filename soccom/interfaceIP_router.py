import extract_IO


def interface_ip_router(ip_dir, ip_filename):
    obj1 = extract_IO.ExtractRtl(ip_dir, ip_filename)
    c_dir = '/Users/kshitijraj/Study /SoC Compiler Tool'
    c_filename = 'compute_tile_dm_spi.sv'
    obj2 = extract_IO.ExtractRtl(c_dir, c_filename)
    c_tile_contents = obj2.file_read()
    obj1.extract_module()
    ip_mod_name = obj1.module_names[0]
    repl_str = 'spi_top_x' #??
    c_tile_contents = extract_IO.re.sub(repl_str, ip_mod_name, c_tile_contents)
    c_tile_contents = extract_IO.re.sub('compute_tile_dm_spi',
                                        extract_IO.os.path.splitext(c_filename)[0][:-3] + ip_mod_name, c_tile_contents)
    top_ip_na = f'{c_filename[:-6]}{ip_mod_name}_t.sv'
    with open(extract_IO.os.path.join(ip_dir, top_ip_na), 'w+') as file:
        file.write(c_tile_contents)

    # create compute_tile object to parse info of the compute tile of IP (IP and Network Adapter)
    compute_tile = extract_IO.ExtractRtl(ip_dir, top_ip_na)
    compute_tile.extract_param()
    compute_tile.extract_headers()
    compute_tile.extract_io()
    compute_tile.extract_module()

    in_from_noc = []
    out_to_noc = []
    resets = []
    clk = []
    for inputs in compute_tile.inputs:
        if 'noc' in inputs[inputs[-1]]:
            in_from_noc.append(inputs[inputs[-1]])
        elif ('rst' in inputs[inputs[-1]]) and ('dbg' not in inputs[inputs[-1]]):
            resets.append(inputs[inputs[-1]])
        elif 'clk' in inputs[inputs[-1]]:
            clk.append(inputs[inputs[-1]])
    for outputs in compute_tile.outputs:
        if 'noc' in outputs[outputs[-1]]:
            out_to_noc.append(outputs[outputs[-1]])

    # create router object to parse info of the router
    router_fname = "noc_router.sv"
    router = extract_IO.ExtractRtl(ip_dir, router_fname)
    router.extract_headers()
    router.extract_io()
    router.extract_param()
    router.extract_module()

    total_packages = list(set(compute_tile.packages).union(set(router.packages)))
    total_includes = list(set(compute_tile.includes).union(set(router.includes)))

    noc_VCHANNELS = 2
    noc_INPUTS = 4
    noc_OUTPUTS = 4
    fname_ip_router = f'top_{ip_mod_name}_router.sv'

    index_clk_rst = []
    router_clk_rst = []
    orig_router_inputs = list(router.inputs)
    for i in range(len(orig_router_inputs)):
        temp = orig_router_inputs[i]
        if temp[temp[-1]] == 'clk' or temp[temp[-1]] == 'rst':
            index_clk_rst.append(i)
    count = 0
    for i in index_clk_rst:
        router_clk_rst.append(orig_router_inputs[i - count][orig_router_inputs[i - count][-1]])
        orig_router_inputs.remove(orig_router_inputs[i - count])
        count += 1

    wires_router_in = []
    wires_router_out = []
    for router_inputs in orig_router_inputs:
        wires_router_in.append(f"link_{router_inputs[router_inputs[-1]]}")
    for router_outputs in router.outputs:
        wires_router_out.append(f"link_{router_outputs[router_outputs[-1]]}")

    with open(extract_IO.os.path.join(ip_dir, fname_ip_router), 'w+') as file:
        for includes in total_includes:
            file.write(f'`include "{includes}"\n')
        file.write('module ' + extract_IO.os.path.splitext(fname_ip_router)[0] + '\n')
        for packages in total_packages:
            file.write(f'import {packages[0]}::{packages[1]};\n')
        file.write('\n')
        file.write('#(\n')
        file.write(f'parameter VCHANNELS = {noc_VCHANNELS},\n')
        file.write(f'parameter INPUTS = {noc_INPUTS},\n')
        file.write(f'parameter OUTPUTS = {noc_OUTPUTS},\n')
        file.write('parameter FLIT_WIDTH = 32,\n')

        file.write('parameter USE_DEBUG = 0,\n')
        file.write('parameter ENABLE_VCHANNELS = 0,\n')
        file.write('parameter integer NUM_CORES = 1 * 1,\n')
        file.write('parameter integer LMEM_SIZE = 32 * 1024\n')

        file.write(' )\n')
        file.write('(\n')
        file.write('input clk,\n')
        file.write('input rst,\n')

        for router_inputs in range(len(orig_router_inputs)):
            if 'ready' in wires_router_in[router_inputs]:
                temp = extract_IO.re.sub(r'OUTPUTS\s*[-]\s*1', 'OUTPUTS-3', orig_router_inputs[router_inputs][0])
                file.write(f"input {temp} {' '.join(orig_router_inputs[router_inputs][1:-2])}"
                           f" {orig_router_inputs[router_inputs][orig_router_inputs[router_inputs][-1]]},\n")
            else:
                temp = extract_IO.re.sub(r'INPUTS\s*[-]\s*1', 'INPUTS-3', orig_router_inputs[router_inputs][0])
                if len(orig_router_inputs[router_inputs]) > 2:
                    file.write(f"input {temp} {' '.join(orig_router_inputs[router_inputs][1:-2])}"
                               f" {orig_router_inputs[router_inputs][orig_router_inputs[router_inputs][-1]]},\n")
                else:
                    file.write(f"input {temp}"
                               f" {orig_router_inputs[router_inputs][orig_router_inputs[router_inputs][-1]]},\n")
        for router_outputs in range(len(wires_router_out) - 1):
            if 'ready' in wires_router_out[router_outputs]:
                temp = extract_IO.re.sub(r'INPUTS\s*[-]\s*1', 'INPUTS-3', router.outputs[router_outputs][0])
                file.write(f"output {temp} {' '.join(router.outputs[router_outputs][1:-2])}"
                           f" {router.outputs[router_outputs][router.outputs[router_outputs][-1]]},\n")
            else:
                temp = extract_IO.re.sub(r'OUTPUTS\s*[-]\s*1', 'OUTPUTS-3', router.outputs[router_outputs][0])
                if len(router.outputs[router_outputs]) > 2:
                    file.write(f"output {temp} {' '.join(router.outputs[router_outputs][1:-2])}"
                               f" {router.outputs[router_outputs][router.outputs[router_outputs][-1]]},\n")
                else:
                    file.write(f"output {temp}"
                               f" {router.outputs[router_outputs][router.outputs[router_outputs][-1]]},\n")

        if 'ready' in wires_router_out[-1]:
            temp = extract_IO.re.sub(r'INPUTS\s*[-]\s*1', 'INPUTS-3', router.outputs[-1][0])
            file.write(f"output {temp} {' '.join(router.outputs[-1][1:-2])}"
                       f" {router.outputs[-1][router.outputs[-1][-1]]}\n);\n")
        else:
            temp = extract_IO.re.sub(r'OUTPUTS\s*[-]\s*1', 'OUTPUTS-3', router.outputs[-1][0])
            if len(router.outputs[-1]) > 2:
                file.write(f"output {temp} {' '.join(router.outputs[-1][1:-2])}"
                           f" {router.outputs[-1][router.outputs[-1][-1]]}\n);\n")
            else:
                file.write(f"output {temp}"
                           f" {router.outputs[-1][router.outputs[-1][-1]]}\n);\n")

        file.write('\n\n')

        for rsts in resets:
            if rsts != 'rst':
                file.write(f'logic {rsts};\n')

        file.write('\n\n')

        with open(extract_IO.os.path.join(ip_dir, "optimsoc_config_call.sv")) as file2:
            file.write(file2.read())
        file.write('\n\n')

        # wire declaration
        for router_inputs in range(len(wires_router_in)):
            if 'ready' in wires_router_in[router_inputs]:
                temp = extract_IO.re.sub(r'OUTPUTS\s*[-]\s*1', 'OUTPUTS-3', orig_router_inputs[router_inputs][0])
                file.write(f"wire {temp} {' '.join(orig_router_inputs[router_inputs][1:-2])}"
                           f" {wires_router_in[router_inputs]};\n")
            else:
                temp = extract_IO.re.sub(r'INPUTS\s*[-]\s*1', 'INPUTS-3', orig_router_inputs[router_inputs][0])
                if len(orig_router_inputs[router_inputs]) > 2:
                    file.write(f"wire {temp} {' '.join(orig_router_inputs[router_inputs][1:-2])}"
                               f" {wires_router_in[router_inputs]};\n")
                else:
                    file.write(f"wire {temp}"
                               f" {wires_router_in[router_inputs]};\n")

        for router_outputs in range(len(wires_router_out)):
            if 'ready' in wires_router_out[router_outputs]:
                temp = extract_IO.re.sub(r'INPUTS\s*[-]\s*1', 'INPUTS-3', router.outputs[router_outputs][0])
                file.write(f"wire {temp} {' '.join(router.outputs[router_outputs][1:-2])}"
                           f" {wires_router_out[router_outputs]};\n")
            else:
                temp = extract_IO.re.sub(r'OUTPUTS\s*[-]\s*1', 'OUTPUTS-3', router.outputs[router_outputs][0])
                if len(router.outputs[router_outputs]) > 2:
                    file.write(f"wire {temp} {' '.join(router.outputs[router_outputs][1:-2])}"
                               f" {wires_router_out[router_outputs]};\n")
                else:
                    file.write(f"wire {temp}"
                               f" {wires_router_out[router_outputs]};\n")

        file.write('\n\n')

        file.write(router.module_names[0] + '\n')
        file.write('#(')
        for params in range(len(router.parameters)):
            if router.parameters[params][0][0] == 'VCHANNELS':
                file.write(f'.VCHANNELS ({noc_VCHANNELS}),\n')
            elif router.parameters[params][1] == "'x":
                temp = router.parameters[params][0][0]
                if temp == 'INPUTS':
                    file.write(f'.INPUTS ({noc_INPUTS}),\n')
                elif temp == 'OUTPUTS':
                    file.write(f'.OUTPUTS ({noc_OUTPUTS}),\n')
                elif temp == 'DESTS':
                    file.write('.DESTS (32))\n')
        file.write('\n')
        file.write(f'{router.module_names[0]}_{compute_tile.module_names[0]}(\n')

        # start interfacing router inputs and outputs
        for clk_rst in router_clk_rst:
            file.write(f'.{clk_rst} ({clk_rst}),\n')

        for i in range(len(wires_router_in)):
            temp = orig_router_inputs[i]
            file.write(f'.{temp[temp[-1]]} ({{{temp[temp[-1]]},{wires_router_in[i]}}}),\n')
        for i in range(len(wires_router_out) - 1):
            temp = router.outputs[i]
            file.write(f'.{temp[temp[-1]]} ({{{temp[temp[-1]]},{wires_router_out[i]}}}),\n')
        file.write(f'.{router.outputs[-1][router.outputs[-1][-1]]}'
                   f' ({{{router.outputs[-1][router.outputs[-1][-1]]},{wires_router_out[-1]}}}));\n')
        file.write('\n\n')

        # instantiating the compute_tile for the given IP
        file.write(f'{compute_tile.module_names[0]}\n')
        file.write('#(.CONFIG(CONFIG),\n')
        file.write('.ID(1),\n')
        file.write('.COREBASE(1*CONFIG.CORES_PER_TILE),\n')
        file.write('.DEBUG_BASEID((CONFIG.DEBUG_LOCAL_SUBNET << (16 - CONFIG.DEBUG_SUBNET_BITS))'
                   '+ 1 + (1*CONFIG.DEBUG_MODS_PER_TILE)))\n')
        file.write('\n')
        file.write(f'{compute_tile.module_names[0]}_inst(\n')
        for clks in clk:
            file.write(f'.{clks} ({clks}),\n')
        for rsts in resets:
            file.write(f'.{rsts} ({rsts}),\n')

        for i in range(len(wires_router_out)):
            file.write(f'.{in_from_noc[i]} ({wires_router_out[i]}),\n')
        for i in range(len(wires_router_in) - 1):
            file.write(f'.{out_to_noc[i]} ({wires_router_in[i]}),\n')
        file.write(f'.{out_to_noc[-1]} ({wires_router_in[-1]}));\n')
        file.write('\n\n')
        file.write('endmodule\n')
    return fname_ip_router


if __name__ == '__main__':
    interface_ip_router("/Users/kshitijraj/Study /SoC Compiler Tool", "fft_top.v")
    #soc_generator(obj.ExtractRtl)
