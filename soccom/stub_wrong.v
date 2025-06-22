

module stub(
           wb_dat_i,wb_clk_i,wb_rst_i,wb_dat_o
       );

parameter dw = 32;
parameter aw = 32;

input [dw-1:0]      wb_dat_i;
output reg [dw-1:0] wb_dat_o;

input wb_clk_i;
input wb_rst_i;

always @(posedge wb_clk_i ) begin

	if(!wb_rst_i) begin

		assign wb_dat_o = wb_dat_i;
	end
end
endmodule
