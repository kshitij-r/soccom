import os
import json
import SoC_generic_AXI
import SoC_generic
import gen_define
import SoC_generic_noc
import time

def soc_main (base_dir_top, in_json_file_top):
    soc_config = None
    with open(os.path.join(base_dir_top, in_json_file_top)) as file:
        try:
            soc_config = json.load(file)
        except ValueError as e:
            print(e)


    for key, value in soc_config.items():
        #NOC
        if value['interconnect_noc' and 'lisnoc']:             
            in_json_file = value['architecture_definition']
            base_dir = value['base_directory']
            SoC_generic_noc.soc_generator_noc(base_dir, in_json_file)    

        #Wishbone
        if value['interconnect_bus' and 'wishbone_bus']:     
            in_json_file = value['architecture_definition']
            base_dir = value['base_directory']
            SoC_generic.soc_generator_wb(base_dir, in_json_file)
            # SoC_generic_AXI.soc_generator_AXI(base_dir, in_json_file)
        
        #AXI
        elif value['interconnect_bus' and 'axi4lite_bus']:     
            in_json_file = value['architecture_definition']
            base_dir = value['base_directory']
            SoC_generic_AXI.soc_generator_AXI(base_dir, in_json_file)
            gen_define.define_generator(base_dir, in_json_file)

        #AXI + Wishbone (Hybrid)
        elif value['interconnect_bus' and 'axi4lite_bus' and 'wishbone_bus']:#AXI + Wishbone
            in_json_file = value['architecture_definition']
            base_dir = value['base_directory']
            SoC_generic.soc_generator_wb(base_dir, in_json_file)
            SoC_generic_AXI.soc_generator_AXI(base_dir, in_json_file)
            gen_define.define_generator(base_dir, in_json_file)

        # NoC & SoC
        elif value['interconnect_noc' and 'interconnect_bus' and 'axi4lite_bus' and 'wishbone_bus']:
            in_json_file = value['architecture_definition']
            base_dir = value['base_directory']
            SoC_generic.soc_generator_wb(base_dir, in_json_file)  # wishbone
            SoC_generic_AXI.soc_generator_AXI(base_dir, in_json_file)  # AXI
            # gen_define.define_generator(base_dir, in_json_file)
            time.sleep(2)
            SoC_generic_noc.soc_generator_noc(base_dir, in_json_file) # NOC + SOC


if __name__ == '__main__':
    soc_main('/Users/kshitijraj/Code/master-repo/sw/soccom/soccom','base_config_wb.json')