//Code written by Daisy Kalra (June 20, 2022) dkalra@nevis.columbia.edu                                                                     
// Binary decoder to decode SN data, calculate TPs and write TPs to a text file.                                                            
//To run this code:                                                                                                                         
// g++ -o bin ReadBinary_chnlMap.cpp                                                                                                        
// ./bin NameOfSNBinaryFile.ubdaq CrateNumber OutputTxtFileToSaveTPs                                                                        


#include <iostream>
#include <fstream>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <map>
#include <tuple>
#include <vector>
#include <typeinfo>

using namespace std;

struct ForChannelMap {
  int crate = {0};
  int femchmap   = {0};
  int ch    = {0};
  int LArWire = {0};

  ForChannelMap(int crate11, int femchmap11, int ch11, int LArWire11)
  {
    crate = crate11;
    femchmap = femchmap11;
    ch = ch11;
    LArWire = LArWire11;
  }



};


struct PassInfoToStitching {
  /*  uint32_t frame4 = {0};
  uint32_t fem   = {0};
  uint32_t mappedchannel  = {0};
  uint16_t timetick  = {0};
  int      tot   = {0};
  uint64_t amp   = {0};
  uint64_t intgrl= {0};
  */
  //Changes for converting int's to string 

  string frame4 = {0};
  string fem   = {0};
  string mappedchannel  = {0};
  string timetick  = {0};
  string      tot   = {0};
  string amp   = {0};
  string intgrl= {0};

  //  PassInfoToStitching(uint32_t fr4, uint32_t fm, uint32_t mc, uint16_t tt, int tot1, uint64_t am, uint64_t in)
  //Changes for converting int's to string  
  PassInfoToStitching(string fr4, string fm, string mc, string tt, string tot1, string am, string in)


  {

    frame4 = fr4;
    fem = fm;
    mappedchannel = mc;
    timetick = tt;
    tot = tot1;
    amp = am;
    intgrl = in;

  }


};



int returnWire(int fcrate, int ffem, int fch, std::vector<ForChannelMap> fholdChMapIds){
  int mappedwire;
  for (int i=0; i<fholdChMapIds.size(); i++){
    std::map<std::tuple<int,int,int>, int> multimap;
    if(fholdChMapIds[i].crate==fcrate and fholdChMapIds[i].femchmap == ffem and fholdChMapIds[i].ch == fch) {
      std::tuple<int,int,int> key(fholdChMapIds[i].crate, fholdChMapIds[i].femchmap, fholdChMapIds[i].ch);
      int val = fholdChMapIds[i].LArWire;
      multimap[key] = val;
      mappedwire = multimap[key];
      return mappedwire;
    }
  }}

