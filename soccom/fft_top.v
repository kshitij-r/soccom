module fft_top(
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
   reg start, RDY;
   wire RDY_w = RDY;
   wire start_w = start;
   reg [5:0]  ADDR;
   reg [19:0] DOR, DOI;

   
/*   wire start_, ED, SHIFT, RDY;
   wire [5:0]  ADDR;
   wire [19:0] DOR, DOI;*/

 /////////////////////////////////////////////////////////////////////
  
wire wb_rst_i;
  


reg SPCREQ;
reg SPCDIS;
reg Pause;
reg ED;
reg [15:0] DI, DR; 
reg [3:0] SHIFT;

wire SPCREQ_w = SPCREQ;
wire SPCDIS_w = SPCDIS; 
wire Pause_w = Pause;
wire ED_w = ED;
wire [15:0] DI_w = DI;
wire [15:0] DR_w = DR;

wire [19:0] DOI_w = DOI;
wire [19:0] DOR_w = DOR;



reg WSI, WRSTN, SelectWIR, ShiftWR, CaptureWR;

wire WSI_w = WSI;
wire WRSTN_w = WRSTN;
wire SelectWIR_w = SelectWIR;
wire ShiftWR_w = ShiftWR;
wire CaptureWR_w = CaptureWR;
wire [3:0] SHIFT_w = SHIFT;


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
     end
     else if(wb_stb_i & wb_we_i)
       case(wb_adr_i[5:2])
         0: start <= wb_dat_i[0];
		 1: SPCREQ <= wb_dat_i;
		 2: SPCDIS <= wb_dat_i;
		 3: Pause <= wb_dat_i;
		 4: WSI <= wb_dat_i;
		 5: WRSTN <= wb_dat_i;
		 6: SelectWIR <= wb_dat_i;
		 7: ShiftWR <= wb_dat_i;
		 8: CaptureWR <= wb_dat_i;
		 9: DBus <= wb_dat_i;
		 10: Sel <= wb_dat_i;
		 11: ED <= wb_dat_i;
		 12: DI <= wb_dat_i;
		 13: DR <= wb_dat_i;
		 13: SHIFT <= wb_dat_i;
         default: ;
       endcase
   end // always @ (posedge wb_clk_i)

   // Implement MD5 I/O memory map interface
   // Read side
   always @(*) begin
      case(wb_adr_i[5:2])
        0: wb_dat_o = {31'b0, start};
        1: wb_dat_o = DOR [19:0];
        2: wb_dat_o = DOI [19:0];
        3: wb_dat_o = RDY;
		4: wb_dat_o = DWR;
		5: wb_dat_o = DO [31:0];
		6: wb_dat_o = DAD [31:0];
		7: wb_dat_o = TP1 [31:0];
		8: wb_dat_o = TPE1;
		9: wb_dat_o = WSO;
		
        default: wb_dat_o = 32'b0;
      endcase
   end // always @ (*)
   
  FFT128wrapper F0(
     .CLK(wb_clk_i),
	 .RSTT(wb_rst_i),
     .ED(ED_w),
     .START(start_w),
     .SHIFT(SHIFT_w),
     .DR(DR_w),
     .DI(DI_w),
	 .RDY(RDY_w),
	 .DOR(DOR_w),
	 .DOI(DOI_w),
	 .WSO(WSO),
	 .DWR(DWR),
	 .DO(DO),
	 .DAD(DAD),
	 .TP1(TP1),
	 .TPE1(TPE1),
	 .SPCREQ(SPCREQ_w),
	 .SPCDIS(SPCDIS_w),
     .WSI(WSI_w),
     .WRSTN(WRSTN_w),
     .SelectWIR(SelectWIR_w),
     .ShiftWR(ShiftWR_w),
     .CaptureWR(CaptureWR_w),
     .DBus(DBus_w),
     .Sel(Sel_w), 
     .MRST(wb_rst_i)
	 
	 
   );
endmodule
