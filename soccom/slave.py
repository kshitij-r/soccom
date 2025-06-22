ip_input = ['wbm_ack_i', 'wbm_dat_i', 'wbm_cyc_i', 'wbm_cab_i']
ip_input_sorted = sorted(ip_input)
#print(ip_input_sorted)
ip_output = ['wbm_adr_o', 'wbm_cyc_o', 'wbm_dat_o',
          'wbm_sel_o', 'wbm_stb_o', 'wbm_we_o']
ip_output_sorted = sorted(ip_output)
#print(ip_output_sorted)
s_input_wires = ['bussl_adr_i','bussl_cyc_i','bussl_dat_i','bussl_sel_i','bussl_stb_i',
                           'bussl_we_i','bussl_cab_i','bussl_cti_i','bussl_bte_i']
slave_input_wires = sorted(s_input_wires)
#print(slave_input_wires)
s_output_wires =   ['bussl_ack_o','bussl_rty_o', 'bussl_err_o','bussl_dat_o','bussl_cyc_o','bussl_we_o']
slave_output_wires = sorted(s_output_wires)
#print(slave_output_wires)
old_ip_i = []
old_ip_o = []
old_bus_i = []
old_bus_o = []
ip_i = []
ip_o = []
bus_i = []
bus_o = []
for i in ip_input:
    ip_i_split = i.split('_')
    old_ip_i.append(ip_i_split[1])
for j in ip_output:
    ip_o_split = j.split('_')
    old_ip_o.append(ip_o_split[1])
for x in s_input_wires:
    bus_i_split = x.split('_')
    old_bus_i.append(bus_i_split[1])
for y in s_output_wires:
    bus_o_split = y.split('_')
    old_bus_o.append(bus_o_split[1])
ip_i=sorted(old_ip_i)
ip_o=sorted(old_ip_o)
bus_i=sorted(old_bus_i)
bus_o=sorted(old_bus_o)
print(ip_i)
print(ip_o)
print(bus_i)
print(bus_o)
index_val=0
#intitializing for input signals
for i,j in enumerate(ip_i):
    try:
        if j in bus_i:
            index_val = bus_i.index(j)
            print(".",ip_input_sorted[i],"(",slave_input_wires[index_val],")",",")
        else:
            pass
    except Exception:
        pass  
# #intilialising the output signals
for i,j in enumerate(ip_o):
    try:
        if j in bus_o:
            index_val = bus_o.index(j)
            print(".",ip_output_sorted[i],"(",slave_output_wires[index_val],")",",")
        else:
            pass
    except Exception:
        pass  
