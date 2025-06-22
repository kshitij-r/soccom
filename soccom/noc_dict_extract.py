import os
import json
import SoC_generic_AXI
import SoC_generic
import gen_define
import SoC_generic_noc



def soc_main (base_dir, in_json_file):
    noc_config = None
    noc_dict = {}
    EP_number = []
    EP = []
    
    with open(os.path.join(base_dir, in_json_file)) as file:
        try:
            noc_config = json.load(file)
        except ValueError as e:
            print(e)
    
    for key,value in noc_config.items():
        for nested_key, nested_value in value.items():
            if (nested_value == 'NOC'):
                EP_number.append(key)
                EP.append(noc_config[key])

    noc_dict = dict(zip(EP_number, EP))
    print(noc_dict)

if __name__ == '__main__':
    soc_main('D:\\Code\\SoC Compiler Tool','demo_noc.json')
