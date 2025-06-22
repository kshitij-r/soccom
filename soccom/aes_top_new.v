module aes_top(
		 wb_adr_i, wb_cyc_i, wb_dat_i, wb_sel_i,
		 wb_stb_i, wb_we_i,
		 wb_ack_o, wb_err_o, wb_dat_o,
		 wb_clk_i, wb_rst_i, int_o
);

   parameter dw = 32;
   parameter aw = 32;

   input [aw-1:0] wb_adr_i;
   input wb_cyc_i;
   input [dw-1:0] wb_dat_i;
   input [3:0] wb_sel_i;
   input wb_stb_i;
   input wb_we_i;
   
   output wb_ack_o;
   output wb_err_o;
   output reg [dw-1:0] wb_dat_o;
   output int_o;
   
   input wb_clk_i;
   input wb_rst_i;


   assign wb_ack_o = 1'b1;
   assign wb_err_o = 1'b0;
   assign int_o = 1'b0;

   // Internal registers
   reg start;
   reg [31:0] pt [0:3];
   reg [31:0] key [0:5];

  wire [127:0] pt_big = {pt[0], pt[1], pt[2], pt[3]};
  wire [127:0] key_big = {key[0], key[1], key[2], key[3]};
  wire [127:0] ct;
  wire ct_valid;
  
  /////////////////////////////////////////////////////////////////////
  
  wire wb_rst_i;
  
reg ld, kld;
wire ld_w = ld;
wire kld_w = kld;


reg SPCREQ;
reg SPCDIS;
reg Pause;

wire SPCREQ_w = SPCREQ;
wire SPCDIS_w = SPCDIS;
wire Pause_w = Pause;



reg WSI, WRSTN, SelectWIR, ShiftWR, CaptureWR;

wire WSI_w = WSI;
wire WRSTN_w = WRSTN;
wire SelectWIR_w = SelectWIR;
wire ShiftWR_w = ShiftWR;
wire CaptureWR_w = CaptureWR;



reg [31:0] DBus;
reg [1:0] Sel;

wire [31:0] DBus_w = DBus;
wire [1:0] Sel_w = Sel;
  
  
  
  wire DWR;
  wire [31:0] DO, DAD;
  wire [31:0] TP1;
  wire TPE1;
  wire WSO;
  /////////////////////////////////////////////////////////////////////
 

   // Implement MD5 I/O memory map interface
   // Write side
   always @(posedge wb_clk_i) begin
     if(wb_rst_i) begin
       start <= 0;
       pt[0] <= 0;
       pt[1] <= 0;
       pt[2] <= 0;
       pt[3] <= 0;
       key[0] <= 0;
       key[1] <= 0;
       key[2] <= 0;
       key[3] <= 0;
     end
     else if(wb_stb_i & wb_we_i)
       case(wb_adr_i[5:1])
         0: start <= wb_dat_i[0];
         1: pt[3] <= wb_dat_i;
         2: pt[2] <= wb_dat_i;
         3: pt[1] <= wb_dat_i;
         4: pt[0] <= wb_dat_i;
         5: key[3] <= wb_dat_i;
         6: key[2] <= wb_dat_i;
         7: key[1] <= wb_dat_i;
         8: key[0] <= wb_dat_i;
		 9: ld <= wb_dat_i;
		 10: kld <= wb_dat_i;
		 11: SPCREQ <= wb_dat_i;
		 12: SPCDIS <= wb_dat_i;
		 13: Pause <= wb_dat_i;
		 14: WSI <= wb_dat_i;
		 15: WRSTN <= wb_dat_i;
		 16: SelectWIR <= wb_dat_i;
		 17: ShiftWR <= wb_dat_i;
		 18: CaptureWR <= wb_dat_i;
		 19: DBus <= wb_dat_i;
		 20: Sel <= wb_dat_i;
         default: ;
       endcase
   end // always @ (posedge wb_clk_i)

   // Implement MD5 I/O memory map interface
   // Read side
   always @(*) begin
      case(wb_adr_i[5:1])
        0: wb_dat_o = {31'b0, start};
        1: wb_dat_o = pt[3];
        2: wb_dat_o = pt[2];
        3: wb_dat_o = pt[1];
        4: wb_dat_o = pt[0];
        5: wb_dat_o = key[3];
        6: wb_dat_o = key[2];
        7: wb_dat_o = key[1];
        8: wb_dat_o = key[0];
        9: wb_dat_o = {31'b0, ct_valid};
        10: wb_dat_o = ct[127:96];
        11: wb_dat_o = ct[95:64];
        12: wb_dat_o = ct[63:32];
        13: wb_dat_o = ct[31:0];
		14: wb_dat_o = DWR;
		15: wb_dat_o = DO [31:0];
		16: wb_dat_o = DAD [31:0];
		17: wb_dat_o = TP1 [31:0];
		18: wb_dat_o = TPE1;
		19: wb_dat_o = WSO;
		
        default: wb_dat_o = 32'b0;
      endcase
   end // always @ (*)
   
  AEStopwrapper AX(
     .clk(wb_clk_i),
     .text_in(pt_big),
     .key(key_big),
     .mode(start),
     .text_out(ct),
     .done(ct_valid),
	 .WSO(WSO),
	 .DWR(DWR),
	 .DO(DO),
	 .DAD(DAD),
	 .TP1(TP1),
	 .TPE1(TPE1),
	 .SPCREQ(SPCREQ_w),
	 .SPCDIS(SPCDIS_w),
     .Pause(Pause_w),
     .WSI(WSI_w),
     .WRSTN(WRSTN_w),
     .SelectWIR(SelectWIR_w),
     .ShiftWR(ShiftWR_w),
     .CaptureWR(CaptureWR_w),
     .DBus(DBus_w),
     .Sel(Sel_w),
     .ld(ld_w),
     .kld(kld_w), 
     .MRST(wb_rst_i), 
     .MASRST(wb_rst_i),
     .rst(wb_rst_i)
	 
   );
endmodule
