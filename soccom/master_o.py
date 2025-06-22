ip_input = ['wbm_ack_i', 'wbm_dat_i']
ip_input_sorted = sorted(ip_input)

ip_output = ['wbm_adr_o', 'wbm_cyc_o', 'wbm_dat_o',
          'wbm_sel_o', 'wbm_stb_o', 'wbm_we_o']
ip_output_sorted = sorted(ip_output)

m_input_wires = ['busms_ack_i_flat','busms_rty_i_flat','busms_err_i_flat','busms_dat_i_flat']
master_input_wires = sorted(m_input_wires)

m_output_wires =   ['busms_adr_o_flat','busms_cyc_o_flat','busms_dat_o_flat','busms_sel_o_flat','busms_stb_o_flat',
                   'busms_we_o_flat','busms_cab_o_flat','busms_cti_o_flat','busms_bte_o_flat']
master_output_wires = sorted(m_output_wires)

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
#intitializing for input signals
size_i = len(ip_i)
size_o = len(ip_o)
size_oo = len(bus_o)
print(size_o)
#print("size ",size)
for i,j in enumerate(ip_i):
    
    try:
        #print(i,j)
        if j in bus_i:
            index_val = bus_i.index(j)
            str = '.' + ip_input_sorted[i] + '(' + master_input_wires[index_val] + ')' + ','
            print(str)
        else:
            pass
    except Exception:
        pass  
#intilialising the output signals
for i,j in enumerate(ip_o):
    
    try:
        #print(i,j)
        if j in bus_o:
            index_val = bus_o.index(j)
            str = '.' + ip_output_sorted[i] + '(' + master_output_wires[index_val] + ')' + ','
            f=""
            #for x in range(size_o): #6 baar chalega
            if i==(size_o-1): 
                f = str.rstrip(',')
                print(f)
            else:
                print(str)
                
                
        else:
            pass
    except Exception:
        pass  

