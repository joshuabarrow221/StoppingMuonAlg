// C++ includes
#include <iostream>
#include <vector>
#include <fstream>
#include <iomanip>
#include <glob.h>
#include <algorithm>
#include <iterator>
#include <numeric>
using namespace std;
struct TriggerPrimitive {
  uint32_t chanel             = {0};
  int64_t  time_start          = {0};
  uint16_t adc_integral        = {0};
  uint16_t adc_peak            = {0};
  int32_t  time_over_threshold = {0};
};

bool compare_channel(const TriggerPrimitive& ch_a, const TriggerPrimitive& ch_b)
{
  // smallest comes first                                                                                  \
                                                                                                            
  return ch_a.chanel < ch_b.chanel ; // and (ch_a.time_start < ch_b.time_start));                        \
                                                                                                            
}

int getIndex(vector<uint16_t> v, uint16_t K){
  auto it = find(v.begin(), v.end(), K);
  if (it != v.end())
    {
      int index = it - v.begin();
      //std::cout << index << std::endl;                                                                       
      return index;
    }
  else {
    //std::cout << "-1" << std::endl;                                                                       
    return -99;
  }
}

void MichelAlgo(){
 
  //dead channels                                                                                                                                              
  int col1, col2;
  std::vector<int> deadch;
  std::vector<int> nodeadch;
  ifstream deadchfile("MCC9_channel_list.txt");

  if (deadchfile.is_open() && !deadchfile.eof()){
    while( deadchfile  >> col1 >> col2 ){
      if (col2 < 2)
        {
          deadch.push_back(0);
        }
      else{
        deadch.push_back(1);
      }
    }
  }


  //this Part to run over all the events 
  TFile *fevt = new TFile("Merged_TriggerPrimitiveOfflineAnalyzer_hist_EXT.root");
  TTree * tree =  (TTree*)fevt->Get("tpm/event_tree");

  // Declaration of leaf types
  vector<int>     *channel;
  vector<int>     *view;
  vector<float>   *max_ADC;
  vector<float>   *max_ADC_tick;
  vector<float>   *integral_sum;
  vector<float>   *tot;
  vector<float>   *first_tick;
  vector<float>   *integral_over_n;

  // List of branches
  TBranch        *b_channel;   //!
  TBranch        *b_view;   //!
  TBranch        *b_max_ADC;   //!
  TBranch        *b_max_ADC_tick;   //!
  TBranch        *b_integral_sum;   //!
  TBranch        *b_tot;   //!
  TBranch        *b_first_tick;   //!
  TBranch        *b_integral_over_n;   //!

  // Set object pointer
  channel = 0;
  view = 0;
  max_ADC = 0;
  max_ADC_tick = 0;
  integral_sum = 0;
  tot = 0;
  first_tick = 0;
  integral_over_n = 0;

  tree->SetMakeClass(1);                                                                    
  tree->SetBranchAddress("channel", &channel, &b_channel);                                  
  tree->SetBranchAddress("view", &view, &b_view);                                           
  tree->SetBranchAddress("max_ADC", &max_ADC, &b_max_ADC);                                  
  tree->SetBranchAddress("max_ADC_tick", &max_ADC_tick, &b_max_ADC_tick);                   
  tree->SetBranchAddress("integral_sum", &integral_sum, &b_integral_sum);                   
  tree->SetBranchAddress("tot", &tot, &b_tot);                                              
  tree->SetBranchAddress("first_tick", &first_tick, &b_first_tick);                         
  tree->SetBranchAddress("integral_over_n", &integral_over_n, &b_integral_over_n); 

  //declare and initialize variables:
  int64_t  time_start;
  int32_t  time_over_threshold;
  uint32_t chanel ;
  uint16_t adc_integral ;
  uint16_t adc_peak;
  int detectorplane;
  uint32_t ch_init = 0;
  int maxadcindex = -99;
  int maxadcind;
  uint16_t maxadc =0;
  uint32_t chnlwid = 0;
  int64_t timewid=0;
  int trigtot = 0;
  int64_t TPvol, TPdensity;
  int time_diff = 30;
  uint16_t braggE = 27500; //  27500 is used in uB based on incoming muon angle vs maxadc                            
  uint32_t chnl_maxadc;
  int64_t time_max, this_time_max, prev_time_max, horiz_tt;
  int64_t temp_t;
  int64_t time_min, this_time_min, prev_time_min, horiz_tb;
  int deadwidthscale = 8;
  float slopecm_scale = 0.04/0.3; //time ticks to cm = 1/25, channels to cm = 0.3                                    
  bool frontfound = false;
  bool hitfound = false;
  int TPcount=0;
  int deadcnt=0;
  int braggcnt=0;
  int chcnt=0;
  int horiz_noise_cnt = 0;
  int horiz_tolerance = 8;
  int tracklen=26;
  float radTodeg=180/3.14;
  int64_t y2,y1,y3,y4;
  uint32_t x2,x1,x3,x4;
  float bky1 =99999;
  float bky2 =99999;
  float bky3 =99999;
  float bky4 =99999;
  float bkpy1,bkpy2,bkpy3,bkpy4;
  float frontangle_top, frontangle_mid, frontangle_bottom, backangle_top, backangle_mid, backangle_bottom;
  float slope, frontslope_top, frontslope_mid, frontslope_bottom, backslope_top, backslope_mid, backslope_bottom;
  uint32_t ColPlStartChnl = 4800; // from uB                                                                        \
                                                                                                                     
  uint32_t ColPlEndChnl = 8255; //from uB                                                                           \
                                                                
  int boxchcnt = 1;
  uint32_t prev_chnl, next_chnl, sf_chnl;
  int64_t prev_tstart, next_tstart, sf_tstart;
  int32_t prev_tot, next_tot, sf_tot;
  int contiguous_tolerance = 16;

  int64_t boxwidtime=1150;
  std::vector<int64_t> timeind_vec;
  uint32_t boxwidch=96; //96;                                                                                                                                                                                                 
  std::vector<uint32_t> chnlind_vec;




  std::vector<TriggerPrimitive> tp_list;
  std::vector<uint16_t> initialvec_adc;
  std::vector<TriggerPrimitive> tp_list_maxadc;
  std::vector<TriggerPrimitive> tp_list_this;
  std::vector<TriggerPrimitive> tp_list_prev;
  std::vector<TriggerPrimitive> tp_list_next;
  std::vector<TriggerPrimitive> tp_list_sf;
  std::vector<TriggerPrimitive> tp_list_sb;
  std::vector<TriggerPrimitive> tmpchnl_vec;
  std::vector<TriggerPrimitive> sublist;
  std::vector<TriggerPrimitive> final_tp_list;
  std::vector<int>  maxadcindex_vec;

  cout << ".......Branch address is set....: \t"  << endl;
  Int_t nevent = tree->GetEntries(); //fChain->GetEntries();
  cout << "no. of event: \t" << nevent << endl;
  for (Int_t evt=0; evt < nevent; evt++) {
    //    for (Int_t evt=12; evt < 14; evt++) {
  tree->GetEntry(evt);
  std::cout << "Entry: " << tree->GetEntry(evt) << std::endl;
  //If running over all the events, then after starting the loop over events, make sure to initialize vars and clear vectors

  tp_list.clear(); 
  timeind_vec.clear();
  chnlind_vec.clear();
  tp_list_maxadc.clear();
  boxchcnt=1;
  initialvec_adc.clear();
  tp_list_this.clear();
  frontfound = false;
  hitfound = false;
  deadcnt=0;
  braggcnt=0;
  slope = 0;
  horiz_noise_cnt = 0;
  frontslope_top = 0;
  backslope_top = 0;
  frontslope_mid = 0;
  backslope_mid = 0;
  frontslope_bottom = 0;
  backslope_bottom = 0;
  horiz_tb = 0;
  horiz_tt = 0;
  trigtot=0;

  //This is required to run the algorithms over a ROOT file with many number of events. So, For each event, we are looping over number of channels to take into account all the TPs from all the channels for a particular event
  
   for (int chh=0; chh<(*channel).size(); chh++){
    if ((*view)[chh] == 2){
    chanel = (*channel)[chh];
    time_start = (*first_tick)[chh];
    time_over_threshold = (*tot)[chh];
    adc_integral = (*integral_sum)[chh];
    adc_peak = (*max_ADC)[chh];

    if (time_start >= 3200 and time_start <= 7800){ 
      tp_list.push_back({chanel, time_start, adc_integral,  adc_peak, time_over_threshold});
     
}

    }
   }
  
   std::cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!E V E N T : " << evt << std::endl;  
   std::cout << "TPList size for event: " << evt << " is : " << tp_list.size() << std::endl;
 
   std::sort (tp_list.begin(), tp_list.end(), compare_channel);  
 
 for (int sorttp=0; sorttp< tp_list.size(); sorttp++){
   initialvec_adc.push_back(tp_list[sorttp].adc_integral);
 }


 //Time slices to divide the collection plane channels                                                              
 for(int timeind=3200; timeind <= 7800; timeind+=boxwidtime){
      timeind_vec.push_back(timeind);                                                                          
    }

    //Channel slices to divide the collection plane channels                                                           
    for(int chnlind=ColPlStartChnl; chnlind<(ColPlEndChnl+boxwidch); chnlind+=boxwidch){
      chnlind_vec.push_back(chnlind);                                                                          
    }
 
    for (int i=0; i<tp_list.size(); ++i){ 
      if ((tp_list[i].chanel > chnlind_vec[boxchcnt]) or (i==tp_list.size()-1)){
	if(tmpchnl_vec.size()==0){
	  while(tp_list[i].chanel > chnlind_vec[boxchcnt]){
	    boxchcnt+=1;
	  }}
	else{
	  for(int time_ind=0; time_ind < timeind_vec.size()-1; time_ind++){
	    sublist.clear();
	    for (int tmpch=0; tmpch < tmpchnl_vec.size(); tmpch++){
	      if ((tmpchnl_vec[tmpch].time_start >= timeind_vec[time_ind]) and (tmpchnl_vec[tmpch].time_start < timeind_vec[time_ind+1])){
		sublist.push_back({tmpchnl_vec[tmpch].chanel, tmpchnl_vec[tmpch].time_start, tmpchnl_vec[tmpch].adc_integral, tmpchnl_vec[tmpch].adc_peak, tmpchnl_vec[tmpch].time_over_threshold});
	      }}
	    maxadc = 0;
	    if(sublist.size()>0){
	      for (int sl=0; sl<sublist.size(); sl++){
		if (sublist[sl].adc_integral> maxadc) {
		  maxadc =  sublist[sl].adc_integral;
		  maxadcind = sl;
		} }
	      if(maxadc > braggE){ 
		tp_list_maxadc.push_back({sublist[maxadcind].chanel, sublist[maxadcind].time_start, sublist[maxadcind].adc_integral, sublist[maxadcind].adc_peak, sublist[maxadcind].time_over_threshold});
		maxadc = 0;
	      }}}
	 
	  tmpchnl_vec.clear();
	  
	}}
  
      if (tp_list[i].chanel > chnlind_vec[boxchcnt]) boxchcnt+=1;
      if (tp_list[i].chanel <= chnlind_vec[boxchcnt] or i==tp_list.size()){

	tmpchnl_vec.push_back({tp_list[i].chanel, tp_list[i].time_start, tp_list[i].adc_integral, tp_list[i].adc_peak, tp_list[i].time_over_threshold});
      }
    
    }
    std::cout << "TPList maxadc size: " << tp_list_maxadc.size() << std::endl;

    //Going forward in channels
    for(int imaxadc=0; imaxadc<tp_list_maxadc.size(); imaxadc++){
      chnl_maxadc = tp_list_maxadc[imaxadc].chanel;
      time_max = tp_list_maxadc[imaxadc].time_start + tp_list_maxadc[imaxadc].time_over_threshold;
      time_min = tp_list_maxadc[imaxadc].time_start;
      tp_list_this.push_back({tp_list_maxadc[imaxadc].chanel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});

      tp_list_prev = tp_list_this;
      tp_list_next = tp_list_this;
      tp_list_sf = tp_list_this;
      tp_list_sb = tp_list_this;

      //Let's initialize again some of the required variables here after starting a loop over maxADC TP
      frontfound = false;
      hitfound = false;
      deadcnt=0;
      braggcnt=0;
      slope = 0;
      horiz_noise_cnt = 0;
      frontslope_top = 0;
      backslope_top = 0;
      frontslope_mid = 0;
      backslope_mid = 0;
      frontslope_bottom = 0;
      backslope_bottom = 0;
      frontangle_top = 0;
      frontangle_mid = 0;
      frontangle_bottom = 0;
      backangle_top=0;
      backangle_mid=0;
      backangle_bottom=0;
      horiz_tb = 0;
      horiz_tt = 0;

      //Get Index of maxADC TP
      maxadcindex =  getIndex(initialvec_adc, tp_list_maxadc[imaxadc].adc_integral);

      for (int icheck=maxadcindex; icheck<tp_list.size(); icheck++){
	if (frontfound == true) break;
	if(tp_list[icheck].chanel >= (chnl_maxadc+2)){
	  chnl_maxadc = tp_list_next[imaxadc].chanel;
	  if (hitfound == false) break;
	  if (deadch[chnl_maxadc+1] ==0 and tp_list[icheck].chanel!=(chnl_maxadc+1)){
	    if (tp_list_prev[imaxadc].chanel == chnl_maxadc){
	      slope = 0;
	    }
	    else if (tp_list_prev[imaxadc].chanel == tp_list_sf[imaxadc].chanel){
	      //Lets put conditions for non-zero denominator if it happens at some point. Most likely, it can be the case where we have TPs from the same channels consecutively with different time start. To avoid C++ exceptions, apply non-zero denominator conditions
	      int den3 = (tp_list_prev[imaxadc].chanel-tp_list_maxadc[imaxadc].chanel);
	      if(den3!=0){
	      slope = float((tp_list_prev[imaxadc].time_start + (tp_list_prev[imaxadc].time_over_threshold)/2 - tp_list_maxadc[imaxadc].time_start - (tp_list_maxadc[imaxadc].time_over_threshold)/2))/ den3 ;
	      } }
	    else {
	      //Here,also for non-zero den condition
	      int den4 = (tp_list_prev[imaxadc].chanel-tp_list_sf[imaxadc].chanel);
	      if(den4!=0){
	      slope = float((tp_list_prev[imaxadc].time_start + (tp_list_prev[imaxadc].time_over_threshold)/2 - tp_list_sf[imaxadc].time_start - (tp_list_sf[imaxadc].time_over_threshold)/2))/ den4;
	      }}
	    deadcnt = 0;
	    while (deadch[chnl_maxadc+1] ==0 and chnl_maxadc+1 < ColPlEndChnl) {
	      chnl_maxadc += 1;
	      deadcnt += 1;
	      std::cout << "Skipping through dead channel: " << chnl_maxadc << "with dead cnt: " << deadcnt << std::endl;
	    }
	    tp_list_prev[imaxadc].time_start = tp_list_prev[imaxadc].time_start + std::floor(float(slope)*float(deadcnt));
	                                         
	  }

	  if (hitfound == true){
	    braggcnt+=1;
	    if (braggcnt==3){
	      tp_list_sf = tp_list_next;
	    }
	    if (braggcnt >= tracklen/2){
	      frontfound = true;
	      //Again, nonzero denom. requirements
	      int denf = (tp_list_next[imaxadc].chanel - tp_list_sf[imaxadc].chanel);
	      if (denf!=0){ 
		frontslope_top = float(tp_list_next[imaxadc].time_start + tp_list_next[imaxadc].time_over_threshold - tp_list_sf[imaxadc].time_start - tp_list_sf[imaxadc].time_over_threshold)/ denf; 

		frontslope_mid = float(tp_list_next[imaxadc].time_start + (tp_list_next[imaxadc].time_over_threshold)/2 -tp_list_sf[imaxadc].time_start - (tp_list_sf[imaxadc].time_over_threshold)/2)/ denf ;

		frontslope_bottom = float(tp_list_next[imaxadc].time_start - tp_list_sf[imaxadc].time_start)/ denf; 

	    }
	    }
	    tp_list_prev = tp_list_next;
	  }
	  hitfound = false;
	  this_time_max = 0;
	  this_time_min = 0;
	  prev_time_max = 0;
	  prev_time_min = 0;
	}

	if(tp_list[icheck].chanel == (chnl_maxadc+1)){
	  this_time_max = tp_list[icheck].time_start + tp_list[icheck].time_over_threshold;
	  this_time_min =  tp_list[icheck].time_start;
	  prev_time_max = tp_list_prev[imaxadc].time_start + tp_list_prev[imaxadc].time_over_threshold;
	  prev_time_min =tp_list_prev[imaxadc].time_start;

	  if ((this_time_min>=prev_time_min and this_time_min<=prev_time_max) or (this_time_max>=prev_time_min and this_time_max<=prev_time_max) or (prev_time_max<=this_time_max and prev_time_min>=this_time_min) ){
	  
	    if (horiz_noise_cnt == 0){
	      horiz_tb = prev_time_min;
	      horiz_tt = prev_time_max;
	    }
	    if (tp_list[icheck].chanel == tp_list_next[imaxadc].chanel) break;
	    hitfound = true;
	    tp_list_next[imaxadc].chanel = tp_list[icheck].chanel;   // Assigning right value (tp_list) to left value (next)                                 
	    tp_list_next[imaxadc].time_start = tp_list[icheck].time_start;
	    tp_list_next[imaxadc].adc_integral = tp_list[icheck].adc_integral;
	    tp_list_next[imaxadc].adc_peak = tp_list[icheck].adc_peak;
	    tp_list_next[imaxadc].time_over_threshold = tp_list[icheck].time_over_threshold;
	    if (abs(this_time_min - horiz_tb) <=1 or abs(this_time_max - horiz_tt) <=1){
	      horiz_noise_cnt+=1;                                                                         
	      if (horiz_noise_cnt>horiz_tolerance) break;
	    }
	    else{
	      horiz_noise_cnt = 0;
	 
	    }

	    if (this_time_max > time_max) time_max = this_time_max;
	    if (this_time_min < time_min) time_min = this_time_min;

	    // std::cout << "Time max: " << this_time_max  << " , Time Min: " << this_time_min << std::endl;
	  }}}

 
      //Bkward going
      chnl_maxadc = tp_list_maxadc[imaxadc].chanel;
      tp_list_prev = tp_list_this;
      tp_list_next = tp_list_this;
      //inittialize some of the required variables here.
      this_time_max =0;
      this_time_min =0;
      prev_time_max = 0;
      prev_time_min =0;
      deadcnt=0;
      slope=0;
      hitfound = false;


      if (frontfound == true){
	// std::cout << "Bkwrd loop FRONT FOUND!!!!!!!!!!!!!!!!!!!!!!!" << std::endl;
	for (int icheckb=maxadcindex; icheckb>=0; icheckb--){
	  if(tp_list[icheckb].chanel <= (chnl_maxadc-2)){
	    chnl_maxadc = tp_list_next[imaxadc].chanel;
	    if (hitfound == false) break;
	    
	    if (deadch[chnl_maxadc-1] ==0 and tp_list[icheckb].chanel!=(chnl_maxadc-1)){
	      if (tp_list_prev[imaxadc].chanel == chnl_maxadc){
		slope = 0;                                                                       
	      }
	      else if (tp_list_prev[imaxadc].chanel == tp_list_sb[imaxadc].chanel){
		//non-zero denomi. conditions
		int den5 = (tp_list_prev[imaxadc].chanel-tp_list_maxadc[imaxadc].chanel);
		if(den5!=0){
		  slope = float(tp_list_prev[imaxadc].time_start + (tp_list_prev[imaxadc].time_over_threshold)/2 - tp_list_maxadc[imaxadc].time_start - (tp_list_maxadc[imaxadc].time_over_threshold)/2) / den5 ;                                                                       
		}}
	      else {
		int den6 = (tp_list_prev[imaxadc].chanel-tp_list_sb[imaxadc].chanel);
		if(den6!=0){
		  slope = (tp_list_prev[imaxadc].time_start + (tp_list_prev[imaxadc].time_over_threshold)/2 - tp_list_sb[imaxadc].time_start - (tp_list_sb[imaxadc].time_over_threshold)/2)/ den6; ;                                                                    
		}}
	      deadcnt = 0;
	      while (deadch[chnl_maxadc-1] ==0 and chnl_maxadc-1 > ColPlStartChnl) {
		chnl_maxadc -= 1;
		deadcnt += 1;
     
	      }
	      tp_list_prev[imaxadc].time_start = tp_list_prev[imaxadc].time_start - std::floor(float(slope)*float(deadcnt));
	    }
	    if (hitfound == true) {
	      //std::cout << "BKward Loop Hit Found!!!!!!!!!!!!!!!!!!!" << std::endl;
	      braggcnt+=1;

	      if (braggcnt == tracklen/2+3){
		tp_list_sb = tp_list_next;
	      }
	      if (braggcnt >= tracklen){
		

		bky1=tp_list_next[imaxadc].time_start;
                bky2=tp_list_next[imaxadc].time_over_threshold;
                bky3=tp_list_sb[imaxadc].time_start;
                bky4=tp_list_sb[imaxadc].time_over_threshold;

		//non zero den conditions:
		float num = float(bky1+bky2-(bky3+bky4));
	       	int den = (tp_list_next[imaxadc].chanel - tp_list_sb[imaxadc].chanel);
		if(den!=0){
		//std::cout << " NUM: " << num << " , " << den << std::endl;
	        backslope_top = (bky1+bky2-(bky3+bky4)) / den; 
                backslope_mid = (bky1+(bky2/2)-(bky3+(bky4/2))) / den; 
	        backslope_bottom = (bky1-bky3) / den; 

	
		frontangle_top = (atan(slopecm_scale*float(frontslope_top)))*radTodeg;
                backangle_top = (atan(slopecm_scale*float(backslope_top)))*radTodeg;
                frontangle_mid = (atan(slopecm_scale*float(frontslope_mid)))*radTodeg;
                backangle_mid = (atan(slopecm_scale*float(backslope_mid)))*radTodeg;
                frontangle_bottom = (atan(slopecm_scale*float(frontslope_bottom)))*radTodeg;
                backangle_bottom = (atan(slopecm_scale*float(backslope_bottom)))*radTodeg;


		if (abs(frontangle_mid-backangle_mid)>30 or abs(frontangle_top-backangle_top)>30 or abs(frontangle_bottom-backangle_bottom)>30){
                  trigtot += 1;
		   std::cout <<" Trigger: " << trigtot << std::endl;
		  final_tp_list.push_back({tp_list_maxadc[imaxadc].chanel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});
		  std::cout <<" Trigger AT (bragg peak found at ): " << tp_list_maxadc[imaxadc].chanel << " , " << tp_list_maxadc[imaxadc].time_start << " , "<< tp_list_maxadc[imaxadc].adc_integral << std::endl;
		}
                else {
                  break;
                }
	      }// end on if den!=0 condition
              }
	      tp_list_prev = tp_list_next;
	    }

	    hitfound =false;
	    this_time_max = 0;
	    this_time_min = 0;
	    prev_time_max = 0;
	    prev_time_min = 0;
	  }

	  //std::cout << "icheckb chnl here : " << tp_list[icheckb].chanel <<", chnl maxadc: " << chnl_maxadc << std::endl;
	  if(tp_list[icheckb].chanel == (chnl_maxadc-1)){
            this_time_max = tp_list[icheckb].time_start + tp_list[icheckb].time_over_threshold;
            this_time_min =  tp_list[icheckb].time_start;
            prev_time_max = tp_list_prev[imaxadc].time_start + tp_list_prev[imaxadc].time_over_threshold;
            prev_time_min =tp_list_prev[imaxadc].time_start;

	    if ((this_time_min>=prev_time_min and this_time_min<=prev_time_max) or (this_time_max>=prev_time_min and this_time_max<=prev_time_max) or (prev_time_max<=this_time_max and prev_time_min>=this_time_min)){
	    

	    if (horiz_noise_cnt == 0){
	      horiz_tb = prev_time_min;
	      horiz_tt = prev_time_max;
	      

	    }


	    if (tp_list[icheckb].chanel == tp_list_next[imaxadc].chanel) break;
	    hitfound = true;
	  

	    tp_list_next[imaxadc].chanel = tp_list[icheckb].chanel;   // Assigning right value (tp_list) to left value (next)
	    tp_list_next[imaxadc].time_start = tp_list[icheckb].time_start;
	    tp_list_next[imaxadc].adc_integral = tp_list[icheckb].adc_integral;
	    tp_list_next[imaxadc].adc_peak = tp_list[icheckb].adc_peak;
	    tp_list_next[imaxadc].time_over_threshold = tp_list[icheckb].time_over_threshold;

	    if (abs(this_time_min - horiz_tb) <=1 or abs(this_time_max - horiz_tt) <=1){
	      horiz_noise_cnt+=1;
	      if (horiz_noise_cnt>horiz_tolerance) break;
	    }
	    else{
	      horiz_noise_cnt = 0;
                                                                  
	    }

	    if (this_time_max > time_max) time_max = this_time_max;
	    if (this_time_min < time_min) time_min = this_time_min;
	    //std::cout <<"bkwrd time min: " << time_min << std::endl;
	    }
	  }//icheckb channel
	  }//end loop icheckb
	} //endloop front found
    }//end over imaxadc loop

    if(trigtot > 0 ){
    std::cout << "Event triggered on :" << evt << std::endl;     
    }
      } //End loop over nevents
 } //End loop over Michel_allevts function
