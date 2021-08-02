//This code has been translated from python (written for uB, by H. Seigel) to C++ (intended to use for DUNE DS, translated by D. Kalra with slight modifications).

#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <limits>
#include <cstddef>
#include <stdint.h>
#include <algorithm>
#include <bits/stdc++.h>


using namespace std;

struct TriggerPrimitive {
  uint32_t channel             = {0};
  int64_t  time_start          = {0};
  uint16_t adc_integral        = {0};
  uint16_t adc_peak            = {0};
  int32_t  time_over_threshold = {0};
};

bool compare_channel(const TriggerPrimitive& ch_a, const TriggerPrimitive& ch_b)
{
  // smallest comes first                                                                                                      
  return ch_a.channel < ch_b.channel ; // and (ch_a.time_start < ch_b.time_start));                                           
}

bool compare_tstart(const TriggerPrimitive& ts_a, const TriggerPrimitive& ts_b)
{
  // smallest comes first                                                                                                     
  if(ts_a.channel == ts_b.channel){
    return ts_a.time_start < ts_b.time_start ;
  }
  else{
    return ts_a.channel < ts_b.channel ;
  }
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


int main(){

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

  ifstream myfile;
  myfile.open("listfilefilter.txt");
  if (!myfile.is_open()) {
  std::cout << "Error opening file";
   }

  uint32_t ch_init = 0;
  int maxadcindex;
  int maxadcind;
  uint16_t maxadc =0;
  uint32_t chnlwid = 0;
  int64_t timewid=0;
  int trigtot;
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
  float bky1,bky2,bky3,bky4, bkpy1,bkpy2,bkpy3,bkpy4;
  float frontangle_top, frontangle_mid, frontangle_bottom, backangle_top, backangle_mid, backangle_bottom;
  float slope, frontslope_top, frontslope_mid, frontslope_bottom, backslope_top, backslope_mid, backslope_bottom;
  uint32_t ColPlStartChnl = 4800; // from uB                                                                                      
  uint32_t ColPlEndChnl = 8255; //from uB                                                                                         
  int boxchcnt = 1;
  uint32_t prev_chnl, next_chnl, sf_chnl;
  int64_t prev_tstart, next_tstart, sf_tstart;
  int32_t prev_tot, next_tot, sf_tot;
  int contiguous_tolerance = 16;

  int64_t boxwidtime=1150;
  std::vector<int64_t> timeind_vec;
  uint32_t boxwidch=96; //96;                                                                                                    
  std::vector<uint32_t> chnlind_vec;

  std::vector<TriggerPrimitive> tp_list;//,5000,5000,5000,5000];
  std::vector<TriggerPrimitive> tp_only;
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
  std::vector<uint16_t> initialvec_adc;
  //  std::vector<TriggerPrimitive> test;

  int64_t  time_start;
  int32_t  time_over_threshold;
  int64_t  time_peak;
  uint32_t channel ;
  uint16_t adc_integral ;
  uint16_t adc_integralN ;
  uint16_t adc_peak;
  uint32_t detid;
  uint32_t type  ;
  

    string line;
    while (getline(myfile, line))
      {
	std::istringstream ss(line);
	while (ss >> channel >> time_start >> adc_integral >> adc_peak >> time_over_threshold)
	    tp_list.push_back({channel, time_start, adc_integral,  adc_peak, time_over_threshold}); 
	initialvec_adc.push_back(adc_integral);
      }
 
  myfile.close();
  
  std::cout<< "Initial TPList size: " << tp_list.size() << std::endl;
  std::sort (tp_list.begin(), tp_list.end(), compare_channel);
  
  //Time slices to divide the collection plane channels
  for(int timeind=3200; timeind <= 7800; timeind+=boxwidtime){
    timeind_vec.push_back(timeind);                                                                                              
  } 
 
  //Channel slices to divide the collection plane channels  
for(int chnlind=ColPlStartChnl; chnlind<(ColPlEndChnl+boxwidch); chnlind+=boxwidch){ 
  chnlind_vec.push_back(chnlind);                                                                                                
 }  
  

 for (int i=0; i<tp_list.size(); ++i){  
   if ((tp_list[i].channel > chnlind_vec[boxchcnt]) or (i==tp_list.size()-1)){
     if(tmpchnl_vec.size()==0){
       while(tp_list[i].channel > chnlind_vec[boxchcnt]){
	 boxchcnt+=1;
       }
     }
     else{       
       for(int time_ind=0; time_ind < timeind_vec.size()-1; time_ind++){
	 sublist.clear(); //={};
	 for (int tmpch=0; tmpch < tmpchnl_vec.size(); tmpch++){
	  
	   if ((tmpchnl_vec[tmpch].time_start >= timeind_vec[time_ind]) and (tmpchnl_vec[tmpch].time_start < timeind_vec[time_ind+1])){
	    
	     sublist.push_back({tmpchnl_vec[tmpch].channel, tmpchnl_vec[tmpch].time_start, tmpchnl_vec[tmpch].adc_integral, tmpchnl_vec[tmpch].adc_peak, tmpchnl_vec[tmpch].time_over_threshold});
	     
	   }} //closed tm[chnl vec block
	 maxadc = 0;
	 if(sublist.size()>0){ //C. now  or i==tp_list.size()){
	   for (int sl=0; sl<sublist.size(); sl++){                            
      	     std::cout << "adc intg in sublist is : " << sublist[sl].adc_integral << std::endl;
	     if (sublist[sl].adc_integral> maxadc) {
	     maxadc =  sublist[sl].adc_integral;
	     maxadcind = sl;
	     } }                                     
	     std::cout << "check on maxadc :" << maxadc  << " with index: " << maxadcind << std::endl;
	     if(maxadc > braggE){
	      
	       tp_list_maxadc.push_back({sublist[maxadcind].channel, sublist[maxadcind].time_start, sublist[maxadcind].adc_integral, sublist[maxadcind].adc_peak, sublist[maxadcind].time_over_threshold});
	     
	       maxadc = 0;
	
	     
  }}
       }
       tmpchnl_vec.clear();
     }

   }
    
   if (tp_list[i].channel > chnlind_vec[boxchcnt]) boxchcnt+=1;
   if (tp_list[i].channel <= chnlind_vec[boxchcnt] or i==tp_list.size()){
         
 tmpchnl_vec.push_back({tp_list[i].channel, tp_list[i].time_start, tp_list[i].adc_integral, tp_list[i].adc_peak, tp_list[i].time_over_threshold});

   }

 } // end for loop on tp size 


 for (int tpt=0; tpt<tp_list_maxadc.size(); tpt++){

   maxadcindex =  getIndex(initialvec_adc, tp_list_maxadc[tpt].adc_integral);
   maxadcindex_vec.push_back(maxadcindex);
  
 }


 for(int imaxadc=0; imaxadc<tp_list_maxadc.size(); imaxadc++){
  
    chnl_maxadc = tp_list_maxadc[imaxadc].channel;
    time_max = tp_list_maxadc[imaxadc].time_start + tp_list_maxadc[imaxadc].time_over_threshold;
    time_min = tp_list_maxadc[imaxadc].time_start;
 
    //tp_list_this: saves the TPs for the current channel in loop
    tp_list_this.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});

    tp_list_prev = tp_list_this;
    tp_list_next = tp_list_this;
    tp_list_sf = tp_list_this;
    tp_list_sb = tp_list_this;  

    frontfound = false;
    hitfound = false;

 
    maxadcindex =  getIndex(initialvec_adc, tp_list_maxadc[imaxadc].adc_integral);

  //Loop starts from channel with maxadc to look through all the TPs in forward channels
    for (int icheck=maxadcindex; icheck<tp_list.size(); icheck++){   
  if (frontfound == true) break;
      if(tp_list[icheck].channel >= (chnl_maxadc+2)){

	chnl_maxadc = tp_list_next[imaxadc].channel;
	if (hitfound == false) break; 
	if (deadch[chnl_maxadc+1] ==0 and tp_list[icheck].channel!=(chnl_maxadc+1)){
	  if (tp_list_prev[imaxadc].channel == chnl_maxadc){  
	  slope = 0;
	  }
	 
	  else if (tp_list_prev[imaxadc].channel == tp_list_sf[imaxadc].channel){
	    slope = (tp_list_prev[imaxadc].time_start + (tp_list_prev[imaxadc].time_over_threshold)/2 - tp_list_maxadc[imaxadc].time_start - (tp_list_maxadc[imaxadc].time_over_threshold)/2)/ (tp_list_prev[imaxadc].channel-tp_list_maxadc[imaxadc].channel);
	    
	  }
	  else {
	    slope = (tp_list_prev[imaxadc].time_start + (tp_list_prev[imaxadc].time_over_threshold)/2 - tp_list_sf[imaxadc].time_start - (tp_list_sf[imaxadc].time_over_threshold)/2)/(tp_list_prev[imaxadc].channel-tp_list_sf[imaxadc].channel);
	  }
	  deadcnt = 0;
	  while (deadch[chnl_maxadc+1] ==0 and chnl_maxadc+1 < ColPlEndChnl) {
	    chnl_maxadc += 1;
	    deadcnt += 1;
	    std::cout << "Skipping through dead channel: "  << std::endl; 
	  }

	  tp_list_prev[imaxadc].time_start = tp_list_prev[imaxadc].time_start + std::floor(float(slope)*float(deadcnt));

	}
     
	if (hitfound == true){
	  braggcnt+=1;
	  if (braggcnt==3){
	      
	    tp_list_sf = tp_list_next; 
	  }
	  //that is 13 channels away from the channel with braggcnt=3 thats is 3 channels away from maxadc channel
	  if (braggcnt >= tracklen/2){
	    frontfound = true;

	    frontslope_top = (tp_list_next[imaxadc].time_start + tp_list_next[imaxadc].time_over_threshold - tp_list_sf[imaxadc].time_start - tp_list_sf[imaxadc].time_over_threshold)/(tp_list_next[imaxadc].channel - tp_list_sf[imaxadc].channel);

	    frontslope_mid = (tp_list_next[imaxadc].time_start + (tp_list_next[imaxadc].time_over_threshold)/2 -tp_list_sf[imaxadc].time_start - (tp_list_sf[imaxadc].time_over_threshold)/2)/(tp_list_next[imaxadc].channel - tp_list_sf[imaxadc].channel);

	    frontslope_bottom = (tp_list_next[imaxadc].time_start - tp_list_sf[imaxadc].time_start)/(tp_list_next[imaxadc].channel - tp_list_sf[imaxadc].channel);

	  }
	  tp_list_prev = tp_list_next;
	}
      

      hitfound = false;
      this_time_max = 0;
      this_time_min = 0;
      prev_time_max = 0;
      prev_time_min = 0;
     
      } //closed icheck chnl > chnlmaxadc loop channel loop

    
      //If current hit (icheck loop) is in channel next to channel with max adc
	if(tp_list[icheck].channel == (chnl_maxadc+1)){
	
	this_time_max = tp_list[icheck].time_start + tp_list[icheck].time_over_threshold;
	this_time_min =  tp_list[icheck].time_start;
	prev_time_max = tp_list_prev[imaxadc].time_start + tp_list_prev[imaxadc].time_over_threshold;
	prev_time_min =tp_list_prev[imaxadc].time_start;
	
	if ((this_time_min>=prev_time_min and this_time_min<=prev_time_max) or (this_time_max>=prev_time_min and this_time_max<=prev_time_max) or (prev_time_max<=this_time_max and prev_time_min>=this_time_min) ){

	  if (horiz_noise_cnt == 0){
	    horiz_tb = prev_time_min;
	    horiz_tt = prev_time_max;
	  

	  }
	
        if (tp_list[icheck].channel == tp_list_next[imaxadc].channel) break;
	hitfound = true;
	std::cout << "Hit Found in channel: " << tp_list[icheck].channel << std::endl;

	tp_list_next[imaxadc].channel = tp_list[icheck].channel;   // Assigning right value (tp_list) to left value (next)
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
	
}

     }
    }
 
  //Look backwards now 

    chnl_maxadc = tp_list_maxadc[imaxadc].channel;
    tp_list_prev = tp_list_this;
    tp_list_next = tp_list_this;
    this_time_max =0;
    this_time_min =0;
    prev_time_max = 0;
    prev_time_min =0;
    deadcnt=0;
    slope=0;
    hitfound = false;
    
   if (frontfound == true){
     std::cout << "FRONT FOUND!!!!!!!!!!!!!!!!!!!!!!!" << std::endl;
      for (int icheckb=maxadcindex; icheckb>=0; icheckb--){ 
	if(tp_list[icheckb].channel <= (chnl_maxadc-2)){

	  chnl_maxadc = tp_list_next[imaxadc].channel; 
	  if (hitfound == false) break;

	  if (deadch[chnl_maxadc-1] ==0 and tp_list[icheckb].channel!=(chnl_maxadc-1)){
	    if (tp_list_prev[imaxadc].channel == chnl_maxadc){
	      slope = 0;
	    }
	    else if (tp_list_prev[imaxadc].channel == tp_list_sb[imaxadc].channel){
	      slope = (tp_list_prev[imaxadc].time_start + (tp_list_prev[imaxadc].time_over_threshold)/2 - tp_list_maxadc[imaxadc].time_start - (tp_list_maxadc[imaxadc].time_over_threshold)/2)/ (tp_list_prev[imaxadc].channel-tp_list_maxadc[imaxadc].channel);
	    }
	    else {
	      slope = (tp_list_prev[imaxadc].time_start + (tp_list_prev[imaxadc].time_over_threshold)/2 - tp_list_sb[imaxadc].time_start - (tp_list_sb[imaxadc].time_over_threshold)/2)/(tp_list_prev[imaxadc].channel-tp_list_sb[imaxadc].channel);
	    }
	    deadcnt = 0;
	    while (deadch[chnl_maxadc-1] ==0 and chnl_maxadc-1 > ColPlStartChnl) {
	      chnl_maxadc -= 1;
	      deadcnt += 1;
	    
	    }
	    tp_list_prev[imaxadc].time_start = tp_list_prev[imaxadc].time_start - std::floor(float(slope)*float(deadcnt));
	   
	  }//end dead channel loop

	  if (hitfound == true) {
	    braggcnt+=1;
	    if (braggcnt == tracklen/2+3){
	      tp_list_sb = tp_list_next;

}
	      if (braggcnt >= tracklen){
	
		bky1=tp_list_next[imaxadc].time_start;
		bky2=tp_list_next[imaxadc].time_over_threshold;
		bky3=tp_list_sb[imaxadc].time_start;
		bky4=tp_list_sb[imaxadc].time_over_threshold;
		backslope_top = float(bky1+bky2-bky3-bky4)/float(tp_list_next[imaxadc].channel-tp_list_sb[imaxadc].channel);
		backslope_mid = float(bky1+bky2/2-bky3-bky4/2)/float(tp_list_next[imaxadc].channel-tp_list_sb[imaxadc].channel);
		backslope_bottom = float(bky1-bky3)/float(tp_list_next[imaxadc].channel-tp_list_sb[imaxadc].channel);


		frontangle_top = (atan(slopecm_scale*float(frontslope_top)))*radTodeg;
		backangle_top = (atan(slopecm_scale*float(backslope_top)))*radTodeg;
		frontangle_mid = (atan(slopecm_scale*float(frontslope_mid)))*radTodeg;
		backangle_mid = (atan(slopecm_scale*float(backslope_mid)))*radTodeg;
		frontangle_bottom = (atan(slopecm_scale*float(frontslope_bottom)))*radTodeg;
		backangle_bottom = (atan(slopecm_scale*float(backslope_bottom)))*radTodeg;
	
		if (abs(frontangle_mid-backangle_mid)>2 or abs(frontangle_top-backangle_top)>2 or abs(frontangle_bottom-backangle_bottom)>2){
		  trigtot += 1;
		  std::cout <<" Trigger: " << trigtot << std::endl;	
	  final_tp_list.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});
	  std::cout <<" Trigger AT (bragg peak found at ): " << tp_list_maxadc[imaxadc].channel << " , " << tp_list_maxadc[imaxadc].time_start << " , "  << tp_list_maxadc[imaxadc].adc_integral << std::endl;
		
		}
		else {
		  break;
		}
	      }
	    
		tp_list_prev = tp_list_next;

	  }
	
	  hitfound ==false;
	  this_time_max = 0;
	  this_time_min = 0;
	  prev_time_max = 0;
	  prev_time_min = 0;
	}	

	  if(tp_list[icheckb].channel == (chnl_maxadc-1)){
	    this_time_max = tp_list[icheckb].time_start + tp_list[icheckb].time_over_threshold;
	    this_time_min =  tp_list[icheckb].time_start;
	    prev_time_max = tp_list_prev[imaxadc].time_start + tp_list_prev[imaxadc].time_over_threshold;
	    prev_time_min =tp_list_prev[imaxadc].time_start;

	    if ((this_time_min>=prev_time_min and this_time_min<=prev_time_max) or (this_time_max>=prev_time_min and this_time_max<=prev_time_max) or (prev_time_max<=this_time_max and prev_time_min>=this_time_min)){
	     
	      if (horiz_noise_cnt == 0){
		horiz_tb = prev_time_min;
		horiz_tt = prev_time_max;

	      }
	    

   if (tp_list[icheckb].channel == tp_list_next[imaxadc].channel) break;
   hitfound == true;
 
   tp_list_next[imaxadc].channel = tp_list[icheckb].channel;     
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
	    }
	  }
      } //endloop over icheck b
     }///end ober frontfound true condition
 }// end over imaxadc loop

  return trigtot;

}
