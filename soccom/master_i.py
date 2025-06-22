list_1 = ['wbm_adr_o', 'wbm_cyc_o', 'wbm_dat_o',
          'wbm_sel_o', 'wbm_stb_o', 'wbm_we_o']


m_input_wires =   ['busms_ack_i_flat','busms_rty_i_flat',
                   'busms_err_i_flat','busms_dat_i_flat']

ip = []
master = []

for i in list_1:
    val = i.split('_')
    ip.append(val[1])

for j in m_input_wires:
    value = j.split('_')
    master.append(value[1])
IP = sorted(ip)
MASTER = sorted(master)
print("IP: ",IP)
print('\n')
print("Master :",MASTER)
print('\n')

k=0
for i,j in enumerate(IP):
    try:
        #print(i,j)
        if j in MASTER:
            index_val = MASTER.index(j)
            print(".",list_1[i],"(",m_input_wires[index_val],")")
            k+=1
        else:
            pass
    except Exception:
        pass  