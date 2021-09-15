/*///////////////////////////////////////////////////////////////////////////////////////////////////
Code based on work from Daisy Kalra, Postdoctoral Research Scientist, Columbia University
Summer 2021

The original intent of this code was to identify Michel electrons from stopping decaying muons

This code was modified in Summer 2021 to identify multiprong candidates (for QE-like nu_mu + Ar -> mu + Np reactions)
as a part of the MicroBooNE R&D program before shutdown in Fall 2021. The ultimate goal of the Michel trigger is to
see if data studies show a similar online trigger efficiency to those completed in MC. The ultimate goal of the 
Multiprong trigger is to serve as a building block for the mu4nu effor (in parallel to the e4nu effort), and will likely
see its first full usage in SBND.

Extension to this trigger may be possible, such as for applications to other multihadron final states resulting from
neutron-antineturon oscillations, and, potentially, tau decays.

For an overview of the idea going in to this trigger, see documents here: https://mitprod-my.sharepoint.com/:f:/g/personal/jbarrow_mit_edu/EuJXN0s5MIhCsWrFzA0vKYQBG0hw7568aOby3MEAnMYDLQ?e=xUrxFx

And the discussion in the OneNote here: https://mitprod-my.sharepoint.com/:o:/g/personal/jbarrow_mit_edu/Evhe2gaHAABIgFsWpdfJ7NQBZkSCAG9AKRfd1Yp3kDh4Mg?e=roCPcF

By Josh Barrow, Zuckerman Postdoctoral Fellow, MIT and TAU
with Daisy Kalra, Adi Ashkenazi (TAU, and Barrow's co-PI), Georgia Karagiorgi (Columbia, PI of Dr. Kalra), and Wes Ketchum (FNAL)

Thanks for the consultancy of all of these and many more colleagues
//////////////////////////////////////////////////////////////////////////////////////////////////*/

// C++ includes
#include <bits/stdc++.h>
#include <iostream>
#include <vector>
#include <fstream>
#include <iomanip>
#include <glob.h>
#include <algorithm>
#include <iterator>
#include <numeric>
#include <map>
#include "TStopwatch.h"
#include <TFile.h>
#include <TH1D.h>
#include <TF1.h>
#include <TCanvas.h>
#include <TString.h>
#include <TStyle.h>
#include <TLegend.h>
#include <TLatex.h>
#include <TMath.h>
#include <TLine.h>
#include <TPad.h>
#include <TGaxis.h>
#include <TBox.h>

using namespace std;

//The trigger primitives (TPs) which we hope to use for our investigations have five basic properties
//One can colloquially think of a TP as a "hit" on the wire of the TPC
//Here, we make a structure for these properties
struct TriggerPrimitive 
{
  uint32_t  chanel              = {0}; //Channel number on which the TP is seen (odd name spelling as to not confuse a vector name use later)
  int64_t   time_start          = {0}; //The start time of the TP relative to the run
  uint16_t  adc_integral        = {0}; //The integral under the ADC curve as a function of time
  uint16_t  adc_peak            = {0}; //The maximum value of the ADC curve (useful for identifying Bragg peaks)
  int32_t   time_over_threshold = {0}; //The total time at which the ADC curve is over baseline  
};

//Boolean to compare channel numbers to "read through" the TPC in some sorted order
bool compare_channel(const TriggerPrimitive& ch_a, const TriggerPrimitive& ch_b)
{
  // smallest comes first                                                                                                            
  return ch_a.chanel < ch_b.chanel ; // and (ch_a.time_start < ch_b.time_start));
}

//**NEED TO UNDERSTAND THIS**
//To allow the finding of the maxADC value index in the vector
int getIndex(vector<uint16_t> v, uint16_t K)
{
  auto it = find(v.begin(), v.end(), K);
  if (it != v.end())
    {
      int index = it - v.begin();
      //std::cout << index << std::endl;                                                                       
      return index;
    }
  else
  	{
    //std::cout << "-1" << std::endl;                                                                       
    return -99;
  }
}