int main(int argc, char** argv){

  //For channel mapping 
  int CRATE=strtol(argv[2], nullptr, 0); //Change for SEB
  std::vector<ForChannelMap> holdChMapIds;
  std::ifstream mapFile;
  mapFile.open("chmapnew.txt");
  std::ofstream outputFile;
  //  outputFile.open("tpinfo.txt");
  outputFile.open(argv[3]);

  string plane;
  int LArWire;
  int mwire;
  int crate, femchmap, ch;

  int mappedwire;
  if(mapFile.is_open() && !mapFile.eof()) {
    while(mapFile >> plane >> LArWire >> crate >> femchmap >> ch ){  // FemId >> ChnlId){                                                         
      //      holdChMapIds.push_back({crate,femchmap,ch,LArWire});
      holdChMapIds.emplace_back(crate,femchmap,ch,LArWire);
}
  }
  mapFile.close();

  //For passing infor to stitching code
  //  const PassInfoToStitching& input_tp = {0};
  std::vector<PassInfoToStitching> tp_list ;

  //Read binary code starts
  int k=-1;
  int femHdrCount=0;
  uint32_t frame = 0;
  uint32_t minFrame;
  int FrameCounter = 0;
  uint32_t frame1, frame2, frame3, frame4, framebitsToskip;
  uint32_t fem, channel, mappedchannel;
  uint16_t timetick=0;
  int tot;
  uint64_t adcval, amp, intgrl; // intgrlval;
  std::ifstream binFile;
  bool doincrement=false;


  //  std::ofstream WriteToBinFile;
  //std::unique_ptr<uint16_t[]> bufferTP;
  // std::streamsize size=1000;
  //    char* bufferTP = new char[size];
    //  binFile.open("2StreamTest-SN-seb03-2021_10_11_22_18_0-0028552-00000.ubdaq", std::ios::binary);

  //  binFile.open("2StreamTest-SN-seb03-2021_10_11_23_23_53-0028554-00000.ubdaq", std::ios::binary);
  binFile.open(argv[1], std::ios::binary);


  //WriteToBinFile.open("TP.bin",std::ios::binary);

  if( !binFile.is_open() ){
    std::cerr << "ERROR: Could not open file " << std::endl;
    return 0;
  }

 
  while( binFile.peek() != EOF ){
    uint32_t word32b;
    binFile.read( reinterpret_cast<char*>(&word32b), sizeof(word32b) );
    //  std::cout.flags ( std::ios::uppercase );
    std::cout.setf ( std::ios::hex, std::ios::basefield );  // set hex as the basefield
    std::cout.setf ( std::ios::showbase ); // activate showbase    i.e with prefix 0x 

    uint16_t first16b = word32b & 0xffff; //right 16 bit word
    uint16_t last16b = (word32b>>16) & 0xffff; // left 16 bit word 
  
    if(word32b == 0xffffffff) {
      femHdrCount=1;
      doincrement=true;
      }

    else if (word32b  == 0xe0000000){
      cout << "End of frame*******************" << endl;
      if(frame4==minFrame+2){
	//Pass the tp_list to next stitching code and then clear the list, for now checking the size of tp_list here and then clearing the tp_list
	// --> Need to put interfacing code here

	cout << "Size of tp_list vector at the end of 3 frames : " << std::dec << tp_list.size() << endl;
	FrameCounter=0;
	tp_list.clear();

      }

    }

    else {

      if(doincrement==true){ //we need this boolean so as to stop FEM cntr after evaluating frame number.
	femHdrCount+=1;
       
	if (femHdrCount==5){ // FEM frame number
	  frame = (first16b & 0xfff);
	  frame1 = (last16b>>6 & 0x3f); 
	  framebitsToskip = (last16b & 0x3f);   // last 6 bits of FEM frame number
	}

	if (femHdrCount==8){ //ROI frame number
	  if(first16b>>12 == 0x1){
	    frame2=(first16b>>6) & 0x3f;
	    //Take care of roll over of bits
	    if ((framebitsToskip-frame2)>=0){
	      frame3 = (frame<<12)+(frame1<<6)+(frame2);
	      frame4 = (frame3 & 0xffffff);
	      if(frame4!=0){
	      FrameCounter+=1;
	      }
	      if(FrameCounter==1){                                                                                                                       
	        minFrame = frame4;                                                                                                                      
		cout << std::dec << minFrame << endl;
		 }                                                                                                                                        
	   
	      //std::cout << "RH frame :****** " << std::dec << (frame3 & 0xffffff) << std::endl;
	      //std::cout << "RH frame :****** " << std::dec << frame4 << std::endl;

		  }
	    else if ((framebitsToskip-frame2)<0){
	    frame3 = (frame<<12)+(frame1<<6)+(frame2);
	    std::cout << "Roll Over" << std::endl;
	    //Subtract 2^6-1 from frame number to take care of roll over
	    //	    std::cout << "RH frame :****** " << std::dec << (frame3 & 0xffffff)-63 << std::endl;
	    // std::cout << "RH frame :****** " << std::dec << (frame4)-63 << std::endl;
	    }

	    k+=1;
	    if (k!=(frame3 & 0xffffff)){
	      std::cout << "************* Missing frame **********" << std::endl;
	      // std::cout << k << " , " << (frame3 & 0xffffff) << std::endl; 
	      k=(frame3 & 0xffffff);
	    }
	    
	    doincrement=false;
	    femHdrCount=0;
	    
	  }

	  else if(last16b>>12 == 0x1){
	    frame2=(last16b>>6) & 0x3f; // skip first 6 bits and then take 6 bits to count
	    if ((framebitsToskip-frame2)>=0){
	      frame3 = (frame<<12)+(frame1<<6)+(frame2);
	      //std::cout << "LH frame :***** " << std::dec << frame4 << std::endl; // (frame3 & 0xffffff) << std::endl;
            }

	    if ((framebitsToskip-frame2)<0){
	      std::cout << "Roll Over" <<std::endl;
	      std::cout << "diff. : " << (framebitsToskip-frame2)<< " and dec is: " << std::dec <<  (framebitsToskip-frame2) << std::endl;
	      frame3 = (frame<<12)+(frame1<<6)+(frame2);
	      frame4 = (frame3 & 0xffffff);
	      if(frame4!=0){
		FrameCounter+=1;
	      }
	      if(FrameCounter==1){
                minFrame = frame4;
                cout <<std::dec << minFrame <<endl;

	      }

	      //    std::cout << "LH frame :****** " << std::dec << (frame4)-63 << std::endl;// (frame3 & 0xffffff)-63 << std::endl;
	    } 
	    k+=1;
	    if (k!=(frame3 & 0xffffff)){
	      std::cout << "************* Missing frame **********" << std::endl;
	      k=(frame3 & 0xffffff);
            }
	    doincrement=false;
	    femHdrCount=0;
	  }

	} //close femhdrcnt == 8

	} //close do increment loop

      if ((last16b >>8 == 0xf1) and (first16b == 0xffff)){
	fem =(last16b&0x1f);
	//std::cout << "FEM number : " << std::dec << fem << std::endl;
      }

      if(first16b>>12 == 0x1){
	channel = (first16b & 0x3f);
	//	std::cout <<  " Channel Number: " << std::dec << channel << std::endl;
	mappedchannel = returnWire(CRATE,fem,channel,holdChMapIds);
	//std::cout <<  " Channel Number: " << std::dec << channel << " , " << mappedchannel << std::endl;

	adcval=0;
	tot=0;
	intgrl=0;
	amp=0;
      }

      else if (first16b>>14 == 01){
	if(tot!=0 and amp!=0 and intgrl!=0){
	  // mappedchannel = returnWire(CRATE,fem,channel,holdChMapIds);
	  std::cout <<"************* First 16 bits loop *********" << std::endl;                 
	  std::cout << "Frame: " <<   std::dec << (frame3 & 0xffffff) << std::endl;
	  std::cout << "FEM number : " << std::dec << fem << std::endl;
	  std::cout <<  " Channel Number: " << std::dec << channel << std::endl;
	  std::cout << "ChannelMap : "<< CRATE << " , " << fem << " , " << channel << std::endl;
	  //mappedchannel = returnWire(CRATE,fem,channel,holdChMapIds);
	  std::cout << "mapped wire: " << std::dec << mappedchannel << std::endl;
	  std::cout << "Final adc val: " << std::dec  << amp << std::endl;                                               
	  std::cout << "tot: " <<  tot << std::endl;                                                                     
	  std::cout << "intgrl: " << std::dec << intgrl << std::endl;                                                    
	  std::cout << "time: " << std::dec << timetick << std::endl;    

   outputFile << frame4 << "\t" << fem <<  "\t" << mappedchannel << "\t" << timetick << "\t" << amp << "\t" << tot << "\t" << intgrl << "\n";

   //   tp_list.push_back({std::to_string(frame4),std::to_string(fem),std::to_string(mappedchannel),timetick,amp,tot,intgrl});
  
   //Changes for converting int's to string  
   tp_list.emplace_back(std::to_string(frame4),std::to_string(fem),std::to_string(mappedchannel),std::to_string(timetick),std::to_string(amp),std::to_string(tot),std::to_string(intgrl));



	  cout << "Size: " << tp_list.size() << endl;
	  //	  cout << tp_list[0].PassFrame << endl;

	  cout << "String test : " << tp_list[0].frame4 << endl;
	  //Verified conversion of int to string 
	  /*
	  cout << typeid(frame4).name() << endl;
	  cout << typeid(tp_list[0].frame4).name() << endl;
	  cout << typeid(tp_list[0].fem).name() << endl;
	  cout << typeid(tp_list[0].mappedchannel).name() << endl;
	  cout << typeid(tp_list[0].timetick).name() << endl;
	  cout << typeid(tp_list[0].amp).name() << endl;
	  cout << typeid(tp_list[0].tot).name() << endl;
	  cout << typeid(tp_list[0].intgrl).name() << endl;
	  */ //if(FrameCounter==1){

	  // minFrame = frame4;
	  // }
	  

	}



	timetick =  first16b & 0x3fff ;
	//std::cout << "time first" << std::dec << timetick << std::endl;                                              

	adcval=0;
	tot=0;
	intgrl=0;
	amp = 0;
      }

      else if (first16b>>12 == 0x2){
	tot+=1;
	adcval=(first16b & 0xfff);
	if (adcval > amp){
	  amp= adcval; //(first16b & 0xfff);                                                                           
	}

	intgrl += (first16b & 0xfff);
	//std::cout << "firstloop check adcavl 0x2:  " << amp << " tot: " << tot << " integral: " << intgrl << std::endl; 

      }
      else if (first16b>>12 == 0x3){
	tot+=1;

	adcval=(first16b & 0xfff);
	if (adcval > amp){
	  amp= adcval; //(first16b & 0xfff);                                                                           
	}
	intgrl += (first16b & 0xfff);
	//std::cout << "firstloop check adcavl 0x3:  " << amp << " tot: " << tot << " integral: " << intgrl << std::endl; 
      }




       if(last16b>>12 == 0x1){
	channel = (last16b & 0x3f);
	mappedchannel = returnWire(CRATE,fem,channel,holdChMapIds);
	//std::cout <<  " Channel Number: " << std::dec << channel << " , " << mappedchannel << std::endl;

	//std::cout <<  " Channel last: " << std::dec << channel << std::endl;

	adcval=0;
	tot=0;
	intgrl=0;
	amp=0;
	//timetick=0;                                                                                                                      
      }

       else if (last16b>>14 == 01){
	 if(tot!=0 and amp!=0 and intgrl!=0){
	   //mappedchannel = returnWire(CRATE,fem,channel,holdChMapIds);
	   std::cout <<"************* Last 16 bits loop *********" << std::endl;                                      
	   std::cout << "Frame: " <<   std::dec << (frame3 & 0xffffff) << std::endl;
	   std::cout << "FEM number : " << std::dec << fem << std::endl;
	   std::cout <<  " Channel Number: " << std::dec << channel << std::endl;
	   std::cout << "ChannelMap : "<< CRATE << " , " << fem << " , " << channel << std::endl;
	   //mappedchannel = returnWire(CRATE,fem,channel,holdChMapIds);
	   std::cout << "mapped wire: " << std::dec << mappedchannel << std::endl;
	   std::cout << "Final adc val: " << std::dec  << amp << std::endl;                                               
	   std::cout << "tot: " <<  tot << std::endl;                                                                     
	   std::cout << "intgrl: " << std::dec << intgrl << std::endl;                                                    
	   std::cout << "time: " << std::dec << timetick << std::endl; 
	   outputFile << frame4 << "\t" << fem <<  "\t" << mappedchannel << "\t" << timetick << "\t" << amp << "\t" << tot << "\t" << intgrl << "\n";

	   //	   tp_list.push_back({std::to_string(frame4),fem,mappedchannel,timetick,amp,tot,intgrl});
	   //	   tp_list.emplace_back(std::to_string(frame4),fem,mappedchannel,timetick,amp,tot,intgrl);
	   //Changes for converting int's to string  	  
 tp_list.emplace_back(std::to_string(frame4),std::to_string(fem),std::to_string(mappedchannel),std::to_string(timetick),std::to_string(amp),std::to_string(tot),std::to_string(intgrl));


	   cout << "Size: " << tp_list.size() << endl;


	 }
	 timetick =  last16b & 0x3fff ;
	 // std::cout << "time last " << std::dec << timetick << std::endl; 
	 adcval=0;
	 tot=0;
	 intgrl=0;
	 amp=0;
       }
       else if (last16b>>12 == 0x2){
	 tot+=1;
	 adcval=(last16b & 0xfff);
	 if (adcval > amp){
	   amp= adcval; //(first16b & 0xfff);                                                                          \
                                                                                                                          
	 }
	 intgrl += (last16b & 0xfff);
       }
       else if (last16b>>12 == 0x3){
	 tot+=1;
	 adcval=(last16b & 0xfff);
	 if (adcval > amp){
	   amp= adcval; //(first16b & 0xfff);                                                                          \
                                                                                                                          
	 }
	 intgrl += (last16b & 0xfff);
       }


    

      else{
	continue;      
}

    }
  }//closed while loop on reading a binary file 
  
}
