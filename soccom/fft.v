fft_top fft_top_inst
     (
        
        .wb_clk_i(clk),
        .wb_rst_i(rst_sys),
        .wb_dat_i(bussl_dat_i[SLAVE_fft_top]),
        .wb_adr_i(bussl_adr_i[SLAVE_fft_top]),
        .wb_sel_i(bussl_sel_i[SLAVE_fft_top]),
        .wb_we_i (bussl_we_i[SLAVE_fft_top]),
        .wb_cyc_i(bussl_cyc_i[SLAVE_fft_top]),
        .wb_stb_i(bussl_stb_i[SLAVE_fft_top]),
        .wb_dat_o(bussl_dat_o[SLAVE_fft_top]),
        .wb_err_o(bussl_err_o[SLAVE_fft_top]),
        .wb_ack_o(bussl_ack_o[SLAVE_fft_top])
   
      ); 