void MultiProngAlgo()
{
  TStopwatch timer;
  //timer.Start();
  //Acquire the dead channel numbers which we want to avoid from extracting TPs from
  int col1, col2; //Columns in the text file of dead channels
  std::vector<int> deadch; //Vector of dead channel numbers
  std::vector<int> nodeadch; //Vector of live channel numbers
  ifstream deadchfile("MCC9_channel_list.txt"); //Stream in the two columned text file of channel numbers
  //ofstream sublistfile("outfiles/sublist.out"); //Stream out sublist entries
  //ofstream multiprongfile("outfiles/multiprong.out"); //Stream out multiprong candidates for check against sublist.out
  //ofstream hitsfile("hits.out"); //Stream out for hits per channel
  //ofstream three_TPs_file("outfiles/triggers.out"); //Stream out for events with more than three hits per wire

  if (deadchfile.is_open() && !deadchfile.eof()) //Begin stream
    {
      while( deadchfile  >> col1 >> col2 ) //Loop through rows
		    {
          if (col2 < 2) //If the channel listed has a value of <2, ignore it  **NEED TO UNDERSTAND WHAT THIS VALUE MEANS**
            {
              deadch.push_back(0);
            }
          else //If the channel listed has a value of >=2, treat it as alive
            {
              deadch.push_back(1);
            }
		    }
    }

  //Open ROOT file of Monte Carlo level truth events
  TFile *fevt = new TFile("Merged_TriggerPrimitiveOfflineAnalyzer_hist_EXT.root");
  TTree * tree =  (TTree*)fevt->Get("tpm/event_tree"); //Get the tree with the TPs
  TFile file("multiprong_analysis.root","RECREATE");//Make new file for multiprong event analysis **THIS DOESN'T WORK AND I DON'T KNOW WHY***
  TTree *multiprong = new TTree("multiprong","EventNumber:Channel:TimeofHit");//Make tree for analysis
  // Declaration of leaf types
  vector<int>     *channel; //Channel number
  vector<int>     *view; //Induction or collection views ({0,1} are induction, {2} is collection)
  vector<float>   *max_ADC; //Maximum ADC value of the TP
  vector<float>   *max_ADC_tick; //Max ADC value's time in time ticks
  vector<float>   *integral_sum; //Integral under the curve of the WHOLE ADC curve
  vector<float>   *tot; //Time over threshold
  vector<float>   *first_tick; //First time tick of TP within (0,3200)ms within a given frame of data
  vector<float>   *integral_over_n; //Integral over n points ("samples") within the waveform, from the "left" in time (first n/N samples)
  // List of branches from the ROOT file
  TBranch        *b_channel; //Channel number
  TBranch        *b_view; //**NEED TO UNDERSTAND THIS**
  TBranch        *b_max_ADC; //Maximum ADC value of the TP
  TBranch        *b_max_ADC_tick; //Max ADC value's time in time ticks
  TBranch        *b_integral_sum; //**NEED TO UNDERSTAND THIS**
  TBranch        *b_tot; //**NEED TO UNDERSTAND THIS**
  TBranch        *b_first_tick; //First time tick of TP **NEED TO UNDERSTAND THIS**
  TBranch        *b_integral_over_n; //**NEED TO UNDERSTAND THIS**
  //Set objects to zero to start
  channel = 0;
  view = 0;
  max_ADC = 0;
  max_ADC_tick = 0;
  integral_sum = 0;
  tot = 0;
  first_tick = 0;
  integral_over_n = 0;
  //Set all branch addresses to draw in data to all variables
  tree->SetMakeClass(1); //Generates some "skeletal" class
  tree->SetBranchAddress("channel", &channel, &b_channel);                                  
  tree->SetBranchAddress("view", &view, &b_view);                                           
  tree->SetBranchAddress("max_ADC", &max_ADC, &b_max_ADC);                                  
  tree->SetBranchAddress("max_ADC_tick", &max_ADC_tick, &b_max_ADC_tick);                   
  tree->SetBranchAddress("integral_sum", &integral_sum, &b_integral_sum);                   
  tree->SetBranchAddress("tot", &tot, &b_tot);                                              
  tree->SetBranchAddress("first_tick", &first_tick, &b_first_tick);                         
  tree->SetBranchAddress("integral_over_n", &integral_over_n, &b_integral_over_n);

  //Set up new tree branches for multiprong analysis, making them pointers for filling later ***THESE DON'T WORK AND I DON'T KNOW WHY***
  int EventNumber, Channel, TimeofHit, ADCHitValue;
  TBranch* EventNumberp=multiprong->Branch("EventNumber",&EventNumber);//Need event number, unlike in original ROOT file
  TBranch* Channelp=multiprong->Branch("Channel",&Channel);//Wire number of TP in the event
  TBranch* TimeofHitp=multiprong->Branch("TimeofHit",&TimeofHit);//Time of start in TP in the event
  TBranch* ADCHitValuep=multiprong->Branch("ADCHitValue",&ADCHitValue);//ADC peak in TP in the event

  //Make a compute time "histogram" (to be filled like one, but will look like a graph with points) to track how long the building of the
  //data structure and the computation of the trigger decision takes
  //Initialize some graphical limits for the event displays
  const int plot_wirebins_col = 3456;//Collection plane wire count (treated as bins)
  const int plot_wirebins_in = 2400;//Induction planes wire counts
  const double plot_wirelower_in0 = -0.5;//Lower graphical limit for x = wires (for first induction plane)
  const double plot_wirelower_in1 = 2399.5;//Lower graphical limit for x = wires (for second induction plane)
  const double plot_wirelower_col = 4799.5;//Lower graphical limit for x = wires (for collection plane)
  const double plot_wireupper_col = 8255.5;//Upper graphical limit for x = wires (for first collection plane)
  const int plot_timebins = 4800;//Bins for time
  const int plot_timelower = 3200;//Lower limit for drift time
  const int plot_timeupper = 7800;//Upper limit for drift time
  //Make histograms
  TH1D* real_compute_time = new TH1D ("real_compute_time","Real Compute Time of Event Mapping and Triggering, All Planes (8255, 4600 tick)",100,0.,0.);
  real_compute_time->GetXaxis()->SetTitle("Trigger Primitives Per Event");
  real_compute_time->GetYaxis()->SetTitle("Real Compute Time");
  //Do the same for the CPU time
  TH1D* cpu_compute_time = new TH1D ("cpu_compute_time","CPU Compute Time of Event Mapping and Triggering, All Planes (8255 wires, 4600 tick)",100,0.,0.);
  cpu_compute_time->GetXaxis()->SetTitle("Trigger Primitives Per Event");
  cpu_compute_time->GetYaxis()->SetTitle("CPU Compute Time");
  //Make histograms of the events and other plots
  TCanvas *canvas = new TCanvas("canvas","canvas",1920,1080);//Make a canvas for the displays
  //Make an event display, filled as a 2D histogram with a "weight" of ADC, filled directly from the TPs from the collection plane
  TH2D* event_truth_allplanes = new TH2D("event_truth_allplanes","Truth Event Display, Collection Plane",8256,plot_wirelower_in0,plot_wireupper_col,plot_timebins,plot_timelower,plot_timeupper);
  event_truth_allplanes->GetXaxis()->SetTitle("Channel/Wire Number");
  event_truth_allplanes->GetYaxis()->SetTitle("Time Ticks");
  event_truth_allplanes->GetZaxis()->SetTitle("ADC Integral Value");
  event_truth_allplanes->SetMarkerStyle(21);
  event_truth_allplanes->SetMarkerSize(2.0);
  //Make an event display, filled directly from the maps (the data structure used in this analysis) as a 2D histogram with a "weight" of ADC from the collection plane
  TH2D* event_mapped_col = new TH2D("event_mapped_col","Mapped Event Display, Collection Plane",plot_wirebins_col,plot_wirelower_col,plot_wireupper_col,plot_timebins,plot_timelower,plot_timeupper);
  event_mapped_col->GetXaxis()->SetTitle("Channel/Wire Number");
  event_mapped_col->GetYaxis()->SetTitle("Time Ticks");
  event_mapped_col->GetZaxis()->SetTitle("ADC Integral Value");
  event_mapped_col->SetMarkerStyle(23);
  event_mapped_col->SetMarkerSize(0.2);
  //Make an overlay/identification area box within the mapped event display, filled as a 2D histogram with points from a loop with particular boundaries on the collection plane
  TH2D* event_identify_multiprong_col = new TH2D("event_identify_multiprong_col","Multiprong Event Identified",plot_wirebins_col,plot_wirelower_col,plot_wireupper_col,plot_timebins,plot_timelower,plot_timeupper);
  event_identify_multiprong_col->SetMarkerStyle(33);
  event_identify_multiprong_col->SetMarkerSize(0.2);
  event_identify_multiprong_col->SetMarkerColor(2);
  //Make an event display, filled as a 2D histogram with a "weight" of ADC, filled directly from the TPs from the induction plane 0
  TH2D* event_truth_in0 = new TH2D("event_truth_in0","Truth Event Display, Induction Plane #0",plot_wirebins_in,plot_wirelower_in0,plot_wirelower_in1,plot_timebins,plot_timelower,plot_timeupper);
  event_truth_in0->GetXaxis()->SetTitle("Channel/Wire Number");
  event_truth_in0->GetYaxis()->SetTitle("Time Ticks");
  event_truth_in0->GetZaxis()->SetTitle("ADC Integral Value");
  event_truth_in0->SetMarkerStyle(21);
  event_truth_in0->SetMarkerSize(2.0);
  //Make an event display, filled directly from the maps (the data structure used in this analysis) as a 2D histogram with a "weight" of ADC from the induction plane 0
  TH2D* event_mapped_in0 = new TH2D("event_mapped_in0","Mapped Event Display, Induction Plane #0",plot_wirebins_in,plot_wirelower_in0,plot_wirelower_in1,plot_timebins,plot_timelower,plot_timeupper);
  event_mapped_in0->GetXaxis()->SetTitle("Channel/Wire Number");
  event_mapped_in0->GetYaxis()->SetTitle("Time Ticks");
  event_mapped_in0->GetZaxis()->SetTitle("ADC Integral Value");
  event_mapped_in0->SetMarkerStyle(23);
  event_mapped_in0->SetMarkerSize(0.2);
  //Make an overlay/identification area box within the mapped event display, filled as a 2D histogram with points from a loop with particular boundaries on induction plane 1
  TH2D* event_identify_multiprong_in0 = new TH2D("event_identify_multiprong_in0","Multiprong Event Identified",plot_wirebins_in,plot_wirelower_in0,plot_wirelower_in1,plot_timebins,plot_timelower,plot_timeupper);
  event_identify_multiprong_in0->SetMarkerStyle(33);
  event_identify_multiprong_in0->SetMarkerSize(0.2);
  event_identify_multiprong_in0->SetMarkerColor(2);
  //Make an event display, filled as a 2D histogram with a "weight" of ADC, filled directly from the TPs from the induction plane 1
  TH2D* event_truth_in1 = new TH2D("event_truth_in1","Truth Event Display, Induction Plane #1",plot_wirebins_in,plot_wirelower_in1,plot_wirelower_col,plot_timebins,plot_timelower,plot_timeupper);
  event_truth_in1->GetXaxis()->SetTitle("Channel/Wire Number");
  event_truth_in1->GetYaxis()->SetTitle("Time Ticks");
  event_truth_in1->GetZaxis()->SetTitle("ADC Integral Value");
  event_truth_in1->SetMarkerStyle(21);
  event_truth_in1->SetMarkerSize(2.0);
  //Make an event display, filled directly from the maps (the data structure used in this analysis) as a 2D histogram with a "weight" of ADC from the induction plane 1
  TH2D* event_mapped_in1 = new TH2D("event_mapped_in1","Mapped Event Display, Induction Plane #1",plot_wirebins_in,plot_wirelower_in1,plot_wirelower_col,plot_timebins,plot_timelower,plot_timeupper);
  event_mapped_in1->GetXaxis()->SetTitle("Channel/Wire Number");
  event_mapped_in1->GetYaxis()->SetTitle("Time Ticks");
  event_mapped_in1->GetZaxis()->SetTitle("ADC Integral Value");
  event_mapped_in1->SetMarkerStyle(23);
  event_mapped_in1->SetMarkerSize(0.2);
  //Make an overlay/identification area box within the mapped event display, filled as a 2D histogram with points from a loop with particular boundaries on induction plane 1
  TH2D* event_identify_multiprong_in1 = new TH2D("event_identify_multiprong_in1","Multiprong Event Identified",plot_wirebins_in,plot_wirelower_in1,plot_wirelower_col,plot_timebins,plot_timelower,plot_timeupper);
  event_identify_multiprong_in1->SetMarkerStyle(33);
  event_identify_multiprong_in1->SetMarkerSize(0.2);
  event_identify_multiprong_in1->SetMarkerColor(2);
  //Set stats box position for these plots
  gStyle->SetStatY(0.9);
  gStyle->SetStatX(0.9);

  //Declare and initialize some important variables
  int64_t time_start; //Time start of the TP
  int32_t time_over_threshold; //Time over threshold of the TP
  uint32_t chanel ; //Channel number (different spelling to differentiate variables)
  uint16_t adc_integral ; //Integral under the ADC curve
  uint16_t adc_peak; //ADC maximum amplitude for each channel
  int detectorplane; //Which one of the three planes being viewed in the detector **NEED TO UNDERSTAND THIS**
  int maxadcind; //Same as above, but saving the TPs slice by slice (slice = 36x5=180 subdivisions of the detector)
  uint16_t maxadc = 0; //Actual ADC value of the TP with index maxadcind within the subdivided slice
  uint16_t braggE = 27500; //27500 is used in uB based on incoming muon angle vs maxadc **NEED TO UNDERSTAND THIS MORE** Minimum threshold, I think
  uint16_t multiprong_min_adc = 0; //Set minimum threshold for MIPs like muons
  int proton_candidate_adc = 90000; //Set minimum threshold for proton cadidates in a give sublist
  //To convert time ticks to cm, multiply by 1/25 **USEFUL**
  //To convert channels to distance, recognize that the spacing between channels is 0.3cm **USEFUL**
  //Declare and initialize some useful counters
  int tracklen = 26; //**NEED TO UNDERSTAND THIS**
  const float radTodeg = 180./3.1415926535; //Convert radians to degrees
  //Channel number ranges for wire planes
  const uint32_t ColPlStartChnl = 4800; //Collection plane starting channel number
  const uint32_t ColPlEndChnl = 8255; //Collection plane ending channel number
  const uint32_t IndPl1StartChnl = 0; //Induction plane starting channel number **NEED TO CHECK THIS NUMBER**
  const uint32_t IndPl1EndChnl = 2399; //Induction plane ending channel number **NEED TO CHECK THIS NUMBER**
  const uint32_t IndPl2StartChnl = 2400; //Induction plane starting channel number **NEED TO CHECK THIS NUMBER**
  const uint32_t IndPl2EndChnl = 4799; //Induction plane ending channel number **NEED TO CHECK THIS NUMBER**  
  int contiguous_tolerance = 16; //**NEED TO UNDERSTAND THIS**
  const int64_t boxwidtime = 1150; //Time ticks (division of 4600/5)
  const uint32_t boxwidch = 96; //**NEED TO UNDERSTAND THIS**
  //Make a bunch of vectors of TP quantities
  //(TPs for a given drift of 4600ms)
  std::vector<TriggerPrimitive> tp_list; //TP vector list
  //std::vector<TriggerPrimitive> sublist;
  std::map<int32_t,int32_t> wiremap;
  std::map<int32_t,std::vector<int64_t>> timemap;
  std::map<int32_t,std::vector<int64_t>> adcmap;
  std::map<int32_t,int32_t>::iterator iter;
  std::map<int32_t,int32_t>::iterator cursor;
  std::map<int32_t,std::vector<int64_t>>::iterator iterr;
  std::map<int32_t,std::vector<int64_t>>::iterator iterrr;
  
  //Get number of entries from tree to loop over
  Int_t nevent = tree->GetEntries();
  std::cout << "Number of events in ROOT file: " << nevent << std::endl;
  //Start loop over events (which are actually frames of data //**NEED TO UNDERSTAND THIS**
  for (Int_t evt=3; evt<4/*nevent*/; evt++)
    {
      //Start a timer at the beginning of each event to track the fillint of the TPs vector
      timer.Start();
      //Start every event with a cleared set of histograms to fill
      event_truth_allplanes->Reset(); event_mapped_col->Reset(); event_truth_in0->Reset(); event_mapped_in0->Reset(); event_truth_in1->Reset(); event_mapped_in1->Reset();
      event_identify_multiprong_col->Reset(); event_identify_multiprong_in0->Reset(); event_identify_multiprong_in1->Reset();
      TString hitsfilename_allplanes = "outfiles/hits_allplanes_";//Make a file for each event for a full printout of the data structure for validation
      hitsfilename_allplanes += evt;
      hitsfilename_allplanes += ".out";
      ofstream hitsfile_allplanes(hitsfilename_allplanes); //Stream out for hits per channel for all planes
      //Get the event from the MC tree
      tree->GetEntry(evt);
		  std::cout << "Entry: " << tree->GetEntry(evt) << std::endl;
    	//If running over all the events, then after starting the loop over events, make sure to initialize vars and clear vectors and maps
    	tp_list.clear(); wiremap.clear(); timemap.clear(); adcmap.clear();
      
      //This is required to run the algorithms over a ROOT file with many number of events
      //So, For each event, we are looping over number of channels to take into account all the TPs 
      //from all the channels for a particular event
      for (int chh=0; chh<(*channel).size(); chh++)
        {
          //<=3 OR ==0 OR ==1 SEPARATELY!-->RUN OVER CODE THREE TIMES WITH THE CHANGE, OR PUT IN ANOTHER LOOP?
          if ((*view)[chh] <= 2)
            {
              chanel = (*channel)[chh];
              time_start = (*first_tick)[chh];
              time_over_threshold = (*tot)[chh];
              adc_integral = (*integral_sum)[chh];
              adc_peak = (*max_ADC)[chh];
              
              if (time_start >= 3200 and time_start <= 7800)//4600 time ticks (full drift)
                { 
                  tp_list.push_back({chanel, time_start, adc_integral, adc_peak, time_over_threshold});//Fill TP vectors and will be sorted in order soon
                }
            }
        }
      timer.Stop();
      std::cout << " Time for the filling of the trigger primitive vector for event #" << evt << " with complete collection plane frames: Real time = " << timer.RealTime() << "s, CPU time = " << timer.CpuTime() << "s" << std::endl;
      timer.Clear();
      //Stream out event about the event/drift to the screen
      std::cout << "E V E N T / D R I F T    N U M B E R   : " << evt << std::endl;
      //Stream out TP vector size for this event/drift to the screen
      std::cout << "TPList size for this event: " << evt << " is : " << tp_list.size() << std::endl;
      //Order the TPs in the vector by comparing channel numbers (puts everything consecutively)
      std::sort (tp_list.begin(), tp_list.end(), compare_channel);
      //Now make a vector of time indices in ticks for each 5 boxes/slices
      //boxwidtime = 1150; 7800 - 3200 = 4800; 4800 / 1150 = 4 + 1 = 5 (need the +1 for the first iteration)
      //Channel slices to divide the collection plane channels
      //For the collection plane:
      //Range is 4800 to 8255; 8255 + 96 = 8351; 8351 - 4800 = 3551; (3551 + 1) / 96 = 37 (need the +1 for the first iteration)
      //I believe this means we have 37 "edges" in time from which we have 36 actual boxes/slices in time
      //Start a loop running through the full list of TPs
      int contiguous_channels = 0;
      int proton_candidate_count = 0;
      timer.Start();
      /*/////////////////////////////// DATA STRUCTURE BEGIN ///////////////////////////////*/
      for (int i=0; i<tp_list.size(); ++i)
        {
          //Fill multiprong file branch for visualizations of all TPs for a given event
          EventNumber = evt;
          EventNumberp->Fill();
          Channel = tp_list[i].chanel;
          Channelp->Fill();
          TimeofHit = tp_list[i].time_start;
          TimeofHitp->Fill();
          ADCHitValue = tp_list[i].adc_integral;
          ADCHitValuep->Fill();
          event_truth_allplanes->Fill(Channel,TimeofHit,ADCHitValue);//Fill the truth MC event display on TP at a time
          //Make cuts on this sublist for a minimum amoung of TPC activity (ADC value)
          if (tp_list[i].adc_integral > multiprong_min_adc)
            {
              //Initialize the number of hits on a given wire
              int wirehitcount = 0;
              std::vector<int64_t> timeofhits;
              //Look only at the collection plane (THIS WILL CHANGE)
              for (int iwire = 0/*ColPlStartChnl*/; iwire < ColPlEndChnl+1; iwire++)
                {
                  //If the wire number is the same as the channel number in a given TP, start looking at it
                  if (iwire == tp_list[i].chanel)
                    {
                      //If the wiremape is not empty (after some filling) then allow for updates
                      if (!wiremap.empty() && !timemap.empty())
                        {
                          //Update the given wire with an iterator
                          iter = wiremap.find(iwire);
                          iterr = timemap.find(iwire);
                          //If the wiremap has a single or more entries already (of the number of hits), then permit it to update
                          if (iter != wiremap.end() && iterr != timemap.end() && wiremap[iwire] >= 1 && timemap[iwire].size() >= 1)
                            {
                              //Save some temporary stuff during the update process
                              int tmphits;//Save the original number of hits
                              std::vector<int64_t> tmp_timeofhits;//Save the original time of those hits
                              tmphits = wiremap[iwire];//Get the original number of hits
                              tmp_timeofhits.insert(tmp_timeofhits.end(),timemap[iwire].begin(),timemap[iwire].end());//Get the original vector of times of those hits
                              wiremap.erase(iwire);//Erase that particular entry in the wire map
                              timemap.erase(iwire);//Erase that particular entry in the time map
                              tmphits++;//Iterate up by one hit per new TP
                              tmp_timeofhits.push_back(tp_list[i].time_start);
                              sort(tmp_timeofhits.begin(),tmp_timeofhits.end());//Time order the vector
                              wiremap.insert({iwire,tmphits});//Insert the newly updated value of hits
                              timemap[iwire] = tmp_timeofhits;//Insert the newly updated vector of times for these hits
                              tmp_timeofhits.clear();
                            }
                        }
                      if (timemap[iwire].size()<1)
                        {
                          wirehitcount++;//Add a single wire count
                          wiremap.insert({iwire,wirehitcount});//Insert the wire hit count of =1 into the map (will be updated above)
                          timeofhits.push_back(tp_list[i].time_start);//Grab the start time of the TP
                          timemap[iwire] = timeofhits;//Save the first vector entry of the time of the hit
                        }
                    }
                }
            }
        }
      //Make ADC map and ADC mean values per plane; don't yet know exactly how to generally calculate the median for an unordered set
      int32_t adc_mean_col = 0, adc_mean_in0 = 0, adc_mean_in1 = 0;
      for (int iii=0; iii<tp_list.size(); ++iii)
        {
          iterr = timemap.find(tp_list[iii].chanel);
          int tmp_adc_count = 0; tmp_adc_count = timemap[tp_list[iii].chanel].size();
          for (int j = 0; j < tmp_adc_count; j++)
            {
              if (iterr != timemap.end() && timemap[tp_list[iii].chanel].at(j) == tp_list[iii].time_start)
                {
                  //std::cout << "Time map value is: " << timemap[tp_list[iii].chanel].at(j) << " and TP list value is: " << tp_list[iii].time_start << std::endl;
                  adcmap[tp_list[iii].chanel].resize(tmp_adc_count);
                  adcmap[tp_list[iii].chanel].at(j) = tp_list[iii].adc_integral;
                  //std::cout << "ADC map value is: " << adcmap[tp_list[iii].chanel].at(j) << " and TP list value is: " << tp_list[iii].adc_integral << std::endl;
                  if (tp_list[iii].chanel>=ColPlStartChnl && tp_list[iii].chanel<=ColPlEndChnl)
                    {
                      adc_mean_col += tp_list[iii].adc_integral;
                    }
                  if (/*tp_list[iii].chanel>=IndPl1StartChnl && */tp_list[iii].chanel<=IndPl1EndChnl)
                    {
                      adc_mean_in0 += tp_list[iii].adc_integral;
                    }
                  if (tp_list[iii].chanel>=IndPl2StartChnl && tp_list[iii].chanel<=IndPl2EndChnl)
                    {
                      adc_mean_in1 += tp_list[iii].adc_integral;
                    }
                }
            }
        }
      /*std::cout << "Collection Plane Total ADC: " << adc_mean_col << std::endl;
      std::cout << "Induction Plane 1 Total ADC: " << adc_mean_in0 << std::endl;
      std::cout << "Induction Plane 2 Total ADC: " << adc_mean_in1 << std::endl;*/
      adc_mean_col = adc_mean_col/tp_list.size();
      adc_mean_in0 = adc_mean_in0/tp_list.size();
      adc_mean_in1 = adc_mean_in1/tp_list.size();
      /*std::cout << "Collection Plane Average ADC: " << adc_mean_col << std::endl;
      std::cout << "Induction Plane 1 Average ADC: " << adc_mean_in0 << std::endl;
      std::cout << "Induction Plane 2 Average ADC: " << adc_mean_in1 << std::endl;*/
      /*/////////////////////////////// DATA STRUCTURE COMPLETE ///////////////////////////////*/

      ///////////////////////////////////////////////////////////////////////////////////////////
      
      /*/////////////////////////////// TRIGGER STRUCTURE BEGIN ///////////////////////////////*/

      //Need to be able to store positions and times of trigger candidates
      //Probably need these to be vectors to be able to store multiple passing candidates per drift
      int number_multiprong_triggers_forward_col=0, number_multiprong_triggers_backward_col=0;//Per event, how many triggers do we have on the collection plane?
      int number_multiprong_triggers_forward_in0=0, number_multiprong_triggers_backward_in0=0;//Per event, how many triggers do we have on the induction plane 0?
      int number_multiprong_triggers_forward_in1=0, number_multiprong_triggers_backward_in1=0;//Per event, how many triggers do we have on the collection plane?
      //The above count should be the size of the below vectors
      std::vector<uint32_t> multiprong_candidate_wire_forward_col, multiprong_candidate_wire_backward_col;//Create variables to store the trigger candidate wire position on collection plane
      std::vector<int64_t>  multiprong_candidate_time_forward_col, multiprong_candidate_time_backward_col;//Creat variables to store trigger candidate times on collection plane
      std::vector<uint32_t> multiprong_candidate_wire_forward_in0, multiprong_candidate_wire_backward_in0;//Create variables to store the trigger candidate wire position on induction plane 0
      std::vector<int64_t>  multiprong_candidate_time_forward_in0, multiprong_candidate_time_backward_in0;//Creat variables to store trigger candidate times on induction plane 0
      std::vector<uint32_t> multiprong_candidate_wire_forward_in1, multiprong_candidate_wire_backward_in1;//Create variables to store the trigger candidate wire position on induction plane 1
      std::vector<int64_t>  multiprong_candidate_time_forward_in1, multiprong_candidate_time_backward_in1;//Creat variables to store trigger candidate times on induction plane 1
      //Construct a vector of a constant wire length (10) to fill with the last few (10) number of hits on a set of wire
      //This vector needs to be dynamically overwritten as we walk through the number of wires, maintaining its legth,
      //deleting the first entry and then appending the new entry; when a patter emerges, we should investigate
      std::vector<uint32_t> partial_hit_history;//This vector is intended for use to track the microscopic history of the topologies within the TPC
      //Set the size of the vecotor to be studied (i.e. the number of wire to consider the history of)
      const int partial_hit_history_size = 10;//This number cannot be too high, as the plan is to implement this algorith on 96 channel-wide detector slices...
      //Use the wiremap to start an iterator over wire numbers
      for (cursor = wiremap.begin(); cursor!=wiremap.end(); cursor++)
        {
          partial_hit_history.push_back(cursor->second);//Fill the partial event history before any continue statements skipping the wire
          if (partial_hit_history.size() > partial_hit_history_size)//Set the appropriate vector length; thus, the iterator needs to run for (10+1) loops to enter this statement 
            {
              //To maintain the vector length, erase only the first element; this keeps the length of the vector to a constant (10) of the last (10) hits
              partial_hit_history.erase(partial_hit_history.begin());//After this, throughout the rest of the loop, the vector is of length (10) and shows the last (10) wire's activity
            }
          if (cursor->second == 0) { continue; } //If there is no activity/hit on a given wire, continue to the next wire          
          uint32_t tmp_wirenumber_singlehit;//Make a temporary variable to store the wire number if a single hit exists on the wire
          int64_t tmp_time_singlehit;//Make a temporary variable to store the time of the single hit
          if (cursor->second == 0) { continue; }//If there are no hits on a given wire, move on to the next wire          
          if (cursor->second == 1)//If there is only one hit on a given wire, move on to the next wire
            {
              tmp_wirenumber_singlehit = cursor->first;//Fill this temporary wire number variable
              tmp_time_singlehit = timemap[cursor->first].at(0);//Fill this temporary time variable
              continue;//Continue to the next wire
            }
          //If there is greater than or equal to two hits on a wire after a single hit was on a wire, investigate!
          //Given that there is noise on the wires, we only want to pay attention to those candidates which do not
          //coincide with a noisy wire, where many hits can occur; thus, make sure to only look for candiates if b/t
          //2-30 TPs are seen on a given wire
          //The first main trigger is when we go from a single TP on a preceding wire, followed by two or more TPs
          if (cursor->second >=2 && cursor->second <= 30 && wiremap[tmp_wirenumber_singlehit] == 1)
            {
              //Make a temporary vector of time differences on the wire (everything is already time ordered in the mapped vectors)
              std::vector<int64_t> tmp_hittimedifferences;
              for (auto it = 1; it < timemap[cursor->first].size(); it++)//Iterate through the vector of times in the timemap
                {
                  //Fill the temporary vector with differences from the already ordered vector of hit times in the timemap
                  tmp_hittimedifferences.push_back(timemap[cursor->first].at(it)-timemap[cursor->first].at(it-1));
                }
              int64_t tmp_hittimedifferences_min;//Make a temporary variable to store the minimum time in the difference vector
              int64_t tmp_hitadc_max;//Make a temporary variable to store the maximum ADC integral value in the hit list from the adcmap
              tmp_hittimedifferences_min = *min_element(tmp_hittimedifferences.begin(),tmp_hittimedifferences.end());//Fill the time
              tmp_hitadc_max = *max_element(adcmap[cursor->first].begin(),adcmap[cursor->first].end());
              //Consider just the first induction plane 0, making sure the time differences do not exceed 22 ticks and we are above the mean ADC value
              //The 22 time ticks is simply tuned from looking at several event displays
              if (tmp_hittimedifferences_min<22 && tmp_hitadc_max>adc_mean_in0 && cursor->first >= IndPl1StartChnl && cursor->first <= IndPl1EndChnl)
                {
                  number_multiprong_triggers_forward_in0++;
                  multiprong_candidate_wire_forward_in0.push_back(tmp_wirenumber_singlehit); multiprong_candidate_time_forward_in0.push_back(tmp_time_singlehit);
                }
              //Consider just the second induction plane 1, making sure the time differences do not exceed 22 ticks and we are above the mean ADC value
              //The 22 time ticks is simply tuned from looking at several event displays
              if (tmp_hittimedifferences_min<22 && tmp_hitadc_max>adc_mean_in1 && cursor->first >= IndPl2StartChnl && cursor->first <= IndPl2EndChnl)
                {
                  number_multiprong_triggers_forward_in1++;
                  multiprong_candidate_wire_forward_in1.push_back(tmp_wirenumber_singlehit); multiprong_candidate_time_forward_in1.push_back(tmp_time_singlehit);
                }
              //Consider just the collection plane, making sure the time differences do not exceed 22 ticks and we are above the mean ADC value
              //The 22 time ticks is simply tuned from looking at several event displays
              if (tmp_hittimedifferences_min<22 && tmp_hitadc_max>adc_mean_col && cursor->first >= ColPlStartChnl && cursor->first <= ColPlEndChnl)
                {
                  number_multiprong_triggers_forward_col++;
                  multiprong_candidate_wire_forward_col.push_back(tmp_wirenumber_singlehit); multiprong_candidate_time_forward_col.push_back(tmp_time_singlehit);
                }
            }
          //Of course, given the candidates will all be cosmics, there is a great likelihood that a candidate will actually be on a wire where there is
          //already much activity (>=2 hits on the current wire, and >=2 hits preceding it). We have to be able to trigger on these as well!
          //These more complicated topologies can be investigated using the partial event history vector, which currently includes the activity (hits)
          //on the last (10) wires; the vector is this (10) size for each iteration of this loop
          if (partial_hit_history.size() == partial_hit_history_size)//When the vector is the appropriate size, begin looking at it
            {
              //If the sum of the vector elements (hits) accumulates to more than the size of the vector, this is likely worth investigating
              //First, consider a potential two-prong candidate
              if (std::accumulate(partial_hit_history.begin(),partial_hit_history.end(),decltype(partial_hit_history)::value_type(0)) > partial_hit_history_size
               && std::accumulate(partial_hit_history.begin(),partial_hit_history.end(),decltype(partial_hit_history)::value_type(0)) <= 2*partial_hit_history_size
                 )
                {
                  std::cout << "Potential 2+ prong topology for Wire #" << cursor->first-partial_hit_history_size << "-" << cursor->first << " the hit pattern is: ";
                  for (auto i = 0; i < partial_hit_history.size(); i++)
                    {
                      std::cout << partial_hit_history.at(i) << "  ";
                    }
                  std::cout << " and the sum of the hits is: " << std::accumulate(partial_hit_history.begin(),partial_hit_history.end(),decltype(partial_hit_history)::value_type(0)) << std::endl;

                }
              
            }
        }
        
      /*//////////////////////////////// TRIGGER STRUCTURE END ////////////////////////////////*/

      ///////////////////////////////////////////////////////////////////////////////////////////
      
      timer.Stop();
      std::cout << " Time for filling the event maps and triggering for event #" << evt << " for all planes: Real time = " << timer.RealTime() << "s, CPU time = " << timer.CpuTime() << "s" << std::endl;
      timer.Clear();
      //Fill compute time histograms with x values and "weights" (times) for y value (will plot these like graphs with points)
      real_compute_time->Fill(tp_list.size(),timer.RealTime());
      cpu_compute_time->Fill(tp_list.size(),timer.CpuTime());
      //Start up a new timer for the ROOT stuff
      timer.Start();
      canvas->cd();//Go to the appropriate canvas
      event_truth_allplanes->Draw("COLZ");//Draw the TRUTH LEVEL (from MC) event display
      //Name things
      TString eventfilename = "eventdisplays/"; eventfilename += evt; eventfilename += ".png";
      TString eventrootfilename = "eventdisplays/"; eventrootfilename += evt; eventrootfilename += ".root";
      TString eventname = "event_"; eventname += evt;
      TString eventtitle = "Event Display: #"; eventtitle += evt;
      event_truth_allplanes->SetName(eventname);
      event_truth_allplanes->SetTitle(eventtitle);
      event_truth_allplanes->Write();//Write to the ROOT file
      canvas->Print(eventfilename);//Print to the image (.png) file
      canvas->Print(eventrootfilename);//Print to a .root file
      canvas->Clear();//Clear the canvas for the next plot
      //Write out all of the information contained in the maps of the TPs to validate the data structure
      hitsfile_allplanes << "Event\tChannel\tHits\tTimes & ADCs" << std::endl;
      for (cursor = wiremap.begin(); cursor!=wiremap.end(); cursor++)//Use the wiremap to start an iterator over wire numbers
        {
          if (cursor->second >= 1)//Only look at those wires with at least one hit
            {
              hitsfile_allplanes << evt;//Print out the event number
              hitsfile_allplanes << "\tWire #" << cursor->first << ": ";//Print out the wire number
              hitsfile_allplanes << "\t# of Hits: " << cursor->second;//Print out the number of hits on that wire
              int tmp_time_count = 0; tmp_time_count = timemap[cursor->first].size();//Make a temporary limit of an iterator for the times on that wire
              for (int ii=0; ii<tmp_time_count; ii++)
                {
                  //Iterate through those time vector element of the timemap and also get their ADC values from the adcmap
                  hitsfile_allplanes << "\tTime #" << ii+1 << ": " << timemap[cursor->first].at(ii) << ", ADC: " << adcmap[cursor->first].at(ii);
                  //Fill another event display directly from these maps for validation
                  if (cursor->first>4799 && cursor->first<8256)
                    {
                      event_mapped_col->Fill(cursor->first,timemap[cursor->first].at(ii),adcmap[cursor->first].at(ii));
                    }
                  if (cursor->first>=0 && cursor->first<2400)
                    {
                      event_mapped_in0->Fill(cursor->first,timemap[cursor->first].at(ii),adcmap[cursor->first].at(ii));
                    }
                  if (cursor->first>=2400 && cursor->first<=4799)
                    {
                      event_mapped_in1->Fill(cursor->first,timemap[cursor->first].at(ii),adcmap[cursor->first].at(ii));
                    }           
                }
              hitsfile_allplanes << std::endl;
            }
        }
      //canvas->cd();
      //Draw event display for collection plane
      event_mapped_col->Draw("COLZ");
      //Draw candidate position identification overlay for collection plane
      for (int jj = 0; jj < number_multiprong_triggers_backward_col+number_multiprong_triggers_forward_col; jj++)
        {
          TLine *TLineBottom = new TLine(multiprong_candidate_wire_forward_col.at(jj)-15, multiprong_candidate_time_forward_col.at(jj)-15,
                                         multiprong_candidate_wire_forward_col.at(jj)+15, multiprong_candidate_time_forward_col.at(jj)-15);
          TLineBottom->SetLineColor(2);
          TLineBottom->SetLineWidth(1);
          TLineBottom->Draw("lsame");
          TLine *TLineTop = new TLine(multiprong_candidate_wire_forward_col.at(jj)-15, multiprong_candidate_time_forward_col.at(jj)+15,
                                      multiprong_candidate_wire_forward_col.at(jj)+15, multiprong_candidate_time_forward_col.at(jj)+15);
          TLineTop->SetLineColor(2);
          TLineTop->SetLineWidth(1);
          TLineTop->Draw("lsame");
          TLine *TLineLeft = new TLine(multiprong_candidate_wire_forward_col.at(jj)-15, multiprong_candidate_time_forward_col.at(jj)-15,
                                       multiprong_candidate_wire_forward_col.at(jj)-15, multiprong_candidate_time_forward_col.at(jj)+15);
          TLineLeft->SetLineColor(2);
          TLineLeft->SetLineWidth(1);
          TLineLeft->Draw("lsame");
          TLine *TLineRight = new TLine(multiprong_candidate_wire_forward_col.at(jj)+15, multiprong_candidate_time_forward_col.at(jj)-15,
                                        multiprong_candidate_wire_forward_col.at(jj)+15, multiprong_candidate_time_forward_col.at(jj)+15);
          TLineRight->SetLineColor(2);
          TLineRight->SetLineWidth(1);
          TLineRight->Draw("lsame");
        }
      TString mapped_truth_eventfilename_col = "eventdisplays/map_truth_"; mapped_truth_eventfilename_col += evt; mapped_truth_eventfilename_col += "_col.png";
      TString mapped_truth_eventrootfilename_col = "eventdisplays/map_truth_"; mapped_truth_eventrootfilename_col += evt; mapped_truth_eventrootfilename_col += "_col.root";
      TString mapped_truth_eventname_col = "map_truth_event_col_"; mapped_truth_eventname_col += evt;
      TString mapped_truth_eventtitle_col = "Collection Plane Mapped Event Display: #"; mapped_truth_eventtitle_col += evt;
      event_mapped_col->SetName(mapped_truth_eventname_col);
      event_mapped_col->SetTitle(mapped_truth_eventtitle_col);
      event_mapped_col->Write();
      canvas->Print(mapped_truth_eventfilename_col);
      canvas->Print(mapped_truth_eventrootfilename_col);
      canvas->Clear();
      //Draw event display for induction plane 0
      event_mapped_in0->Draw("COLZ");
      //Draw candidate position identification overlay for induction plane 0
      for (int jj = 0; jj < number_multiprong_triggers_backward_in0+number_multiprong_triggers_forward_in0; jj++)
        {
          TLine *TLineBottom = new TLine(multiprong_candidate_wire_forward_in0.at(jj)-15, multiprong_candidate_time_forward_in0.at(jj)-15,
                                         multiprong_candidate_wire_forward_in0.at(jj)+15, multiprong_candidate_time_forward_in0.at(jj)-15);
          TLineBottom->SetLineColor(2);
          TLineBottom->SetLineWidth(1);
          TLineBottom->Draw("lsame");
          TLine *TLineTop = new TLine(multiprong_candidate_wire_forward_in0.at(jj)-15, multiprong_candidate_time_forward_in0.at(jj)+15,
                                      multiprong_candidate_wire_forward_in0.at(jj)+15, multiprong_candidate_time_forward_in0.at(jj)+15);
          TLineTop->SetLineColor(2);
          TLineTop->SetLineWidth(1);
          TLineTop->Draw("lsame");
          TLine *TLineLeft = new TLine(multiprong_candidate_wire_forward_in0.at(jj)-15, multiprong_candidate_time_forward_in0.at(jj)-15,
                                       multiprong_candidate_wire_forward_in0.at(jj)-15, multiprong_candidate_time_forward_in0.at(jj)+15);
          TLineLeft->SetLineColor(2);
          TLineLeft->SetLineWidth(1);
          TLineLeft->Draw("lsame");
          TLine *TLineRight = new TLine(multiprong_candidate_wire_forward_in0.at(jj)+15, multiprong_candidate_time_forward_in0.at(jj)-15,
                                        multiprong_candidate_wire_forward_in0.at(jj)+15, multiprong_candidate_time_forward_in0.at(jj)+15);
          TLineRight->SetLineColor(2);
          TLineRight->SetLineWidth(1);
          TLineRight->Draw("lsame");
        }
      TString mapped_truth_eventfilename_in0 = "eventdisplays/map_truth_"; mapped_truth_eventfilename_in0 += evt; mapped_truth_eventfilename_in0 += "_in0.png";
      TString mapped_truth_eventrootfilename_in0 = "eventdisplays/map_truth_"; mapped_truth_eventrootfilename_in0 += evt; mapped_truth_eventrootfilename_in0 += "_in0.root";
      TString mapped_truth_eventname_in0 = "map_truth_event_in0_"; mapped_truth_eventname_in0 += evt;
      TString mapped_truth_eventtitle_in0 = "First Induction Plane Mapped Event Display: #"; mapped_truth_eventtitle_in0 += evt;
      event_mapped_in0->SetName(mapped_truth_eventname_in0);
      event_mapped_in0->SetTitle(mapped_truth_eventtitle_in0);
      event_mapped_in0->Write();
      canvas->Print(mapped_truth_eventfilename_in0);
      canvas->Print(mapped_truth_eventrootfilename_in0);
      canvas->Clear();
      //Draw event display for induction plane 1
      event_mapped_in1->Draw("COLZ");
      //Draw candidate position identification overlay for induction plane 1
      for (int jj = 0; jj < number_multiprong_triggers_backward_in1+number_multiprong_triggers_forward_in1; jj++)
        {
          TLine *TLineBottom = new TLine(multiprong_candidate_wire_forward_in1.at(jj)-15, multiprong_candidate_time_forward_in1.at(jj)-15,
                                         multiprong_candidate_wire_forward_in1.at(jj)+15, multiprong_candidate_time_forward_in1.at(jj)-15);
          TLineBottom->SetLineColor(2);
          TLineBottom->SetLineWidth(1);
          TLineBottom->Draw("lsame");
          TLine *TLineTop = new TLine(multiprong_candidate_wire_forward_in1.at(jj)-15, multiprong_candidate_time_forward_in1.at(jj)+15,
                                      multiprong_candidate_wire_forward_in1.at(jj)+15, multiprong_candidate_time_forward_in1.at(jj)+15);
          TLineTop->SetLineColor(2);
          TLineTop->SetLineWidth(1);
          TLineTop->Draw("lsame");
          TLine *TLineLeft = new TLine(multiprong_candidate_wire_forward_in1.at(jj)-15, multiprong_candidate_time_forward_in1.at(jj)-15,
                                       multiprong_candidate_wire_forward_in1.at(jj)-15, multiprong_candidate_time_forward_in1.at(jj)+15);
          TLineLeft->SetLineColor(2);
          TLineLeft->SetLineWidth(1);
          TLineLeft->Draw("lsame");
          TLine *TLineRight = new TLine(multiprong_candidate_wire_forward_in1.at(jj)+15, multiprong_candidate_time_forward_in1.at(jj)-15,
                                        multiprong_candidate_wire_forward_in1.at(jj)+15, multiprong_candidate_time_forward_in1.at(jj)+15);
          TLineRight->SetLineColor(2);
          TLineRight->SetLineWidth(1);
          TLineRight->Draw("lsame");
        }
      TString mapped_truth_eventfilename_in1 = "eventdisplays/map_truth_"; mapped_truth_eventfilename_in1 += evt; mapped_truth_eventfilename_in1 += "_in1.png";
      TString mapped_truth_eventrootfilename_in1 = "eventdisplays/map_truth_"; mapped_truth_eventrootfilename_in1 += evt; mapped_truth_eventrootfilename_in1 += "_in1.root";
      TString mapped_truth_eventname_in1 = "map_truth_event_in1_"; mapped_truth_eventname_in1 += evt;
      TString mapped_truth_eventtitle_in1 = "Second Induction Plane Mapped Event Display: #"; mapped_truth_eventtitle_in1 += evt;
      event_mapped_in1->SetName(mapped_truth_eventname_in1);
      event_mapped_in1->SetTitle(mapped_truth_eventtitle_in1);
      event_mapped_in1->Write();
      canvas->Print(mapped_truth_eventfilename_in1);
      canvas->Print(mapped_truth_eventrootfilename_in1);
      canvas->Clear();
      timer.Stop();
      std::cout << " Time for making event diplay and printing out event maps for event #" << evt << " with all planes: Real time = " << timer.RealTime() << "s, CPU time = " << timer.CpuTime() << "s" << std::endl;
      timer.Clear();
	} //End loop over nevents
  canvas->cd();
  real_compute_time->Draw("*");
  canvas->Print("outputplots/realcomputetime.png"); canvas->Clear();
  cpu_compute_time->Draw("*");
  canvas->Print("outputplots/cpucomputetime.png");

  file.Write();
  file.Close();
} //End loop over MultiProngAlgo function