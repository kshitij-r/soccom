## SoCCom: SoC Compiler

 SoCCom is a open-source framework for automated generation of flexible and scalable System-on-Chip (SoC) and Network-on-Chip (NoC) architectures.

### Tool Flow
- #### Parse Configuration
  - Reads a JSON spec defining IP blocks, addresses, interconnect fabrics, and bridge setups.
- #### RTL Parsing
  - Extracts bus interfaces (e.g. Wishbone, AXI4‑Lite) from existing SystemVerilog RTL IPs.
- #### Wrapper Generation
  - Produces synthesizable RTL wrappers around each IP core to standardize interconnect compatibility.
- #### SoC Assembly
  - Connects cores via the chosen bus fabrics, instantiates bridges if needed, and generates the SoC-top RTL.
- #### Output
  - Outputs a ready-to-synthesize SystemVerilog RTL. Designers can then perform simulation, synthesis, or PPA analysis.

### Prerequisites
- Python 3.8+
- Verilog/SystemVerilog RTL files for your IP blocks

### SoC/NoC Configuration
SoCCom requires two valid JSON configuration files:
- base_config_{-interconnect_name-}.json
  - This configuration contains the SoC/NoC specification providing the following information (multiple configuration files are provided in the repo):
   ```json
    {
        "base_config": {
            "interconnect_noc": false,
            "lisnoc": false,
            "interconnect_bus": true,
            "wishbone_bus": true,
            "axi4lite_bus": false,
            "security_policy_engine": null,
            "test_wrapper": null,
            "smart_security_wrapper": null,
            "architecture_definition": "hybrid_wb_1.json",
            "base_directory": "/Users/kshitijraj/Study /SoC Compiler Tool"
        }
    }
  ```
  - architecture_definition configuration which outlines the hierarchy and connectivity structure of the SoC/NoC (multiple configuration files are provided in the repo):  
     ```json
     {"R_1":
        {
        "IP_name": "wb_bus_b3.v",
        "config" : "SLAVE",
        "neighbors": ["EP_0","EP_1","EP_2","EP_3"],
        "IP_type": "non_memory",
        "size"   : "32'h0000_0000",
        "bus_type" : "Wishbone",
        "is_Router": true
        },
        "EP_O":
        {
        "IP_name": "aes_top.v",
        "neighbors": ["R_1"],
        "config" : "SLAVE",
        "IP_type": "non_memory",
        "size"   : "32'h0000_0000",
        "bus_type" : "Wishbone",
        "is_Router": false
        },
        "EP_1":
        {
        "IP_name": "picorv32_top.v",
        "config" : "MASTER",
        "neighbors": ["R_1"],
        "IP_type": "non_memory",
        "size"   : "32'h0000_0000",
        "bus_type" : "Wishbone",
        "is_Router": false
        }
    }
     ```
#### Running SoCCom
- Once you have both the configuration files set up based on your requirement, we are ready to run soccom
- Update the confiuration file and path in the `soc_main.py`
    ```python
    if __name__ == '__main__':
        soc_main('Path to the tool','base_config json file')
    ```
- Execute the command
    ```python
        python3 soc_main.py
    ```



**Note** Please change the paths in the configuration files and other places. This is a very old codebase which I wrote when I was not good at programming. I will fix this when I get time

If you use this tool in your research, please cite the following work:
```bibtex
@ARTICLE{9714864,
  author={Deb Nath, Atul Prasad and Raj, Kshitij and Bhunia, Swarup and Ray, Sandip},
  journal={IEEE Transactions on Very Large Scale Integration (VLSI) Systems}, 
  title={SoCCom: Automated Synthesis of System-on-Chip Architectures}, 
  year={2022},
  volume={30},
  number={4},
  pages={449-462},
  keywords={Hardware design languages;System-on-chip;Topology;Multicore processing;Fabrics;Benchmark testing;Space exploration;Benchmarking;intellectual property (IP) standardization;system-on-chip (SoC) security;SoC synthesis},
  doi={10.1109/TVLSI.2022.3141326}}

```