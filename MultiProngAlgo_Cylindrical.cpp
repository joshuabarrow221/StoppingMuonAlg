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
#include <list>
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
#define PI 3.14159265
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


void MultiProngAlgo_Cylindrical()
{
  TStopwatch timer;
  //timer.Start();
  //Acquire the dead channel numbers which we want to avoid from extracting TPs from
  int col1, col2; //Columns in the text file of dead channels
  std::vector<int> deadch; //Vector of dead channel numbers
  std::vector<int> nodeadch; //Vector of live channel numbers
  ifstream deadchfile("/uboone/app/users/jbarrow/StoppingMuonAlg/MCC9_channel_list.txt"); //Stream in the two columned text file of channel numbers
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
  TFile *fevt = new TFile("/uboone/app/users/jbarrow/StoppingMuonAlg/Merged_TriggerPrimitiveOfflineAnalyzer_hist_EXT.root");
  TTree * tree =  (TTree*)fevt->Get("tpm/event_tree"); //Get the tree with the TPs
  TFile file("multiprong_analysis_cylindrical.root","RECREATE");//Make new file for multiprong event analysis **THIS DOESN'T WORK AND I DON'T KNOW WHY***
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
  //Create maps for the data structure of the whole TPC; this is needed in order to wire-order and time-order the hits
  std::map<int32_t,int32_t> wiremap;
  std::map<int32_t,std::vector<int64_t>> timemap;
  std::map<int32_t,std::vector<int64_t>> adcmap;
  //Create some iterators to run over the maps
  std::map<int32_t,int32_t>::iterator iter;
  std::map<int32_t,int32_t>::iterator cursor;
  std::map<int32_t,std::vector<int64_t>>::iterator iterr;
  std::map<int32_t,std::vector<int64_t>>::iterator iterrr;
  const int32_t acceptable_maximum_hits_on_wire = 30;//The maximum number of hits allowed on a wire; do this to elminate noise
  const int partial_wire_history_size = 35;//This number cannot be too high, as the plan is to implement this algorith on 96 channel-wide detector slices...
  const int partial_wire_history_inner_radius = 10;//This number defines the inner "radius" of the "shell" of the partial history
  const int acceptable_time_diff = 100;//Difference between hits' number of time ticks for an sequence of hits to be considered for a trigger
  const int acceptable_similar_angles = 6;//Number of similar theta values to make an average of these thetas
  const double angular_tolerance = 3.;//Set up an acceptable tolerance for the reconstructed angles of hits from the centroid for "form" tracks
  
  //Get number of entries from tree to loop over
  Int_t nevent = tree->GetEntries();
  std::cout << "Number of events in ROOT file: " << nevent << std::endl;
  //Start loop over events (which are actually frames of data //**NEED TO UNDERSTAND THIS**
  for (Int_t evt=64; evt<65/*nevent*/; evt++)
    {
      //Start a timer at the beginning of each event to track the fillint of the TPs vector
      timer.Start();
      //Start every event with a cleared set of histograms to fill
      event_truth_allplanes->Reset(); event_mapped_col->Reset(); event_truth_in0->Reset(); event_mapped_in0->Reset(); event_truth_in1->Reset(); event_mapped_in1->Reset();
      event_identify_multiprong_col->Reset(); event_identify_multiprong_in0->Reset(); event_identify_multiprong_in1->Reset();
      TString hitsfilename_allplanes = "outfiles/hits_allplanes_";//Make a file for each event for a full printout of the data structure for validation
      hitsfilename_allplanes += evt;
      hitsfilename_allplanes += ".out";
      TString original_partial_history_filename_allplanes = "outfiles/original_partial_history_allplanes_";//Make a file for each event for a full printout of the data structure for validation
      original_partial_history_filename_allplanes += evt;
      original_partial_history_filename_allplanes += ".out";
      TString changed_partial_history_filename_allplanes = "outfiles/changed_partial_history_allplanes_";//Make a file for each event for a full printout of the data structure for validation
      changed_partial_history_filename_allplanes += evt;
      changed_partial_history_filename_allplanes += ".out";
      TString angular_history_filename = "outfiles/angular_history_";//Make a file for each event for a full printout of the data structure for validation
      angular_history_filename += evt;
      angular_history_filename += ".out";
      ofstream hitsfile_allplanes(hitsfilename_allplanes); //Stream out for hits per channel for all planes
      ofstream original_partial_history_allplanes(original_partial_history_filename_allplanes);//Stream out the partial history of hits, times, and ADCs
      ofstream changed_partial_history_allplanes(changed_partial_history_filename_allplanes);//Stream out the partial history of hits, times, and ADCs
      ofstream angular_history(angular_history_filename);//Stream out the partial history of angles between a given centroid and its surrounding hits, with times and ADCs
      //Get the event from the MC tree
      tree->GetEntry(evt);
		  std::cout << "Event: " << evt << " and ROOT Entry: " << tree->GetEntry(evt) << std::endl;
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
      double adc_mean_col = 0, adc_mean_in0 = 0, adc_mean_in1 = 0;
      for (int iii=0; iii<tp_list.size(); ++iii)//Loop over all of the trigger primitives to get their ADCs
        {
          iterr = timemap.find(tp_list[iii].chanel);//Find the given wire in the timemap
          int tmp_adc_count = 0; tmp_adc_count = timemap[tp_list[iii].chanel].size();//Get the number of hits on that wire
          for (int j = 0; j < tmp_adc_count; j++)//Loop over the hits in that wire
            {
              if (iterr != timemap.end() && timemap[tp_list[iii].chanel].at(j) == tp_list[iii].time_start)//Check that the hit is identical to the one we are investigating
                {
                  //std::cout << "Time map value is: " << timemap[tp_list[iii].chanel].at(j) << " and TP list value is: " << tp_list[iii].time_start << std::endl;
                  adcmap[tp_list[iii].chanel].resize(tmp_adc_count);//Resize the ADC value vector to the appropriate number of hits
                  adcmap[tp_list[iii].chanel].at(j) = tp_list[iii].adc_integral;//Fill the ADC value vector
                  //std::cout << "ADC map value is: " << adcmap[tp_list[iii].chanel].at(j) << " and TP list value is: " << tp_list[iii].adc_integral << std::endl;
                  if (tp_list[iii].chanel>=ColPlStartChnl && tp_list[iii].chanel<=ColPlEndChnl)//If on the collection plane...
                    {
                      adc_mean_col += (double)(tp_list[iii].adc_integral);//Add up all of the contributions from all of the hits
                    }
                  if (/*tp_list[iii].chanel>=IndPl1StartChnl && */tp_list[iii].chanel<=IndPl1EndChnl)//Do the same for the first induction plane...
                    {
                      adc_mean_in0 += (double)(tp_list[iii].adc_integral);
                    }
                  if (tp_list[iii].chanel>=IndPl2StartChnl && tp_list[iii].chanel<=IndPl2EndChnl)//And the second induction plane
                    {
                      adc_mean_in1 += (double)(tp_list[iii].adc_integral);
                    }
                }
            }
        }
      //And now take the averages
      adc_mean_col = (double)(adc_mean_col/tp_list.size());
      adc_mean_in0 = (double)(adc_mean_in0/tp_list.size());
      adc_mean_in1 = (double)(adc_mean_in1/tp_list.size());
      //Remove noisy wires
      for (cursor = wiremap.begin(); cursor!=wiremap.end(); cursor++)
        {
          if (cursor->second > acceptable_maximum_hits_on_wire)
            {
              auto get_wire_key = cursor->first;
              //std::cout << "Wire number: " << cursor->first << " and hits: " << cursor->second << " and get_wire_key: " << get_wire_key << std::endl;
              //std:: cout << "wiremap.at(get_wire_key): " << wiremap.at(get_wire_key) << std::endl;
              wiremap.erase(get_wire_key);
              timemap.erase(get_wire_key);
              adcmap.erase(get_wire_key);
              //cursor=wiremap.find(get_wire_key);
              //wiremap.erase(cursor);
              //if (wiremap.find(get_wire_key)==wiremap.end()){ std::cout << "The wire is now empty" << std::endl; }
              //if (!wiremap.find(get_wire_key)==wiremap.end()){ std::cout << "The wire is NOT empty" << std::endl; }
              //std::cout << "AFTER: Wire number: " << cursor->first << " and hits: " << cursor->second << " and get_wire_key: " << get_wire_key << std::endl;
            }
        }
        
      /*/////////////////////////////// DATA STRUCTURE COMPLETE ///////////////////////////////*/

      ///////////////////////////////////////////////////////////////////////////////////////////
      
      /*/////////////////////////////// TRIGGER STRUCTURE BEGIN ///////////////////////////////*/

      //Create a vector ordered by wire number which holds the total number of hits on surrounding wires
      std::vector<int32_t> surrounding_hits;
      std::vector<double> thetas;//Create a vector to hold all of the angles between the centroid/vertex and the hits on the surrounding
      std::list<double> thetas_list;//Create a LIST to hold all of the same angles between the centroid/vertex and the hits on the surrounding
      std::vector<double> unique_thetas_pos0to90_neg90to180;//Create a vector of the "unique" angles that have similar angles to each other in the 1st/3rd quandrant
      std::vector<double> unique_thetas_pos90to180_neg0to90;//Create a vector of the "unique" angles that have similar angles to each other in the 2ndst/4th quandrant
      std::vector<int32_t> centroid_wires;//Do the same for the centroid wires...
      std::vector<int32_t> surrounding_wires;//..and the same for the surrounding wires...
      std::vector<double> unique_wires_pos0to90_neg90to180;//Create a vector of the "unique" wires assoicated with the similar angles to each other in the 1st/3rd quandrant
      std::vector<double> unique_wires_pos90to180_neg0to90;//Create a vector of the "unique" wires associated with the similar angles to each other in the 2ndst/4th quandrant
      std::vector<int64_t> centroid_times;//...and the centroid times...
      std::vector<int64_t> surrounding_times;//...and the surrounding times...
      std::vector<int64_t> surrounding_adcs;//...and the ADC values...
      std::vector<int32_t> trigger_centroid_wires;//Do the same for the centroid wires..
      std::vector<int64_t> trigger_centroid_times;//...and the times...
      //Loop over the whole detector in a "left-to-right" fashion, going through all the wires (which will act as the centroids' wire)
      for (int32_t wirenumber = 1719; wirenumber < 1720; wirenumber++)
        {
          surrounding_hits.clear();
          //If the wire is empty, move to the next wire
          //std::cout << "wiremap.count(wirenumber): " << wiremap.count(wirenumber) << std::endl;
          if (wiremap.count(wirenumber)==0)
            {
              //std::cout << "The wiremap has no entry for wire number: " << wirenumber << std::endl;
              continue;
            }
          //std::cout << "wiremap.at(wirenumber): " << wiremap.at(wirenumber) << std::endl;
          //Make sure we aren't seeing any noisy wires
          if (wiremap.at(wirenumber) > acceptable_maximum_hits_on_wire)
            {
              //std::cout << "There is likely noise on wire number: " << wirenumber << std::endl;
              continue;
            }
          if (wirenumber>=partial_wire_history_size/2)//Make sure that we can look backward in the TPC by an appropriate number of wires
            {
              //Loop over the wires and fill a vector of
              for (auto i = (wirenumber-partial_wire_history_size/2); i < (wirenumber+partial_wire_history_size/2); i++)
                {
                  surrounding_hits.push_back(wiremap[i]);
                }
              //If there is too little activity (<15 hits across +/- 15 wires from this position), then we know we have <1 hit per wire on average; get out of the loop
              if (std::accumulate(surrounding_hits.begin(),surrounding_hits.end(),decltype(surrounding_hits)::value_type(0)) < partial_wire_history_size) {continue;}
              //Start to loop over the surrounding hits to calculate their angles and such, but only if they are close enough to the vertex in time
              for (auto i = 0; i < surrounding_hits.size(); i++)//Run over the wires (15 of them), which is on the interval [wirenumber-8,wirenumber+7]
                {
                  for (auto ii = 0; ii < surrounding_hits.at(i); ii++)//Run through the hits on the ith wire, which again is actually running from [wirenumber-5,wirenumber+4]
                    {
                      //Run over all of the times for a given entry in the time map
                      for (auto hit = 0; hit < timemap[wirenumber].size(); hit++)//Compute time differences for a given time on the ith wire
                        {
                          //If the absolute value of any of the time differences between the centroid and its surrounding hits are acceptable, then start finding angles/distances
                          //The centroid is on the central wire at the hit time (timemap[wirenumber].at(hit)), and all of the other hits are on other wires (or the same wire, but above/below it)
                          if(abs(timemap[wirenumber].at(hit) - timemap[wirenumber-partial_wire_history_size/2+i].at(ii)) < acceptable_time_diff)
                            {
                              //Avoid taking idempotent differences (the hit's difference with itself on its own wire)
                              if (wirenumber == (wirenumber-partial_wire_history_size/2+i) && abs(timemap[wirenumber].at(hit) - timemap[wirenumber-partial_wire_history_size/2+i].at(ii)) == 0)
                                  {
                                    //std::cout << "I was about to find a difference with myself! Silly me!" << std::endl;
                                    continue;
                                  }
                              //Create a "shell" of a partial history, where wires with only >=3 wires apart are considered to determin angles; this will lead to misses of
                              //very short tracks, but we need to quell the non-smoothly varying nature of arctangent
                              if (abs(wirenumber - (wirenumber-partial_wire_history_size/2+i)) >= partial_wire_history_inner_radius)
                                {
                                  //std::cout << "Centroid wire number: " << wirenumber << " and centroid hit time is: " << timemap[wirenumber].at(hit) << std::endl;
                                  //std::cout << "Leg wire number     : " << wirenumber-partial_wire_history_size/2+i << " and leg hit time is     : " << timemap[wirenumber-partial_wire_history_size/2+i].at(ii) << std::endl;
                                  //Calculate the angle between the centroid and the surrounding hits
                                  double theta = -500;//Initialize the value to a nonphysical one
                                  //Find the angle theta, where the delta_x = delta_wires is the adjacent side of a right triangle, and delta_y = delta_t is the opposite side from theta
                                  //Thus, theta = atan2(delta_t,delta_wires); make sure that we pass atan2 doubles!
                                  theta = (180./PI)*atan2((double)(timemap[wirenumber].at(hit) - timemap[wirenumber-partial_wire_history_size/2+i].at(ii)),(double)((wirenumber - (wirenumber-partial_wire_history_size/2+i))/1.));
                                  thetas.push_back(theta);//Fill the vector of thetas with this new value for all surrounding hits
                                  thetas_list.push_back(theta);//Do the same for the accompanying list
                                  //std::cout << "Theta: " << theta << std::endl;
                                  centroid_wires.push_back(wirenumber);//..etc...
                                  //std::cout << "Wire number: " << wirenumber << std::endl;
                                  centroid_times.push_back(timemap[wirenumber].at(hit));
                                  //std::cout << "Centroid time: " << timemap[wirenumber].at(hit) << std::endl;
                                  surrounding_wires.push_back(wirenumber-partial_wire_history_size/2+i);
                                  //std::cout << "Surrounding wire: " << wirenumber-partial_wire_history_size/2+i << std::endl;
                                  surrounding_times.push_back(timemap[wirenumber-partial_wire_history_size/2+i].at(ii));
                                  //std::cout << "Surrounding time: " << timemap[wirenumber-partial_wire_history_size/2+i].at(ii) << std::endl;
                                  surrounding_adcs.push_back(adcmap[wirenumber-partial_wire_history_size/2+i].at(ii));
                                  //std::cout << "Surrounding ADC: " << adcmap[wirenumber-partial_wire_history_size/2+i].at(ii) << std::endl;
                                  //std::cout << "\n" << std::endl;
                                }
                            }
                        }
                    }
                }
              //Print out the angular history
              for (auto i = 0; i < thetas.size(); i++)
                {
                  //if (centroid_wires.at(i)==1719 && centroid_times.at(i)==5457)
                    //{
                      angular_history << "Event Number: " << evt << std::endl;
                      angular_history << "Centroid Wire Number: " << centroid_wires.at(i) << "\t""Centroid Wire Time: " << centroid_times.at(i) << std::endl;
                      angular_history << "Surrounding Wire No.: " << surrounding_wires.at(i) << "\t""Surrounding Wire T: " << surrounding_times.at(i) << "\t""Theta: " << thetas.at(i) << std::endl;
                      angular_history << "\t""ADC Value: " << surrounding_adcs.at(i) << std::endl;
                      angular_history << " " << std::endl;
                    //}
                }
              //Find the unique angle values and save them
              std::vector<double> unique_average_thetas;
              for (auto i = 0; i < thetas.size(); i++)
                {
                  double tmp_theta = thetas.at(i);//Same the temporary value for comparisons
                  thetas.at(i) = -1000.;//Overwrite and set to unphysical value, from top to bottom; can't erase, otherwise thetas.size changes
                  //Now make a temporary vector of sorts which will save all of the similar angles to one vector, using the (former) ith element
                  //of the thetas vector to search for similar angles within the angular_tolerance
                  std::vector<decltype(thetas)::value_type> copy_thetas_pos0to90_neg180to90;
                  std::vector<decltype(thetas)::value_type> copy_thetas_pos90to180_neg90to0;
                  //Now, do the search for two quadrants on [0,90) and [-180,-90)
                  std::copy_if(thetas.begin(),thetas.end(),std::back_inserter(copy_thetas_pos0to90_neg180to90),
                              [tmp_theta,angular_tolerance](double unique_theta_pos0to90_neg180to90) -> bool
                              { return
                                ((unique_theta_pos0to90_neg180to90>=0. && unique_theta_pos0to90_neg180to90<90.) || (unique_theta_pos0to90_neg180to90>=-180. && unique_theta_pos0to90_neg180to90<-90.))
                                 &&
                                (std::abs(tmp_theta - unique_theta_pos0to90_neg180to90) < angular_tolerance);
                              });
                  //Now, do the search for two quadrants on [90,180) and [-90,0)
                  std::copy_if(thetas.begin(),thetas.end(),std::back_inserter(copy_thetas_pos0to90_neg180to90),
                              [tmp_theta,angular_tolerance](double unique_theta_pos90to180_neg90to0) -> bool
                              { return
                                ((unique_theta_pos90to180_neg90to0>=90. && unique_theta_pos90to180_neg90to0<180.) || (unique_theta_pos90to180_neg90to0>=-90. && unique_theta_pos90to180_neg90to0<00.))
                                 &&
                                (std::abs(tmp_theta - unique_theta_pos90to180_neg90to0) < angular_tolerance);
                              });
                  std::cout << "i = " << i << " and thetas.at(i) = " << tmp_theta << std::endl;
                  std::cout << "On [0,90) and [-180,-90): " << std::endl;
                  for (double unique_theta_pos0to90_neg180to90 : copy_thetas_pos0to90_neg180to90)
                    std::cout << unique_theta_pos0to90_neg180to90 << ' ';
                  std::cout << '\n';
                  std::cout << "On [90,180) and [-90,0): " << std::endl;
                  for (double unique_theta_pos90to180_neg90to0 : copy_thetas_pos90to180_neg90to0)
                    std::cout << unique_theta_pos90to180_neg90to0 << ' ';
                  std::cout << '\n';
                  //Now that we have a new copy_thetas_pos0to90_neg180to90 vector full of similar angles, we should change those values in the original thetas
                  //vector to make sure they don't get searched again as we progress through the i loop over thetas elements
                  for (auto ii = i+1; ii< thetas.size(); ii++)//Start the iterator after the current ith entry
                    {
                      for (auto iii = 0; iii < copy_thetas_pos0to90_neg180to90.size(); iii++)//Loop through the copy_thetas_pos0to90_neg180to90 elements
                        {
                          if (copy_thetas_pos0to90_neg180to90.at(iii) == thetas.at(ii))//Check if they match any of their parents
                            {
                              //If they do, change their values to be outside the angular_tolerance so that they aren't searchable
                              thetas.at(ii) = -1000. - angular_tolerance - 1.;
                            }
                        }
                      for (auto iii = 0; iii < copy_thetas_pos90to180_neg90to0.size(); iii++)//Loop through the copy_thetas_pos0to90_neg180to90 elements
                        {
                          if (copy_thetas_pos90to180_neg90to0.at(iii) == thetas.at(ii))//Check if they match any of their parents
                            {
                              //If they do, change their values to be outside the angular_tolerance so that they aren't searchable
                              thetas.at(ii) = -1000. - angular_tolerance - 1.;
                            }
                        }
                    }
                  //If there are more than the acceptable number of angles (>4), then make an average, and pass this to the unique_average_thetas_all
                  //vector; this vector will tell us the number of unique angles we have in a given partial history, and its size will allow us to trigger
                  if (copy_thetas_pos0to90_neg180to90.size()>acceptable_similar_angles)
                    {
                      unique_average_thetas.push_back(std::accumulate(copy_thetas_pos0to90_neg180to90.begin(),
                                                                      copy_thetas_pos0to90_neg180to90.end(),
                                                                      decltype(copy_thetas_pos0to90_neg180to90)::value_type(0))
                                                                      /copy_thetas_pos0to90_neg180to90.size());
                    }
                   if (copy_thetas_pos90to180_neg90to0.size()>acceptable_similar_angles)
                    {
                      unique_average_thetas.push_back(std::accumulate(copy_thetas_pos90to180_neg90to0.begin(),
                                                                      copy_thetas_pos90to180_neg90to0.end(),
                                                                      decltype(copy_thetas_pos90to180_neg90to0)::value_type(0))
                                                                      /copy_thetas_pos90to180_neg90to0.size());
                    }
                  copy_thetas_pos0to90_neg180to90.clear();
                  copy_thetas_pos90to180_neg90to0.clear();           
                }
              std::cout << "The number of uniqe angle are: " << unique_average_thetas.size() << std::endl;
              std::cout << "The unique angles are: " << std::endl;
              for (auto i = 0; i < unique_average_thetas.size(); i++)
                {
                  std::cout << unique_average_thetas.at(i) << "\t";
                }
              std::cout << " " << std::endl;
              
              
              /*std::copy_if(thetas.begin(),thetas.end(),std::back_inserter(unique_thetas_pos0to90_neg90to180),
                              [](double unique_theta) 
                              { return
                                (unique_theta>=0. && unique_theta<90.) || (unique_theta>=-180. && unique_theta<-90.)
                                 &&
                                (abs(theta.at(i) - unique_theta) < angular_tolerance);
                              });
              std::copy_if(thetas.begin(),thetas.end(),std::back_inserter(unique_thetas_pos90to180_neg0to90),
                           [](double unique_theta) 
                           { return (unique_theta>=90. && unique_theta<180.) || (unique_theta>=-90. && unique_theta<0.);});
              //std::sort(unique_thetas_pos0to90_neg90to180.begin(),unique_thetas_pos0to90_neg90to180.end());
              std::cout << "Unique thetas on [0,90) and [-180,-90): " << std::endl;
              for (double unique_theta : unique_thetas_pos0to90_neg90to180)
                  std::cout << unique_theta << std::endl;
              std::cout << "Unique thetas on (90,180) and [-90,0): " << std::endl;
              for (double unique_theta : unique_thetas_pos90to180_neg0to90)
                  std::cout << unique_theta << std::endl;
              std::cout << "The size of the thetas vector is: " << thetas.size() << std::endl;
              std::cout << "The size of the unique thetas vector on [0,90) and [-180,-90) is: " << unique_thetas_pos0to90_neg90to180.size() << std::endl;
              std::cout << "The size of the unique thetas vector on (90,180) and [-90,0) is:  " << unique_thetas_pos90to180_neg0to90.size() << std::endl;
              std::cout << "Unique thetas from vector on [0,90) and [-180,-90): " << std::endl;
              for (auto ii = 0; ii < unique_thetas_pos0to90_neg90to180.size(); ii++)
                {
                  std::cout << unique_thetas_pos0to90_neg90to180.at(i) << std::endl;
                }
              std::cout << "Unique thetas from vector on (90,180) and [-90,0): " << std::endl;
              for (auto ii = 0; ii < unique_thetas_pos90to180_neg0to90.size(); ii++)
                {
                  std::cout << unique_thetas_pos90to180_neg0to90.at(i) << std::endl;
                }*/
              

              surrounding_hits.clear();//Clear the surrounding hits list
              thetas.clear();//Clear their assoicated theta values..
              centroid_wires.clear();//...and the same for the rest of the vectors
              surrounding_wires.clear();
              surrounding_times.clear();
              surrounding_adcs.clear();
              unique_wires_pos90to180_neg0to90.clear();
              unique_thetas_pos90to180_neg0to90.clear();
              unique_wires_pos0to90_neg90to180.clear();
              unique_thetas_pos0to90_neg90to180.clear();
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
      
      //********** BEGIN DRAWING ALL EVENT DISPLAYS AND TRIGGER CANDIDATE BOXES **********
      
      //********** END DRAWING ALL EVENT DISPLAYS AND TRIGGER CANDIDATE BOXES **********
      
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