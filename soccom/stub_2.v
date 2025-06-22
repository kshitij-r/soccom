module stub(
	input [31:0] wb_dat_i,
    input wb_clk_i,
    input wb_rst_i,
	output reg [31:0] wb_dat_o
	);
//reg [31:0] out ;

always @(posedge wb_clk_i ) begin

	if(!wb_rst_i) begin

		assign wb_dat_o = wb_dat_i;
	end
end



