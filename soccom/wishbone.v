wb_bus_b3
     #(.MASTERS(NR_MASTERS),.SLAVES(NR_SLAVES),
       .S0_ENABLE(1),
       .S0_RANGE_WIDTH(1),.S0_RANGE_MATCH(1'b0)

	  )
   u_bus(
         // Outputs
         .m_dat_o                       (busms_dat_i_flat),      
         .m_ack_o                       (busms_ack_i_flat),      
         .m_err_o                       (busms_err_i_flat),      
         .m_rty_o                       (busms_rty_i_flat),      
         .s_adr_o                       (bussl_adr_i_flat),      
         .s_dat_o                       (bussl_dat_i_flat),      
         .s_cyc_o                       (bussl_cyc_i_flat),      
         .s_stb_o                       (bussl_stb_i_flat),      
         .s_sel_o                       (bussl_sel_i_flat),      
         .s_we_o                        (bussl_we_i_flat),       
         .s_cti_o                       (bussl_cti_i_flat),      
         .s_bte_o                       (bussl_bte_i_flat),      
         .snoop_adr_o                   (snoop_adr),             
         .snoop_en_o                    (snoop_enable),          
         .bus_hold_ack                  (),                      
         // Inputs
         .clk_i                         (clk),                   
         .rst_i                         (rst_sys),               
         .m_adr_i                       (busms_adr_o_flat),      
         .m_dat_i                       (busms_dat_o_flat),      
         .m_cyc_i                       (busms_cyc_o_flat),      
         .m_stb_i                       (busms_stb_o_flat),      
         .m_sel_i                       (busms_sel_o_flat),      
         .m_we_i                        (busms_we_o_flat),       
         .m_cti_i                       (busms_cti_o_flat),      
         .m_bte_i                       (busms_bte_o_flat),      
         .s_dat_i                       (bussl_dat_o_flat),      
         .s_ack_i                       (bussl_ack_o_flat),      
         .s_err_i                       (bussl_err_o_flat),      
         .s_rty_i                       (bussl_rty_o_flat),      
         .bus_hold                      (1'b0)
		 );                         