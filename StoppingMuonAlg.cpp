//This code has been translated from python (written for uB, by H. Seigel) to C++ (intended to use for DUNE DS, translated by D. Kalra with slight modifications). Currently, doesn't account for dead channels and also uses TPs from uB raw data which is zero suppressed. Surely, needs some modifications especially in block where detector/collection plane channels are sliced.

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

int main(){

  //ifstream myfile("tps.txt");                                                                                                  
  ifstream myfile("test.txt");
  if (!myfile.is_open()) {
    std::cout << "Error opening file";
  }

  uint32_t ch_init = 0;
  int maxadcindex;
  uint16_t maxadc =0;
  uint32_t chnlwid = 0;
  int64_t timewid=0;
  int trigtot;
  int64_t TPvol, TPdensity;
  int time_diff = 30;
  uint16_t braggE = 27500; //  27500 is used in uB based on incoming muon angle vs maxadc                   
  uint32_t chnl_maxadc;
  int64_t time_max, this_time_max, prev_time_max;
  int64_t temp_t;
  int64_t time_min, this_time_min, prev_time_min;
  int deadwidthscale = 8;
  float slopecm_scale = 0.04/0.3; //time ticks to cm = 1/25, channels to cm = 0.3                            
  bool frontfound = false;
  bool hitfound = false;
  int TPcount=0;
  int DEADcount=0;
  int braggcnt=0;
  int chcnt=0;
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
  uint32_t boxwidch=250; //96;                                                                                                    
  std::vector<uint32_t> chnlind_vec;

  std::vector<TriggerPrimitive> tp_list;
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

  int64_t  time_start;
  int32_t  time_over_threshold;
  int64_t  time_peak;
  uint32_t channel ;
  uint16_t adc_integral ;
  uint16_t adc_integralN ;
  uint16_t adc_peak;
  uint32_t detid;
  uint32_t type  ;


  while (myfile >> channel >> time_start >> adc_integral >> adc_peak >> time_over_threshold)
    {
      //tp_list.push_back({time_start, time_over_threshold, time_peak, channel, adc_integral, adc_peak, detid, type});             
      tp_list.push_back({channel, time_start, adc_integral,  adc_peak, time_over_threshold});
    }
  std::cout<< "Initial TPList size: " << tp_list.size() << std::endl;
  std::sort (tp_list.begin(), tp_list.end(), compare_channel);
  std::sort (tp_list.begin(), tp_list.end(), compare_tstart);


  for (int i=0; i<tp_list.size(); ++i){
    std::cout << "Initital Sorted TPList contents, Channel" << tp_list[i].channel << ", tstart" << tp_list[i].time_start  << "TPs(ToT,ADCIntg, ADC)"<< tp_list[i].time_over_threshold << " , " << tp_list[i].adc_integral << " , " << tp_list[i].adc_peak <<std::endl;
  }
  //Time slices to divide the collection plane channels
  for(int timeind=3200; timeind <= 7800; timeind+=boxwidtime){
    timeind_vec.push_back(timeind);                                                                                              
  } 
  for(int i=0;i< timeind_vec.size();i++){                                                                                          
    std::cout<< "timeind vector: "<< timeind_vec[i] << std::endl;                                                                   
  } 
  //Channel slices to divide the collection plane channels  
for(int chnlind=ColPlStartChnl; chnlind<(ColPlEndChnl+boxwidch); chnlind+=boxwidch){ 
  chnlind_vec.push_back(chnlind);                                                                                                
 }  

 for(int i=0;i< chnlind_vec.size();i++){                                                                             
                                                                                                                           
   std::cout<< "Chnlind vector: "<< chnlind_vec[i] << std::endl;                                                     
                                                                                                                           
 }  

 for (int i=0; i<tp_list.size(); ++i){  
   if (tp_list[i].channel > chnlind_vec[boxchcnt] or i==tp_list.size()){
     if (tmpchnl_vec.size() == 0){
       while(tp_list[i].channel > chnlind_vec[boxchcnt]){
	 boxchcnt+=1;
       }
     }

     else{
       //sublist vector saves the TPs in each subregions (should do that) [This part might need modification]
       for(int time_ind=0; time_ind < timeind_vec.size(); time_ind++){ 
	 sublist.clear(); //={};
	 for (int tmpch=0; tmpch < tmpchnl_vec.size(); tmpch++){  
	   if(tp_list[tmpch].time_start >= timeind_vec[time_ind] and tp_list[tmpch].time_start < timeind_vec[time_ind+1]){
	     sublist.push_back({tp_list[tmpch].channel, tp_list[tmpch].time_start, tp_list[tmpch].adc_integral, tp_list[tmpch].adc_peak, tp_list[tmpch].time_over_threshold});
	   }}
	 if(sublist.size()>0){
	   for (int sl=0; sl<sublist.size(); sl++){ 
	     maxadc =  sublist[sl].adc_integral;
	     maxadcindex = sl;
	   }
	   std::cout << "Maxadc, index" << maxadc << " , " << maxadcindex << std::endl;
	   //tp_list_maxadc should save the TPs with maxadc > bragg E in each subregion 
	   if (maxadc > braggE){
	     tp_list_maxadc.push_back({sublist[maxadcindex].channel, sublist[maxadcindex].time_start, sublist[maxadcindex].adc_integral, sublist[maxadcindex].adc_peak, sublist[maxadcindex].time_over_threshold});
	   }
	 }
       }
       tmpchnl_vec.clear();
     }
   }

   if (tp_list[i].channel <= chnlind_vec[boxchcnt]){
     tmpchnl_vec.push_back({tp_list[i].channel, tp_list[i].time_start, tp_list[i].adc_integral, tp_list[i].adc_peak, tp_list[i].time_over_threshold});
   }
 }

 //std::cout << "Size of tp_list_maxadc: " << tp_list_maxadc.size() << std::endl;

 for (int tpt=0; tpt<tp_list_maxadc.size(); tpt++){

   std::cout << "channel: " << tp_list[tpt].channel << " tstart: " << tp_list[tpt].time_start << "  ADCIntgl, ADCPeak, Tot" << tp_list[tpt].adc_integral <<" , " << tp_list[tpt].adc_peak << " , " << tp_list[tpt].time_over_threshold << std::endl;

 }


  /*
//In case, we don't want to divide detector region then its straightforward to calculate maxadc
  for (int i=0; i<tp_list.size(); ++i){
    if (tp_list[i].adc_integral > maxadc){
      maxadc =  tp_list[i].adc_integral;
      maxadcindex = i;
    }
  }
  std::cout << maxadc << " , " << maxadcindex << std::endl;

  if (maxadc > braggE){
    for (int i=0; i<tp_list.size(); ++i){
      if (tp_list[i].adc_integral == maxadc){
	tp_list_maxadc.push_back({tp_list[maxadcindex].channel, tp_list[maxadcindex].time_start, tp_list[maxadcindex].adc_integral, tp_list[maxadcindex].adc_peak, tp_list[maxadcindex].time_over_threshold});
      }
    }
  }
  for (int i=0; i<tp_list_maxadc.size(); ++i){
    std::cout << "TP MaxADC, Channel" << tp_list_maxadc[i].channel << ", tstart" << tp_list_maxadc[i].time_start << "TPs (ToT,ADCIntg, ADC)"<< tp_list_maxadc[i].time_over_threshold << " , " << tp_list_maxadc[i].adc_integral << " , " << tp_list_maxadc[i].adc_peak <<std::endl;
  }
  */

  //Look for TPs in forward channels starting from TP with maxADC 

  for (int imaxadc=0; imaxadc<tp_list_maxadc.size(); imaxadc++){
    hitfound = false;
    chnl_maxadc = tp_list_maxadc[imaxadc].channel;
    std::cout << "ChnlMaxADC: " << chnl_maxadc << std::endl;
    time_max = tp_list_maxadc[imaxadc].time_start + tp_list_maxadc[imaxadc].time_over_threshold;
    time_min = tp_list_maxadc[imaxadc].time_start;

    //tp_list_this: saves the TPs for the current channel in loop
    tp_list_this.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});

    //tp_list_prev: saves the TPs for the previous channel w.r.t current channel in loop
    tp_list_prev.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});

    //tp_list_next: saves the TPs for the next channel w.r.t current channel in loop 
    tp_list_next.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});

    //tp_list_sf: save the TPs while calculating forward slope (should update the values)
    tp_list_sf.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});

    //tp_list_sb: save the TPs while calculating backward slope (should update the values)   
    tp_list_sb.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start,tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});

    for (int thisindex=0; thisindex<tp_list_this.size(); thisindex++){
      std::cout << "This TPList contents, Channel" << tp_list_this[thisindex].channel << ", tstart" << tp_list_this[thisindex].time_start << "TPs(ToT,ADCIntg, ADC)"<< tp_list_this[thisindex].time_over_threshold << " , " << tp_list_this[thisindex].adc_integral << " , " <<tp_list_this[thisindex].adc_peak <<std::endl;
    }
    //Loop starts from channel with maxadc to look through all the TPs in forward channels
    for (int icheck=maxadcindex; icheck<tp_list.size(); icheck++){
      if (frontfound == true) break;

      std::cout << tp_list_next[icheck].channel << std::endl;
      std::cout << "ChnlMaxADC: " << chnl_maxadc << std::endl;
      //If current hit (icheck loop) is in channel two channels away either from channel with max adc or channel next to maxadc channel based on if we find hit in next channel (right next to chnl with max adc)   
      if(tp_list[icheck].channel >= (chnl_maxadc+2)){
	chnl_maxadc = tp_list_next[icheck].channel;
	std::cout << "ChnlMaxADC: " << chnl_maxadc << std::endl;
	
	std::cout << "chnlmaxadc: " << chnl_maxadc << "next chnl: " << tp_list_next[icheck].channel << "prev chnl: " << tp_list_prev[icheck].channel << "sf channel: " << tp_list_sf[icheck].channel;
	
	if (hitfound == false) break;
	if (hitfound == true){
	  braggcnt+=1;
	  std::cout << "BraggCount: " << braggcnt << std::endl;
	  //that is 3 channels away from the channel with maxadc
	  if (braggcnt==3){
	    tp_list_sf = tp_list_next;
	    std::cout << "bragcnt=3 contents(sb, next): " << tp_list_sf[0].channel << " , " << tp_list_next[0].channel << std::endl;
	  }
	  //that is 13 channels away from the channel with braggcnt=3 thats is 3 channels away from maxadc channel
	  if (braggcnt >= tracklen/2){
	    frontfound = true;
	    std::cout << "next tmin, tmax" << tp_list_next[icheck].time_start << " , " << (tp_list_next[icheck].time_start + tp_list_next[icheck].time_over_threshold) <<  "sf tmin, tmax"<< tp_list_sf[icheck].time_start <<  " , " << (tp_list_sf[icheck].time_start + tp_list_sf[icheck].time_over_threshold) <<  std::endl;

	    frontslope_top = (tp_list_next[icheck].time_start + tp_list_next[icheck].time_over_threshold - tp_list_sf[icheck].time_start - tp_list_sf[icheck].time_over_threshold)/(tp_list_next[icheck].channel - tp_list_sf[icheck].channel);

	    frontslope_mid = (tp_list_next[icheck].time_start + (tp_list_next[icheck].time_over_threshold)/2 -tp_list_sf[icheck].time_start - (tp_list_sf[icheck].time_over_threshold)/2)/(tp_list_next[icheck].channel - tp_list_sf[icheck].channel);

	    frontslope_bottom = (tp_list_next[icheck].time_start - tp_list_sf[icheck].time_start)/(tp_list_next[icheck].channel - tp_list_sf[icheck].channel);

	    std::cout << "front slope top, mid, bottom " << frontslope_top << " , " << frontslope_mid << " , " << frontslope_bottom << std::endl;

	  }
	  tp_list_prev = tp_list_next;
	}
      }

      hitfound = false;
      this_time_max = 0;
      this_time_min = 0;
      prev_time_max = 0;
      prev_time_min = 0;
      //If current hit (icheck loop) is in channel next to channel with max adc
      if(tp_list[icheck].channel = (chnl_maxadc+1)){
	this_time_max = tp_list[icheck].time_start + tp_list[icheck].time_over_threshold;
	this_time_min =  tp_list[icheck].time_start;
	prev_time_max = tp_list_prev[icheck].time_start + tp_list_prev[icheck].time_over_threshold;
	prev_time_min =tp_list_prev[icheck].time_start;
        if (tp_list[icheck].channel == tp_list_next[icheck].channel) break;

	//Need to re-visit the time condition
	if (abs(prev_time_min-this_time_min)<=time_diff or abs(prev_time_max-this_time_max)<=time_diff){
	  hitfound = true;
	  time_diff = abs(prev_time_min-this_time_min);
	  tp_list_next = tp_list;
	  if (this_time_max > time_max) time_max = this_time_max;
	  if (this_time_min < time_min) time_min = this_time_min;
	}
      }
    }
 

  //Look backwards now 

    chnl_maxadc = tp_list_maxadc[imaxadc].channel;
    tp_list_prev.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});
    tp_list_next.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});
    this_time_max =0;
    this_time_min =0;
    prev_time_max = 0;
    prev_time_min =0;
    slope=0;
    hitfound = false;
    
    if (frontfound == true){
      for (int icheckb=maxadcindex; icheckb>=0; --icheckb){
	if(tp_list[icheckb].channel <= (chnl_maxadc+2)){

	  chnl_maxadc = tp_list_next[icheckb].channel;
	  if (hitfound == false) break;

	  if (hitfound == true) {
	    braggcnt+=1;
	    if (braggcnt == 3){
	      tp_list_sb = tp_list_next;
	    }
	      if (braggcnt >= tracklen){

		bky1=tp_list_next[icheckb].time_start;
		bky2=tp_list_next[icheckb].time_over_threshold;
		bky3=tp_list_sb[icheckb].time_start;
		bky4=tp_list_sb[icheckb].time_over_threshold;
		backslope_top = float(bky1+bky2-bky3-bky4)/float(tp_list_next[icheckb].channel-tp_list_sb[icheckb].channel);
		backslope_mid = float(bky1+bky2/2-bky3-bky4/2)/float(tp_list_next[icheckb].channel-tp_list_sb[icheckb].channel);
		backslope_bottom = float(bky1-bky3)/float(tp_list_next[icheckb].channel-tp_list_sb[icheckb].channel);


		frontangle_top = (atan(slopecm_scale*float(frontslope_top)))*radTodeg;
		backangle_top = (atan(slopecm_scale*float(backslope_top)))*radTodeg;
		frontangle_mid = (atan(slopecm_scale*float(frontslope_mid)))*radTodeg;
		backangle_mid = (atan(slopecm_scale*float(backslope_mid)))*radTodeg;
		frontangle_bottom = (atan(slopecm_scale*float(frontslope_bottom)))*radTodeg;
		backangle_bottom = (atan(slopecm_scale*float(backslope_bottom)))*radTodeg;

		if (abs(frontangle_mid-backangle_mid)>50 and abs(frontangle_top-backangle_top)>50 and abs(frontangle_bottom-backangle_bottom)>50){
		  trigtot += 1;
		  final_tp_list.push_back({tp_list_maxadc[imaxadc].channel, tp_list_maxadc[imaxadc].time_start, tp_list_maxadc[imaxadc].adc_integral, tp_list_maxadc[imaxadc].adc_peak, tp_list_maxadc[imaxadc].time_over_threshold});
		}
		else {
		  break;
		}
	      }
		tp_list_prev = tp_list_next;
	  }
	}
	  hitfound ==false;
	  this_time_max = 0;
	  this_time_min = 0;
	  prev_time_max = 0;
	  prev_time_min = 0;

	  if(tp_list[icheckb].channel = (chnl_maxadc-1)){
	    this_time_max = tp_list[icheckb].time_start + tp_list[icheckb].time_over_threshold;
	    this_time_min =  tp_list[icheckb].time_start;
	    prev_time_max = tp_list_prev[icheckb].time_start + tp_list_prev[icheckb].time_over_threshold;
	    prev_time_min =tp_list_prev[icheckb].time_start;

	    if (tp_list[icheckb].channel == tp_list_next[icheckb].channel) break;

	    if (abs(prev_time_min-this_time_min)<=time_diff or abs(prev_time_max-this_time_max)<=time_diff){
	      hitfound = true;
	      time_diff = abs(prev_time_min-this_time_min);
	      tp_list_next = tp_list;
	      if (this_time_max > time_max) time_max = this_time_max;
	      if (this_time_min < time_min) time_min = this_time_min;
	    }
	  }
      }
    }
  }

  return trigtot;
}
