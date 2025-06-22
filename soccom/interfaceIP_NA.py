import extract_IO
#interfaces any non-router IP with the network adapter and write the whole thing in a new file

def interface_ip_na(ip_dir, ip_filename):
    if ip_filename == 'picorv32.sv':    #hardcoded the value for risc 5 processor file to return the 'Compute_Tile_RV32.sv' file. 
        return 'Compute_Tile_RV32.sv'
    obj1 = extract_IO.ExtractRtl(ip_dir, ip_filename) 
    c_dir = "/Users/kshitijraj/Study /SoC Compiler Tool"  #using a template module and making changes in that
    c_filename = 'compute_tile_dm_spi.sv' #template module file name
    obj2 = extract_IO.ExtractRtl(c_dir, c_filename)
    c_tile_contents = obj2.file_read()
    obj1.extract_module()
    ip_mod_name = obj1.module_names[0]
    repl_str = 'spi_top_x'
    c_tile_contents = extract_IO.re.sub(repl_str, ip_mod_name, c_tile_contents)
    c_tile_contents = extract_IO.re.sub('compute_tile_dm_spi',
                                        extract_IO.os.path.splitext(c_filename)[0][:-3] + ip_mod_name, c_tile_contents)
    c_tile_contents = extract_IO.re.sub('ST0', ip_mod_name + '_inst', c_tile_contents)
    c_tile_contents = extract_IO.re.sub('u_na', f'{ip_mod_name}_na', c_tile_contents)
    top_ip_na = f'{c_filename[:-6]}{ip_mod_name}_t.sv'
    with open(extract_IO.os.path.join(ip_dir, top_ip_na), 'w+') as file:
        file.write(c_tile_contents)
    #print(top_ip_na)
    return top_ip_na # top_ip_na is the name of the output file
