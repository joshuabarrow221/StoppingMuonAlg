//Binary decoder that decodes supernova binary files and calculates trigger primitives
//Developed by Daisy Kalra (dkalra@nevis.columbia.edu) on May 18 2022.
//Followed the data format defined in sbn doc db 17726
//https://sbn-docdb.fnal.gov/cgi-bin/sso/RetrieveFile?docid=17726&filename=SBND_TPC_Data_Format_April_24_2020.pdf&version=1


#include <iostream>
#include <fstream>
#include <stdint.h>
#include <string.h>
#include <math.h>
using namespace std;

int main(){

  int k=-1;
  int femHdrCount=0;
  uint32_t frame = 0;
  uint32_t frame1, frame2, frame3, frame4, framebitsToskip;
  uint32_t fem, channel;
  uint16_t timetick=0;
  int tot;
  uint64_t adcval, amp, intgrl;
  std::ifstream binFile;
  //  std::ofstream WriteToBinFile;
  //std::unique_ptr<uint16_t[]> bufferTP;
  bool doincrement=false;
 

    //  binFile.open("2StreamTest-SN-seb03-2021_10_11_22_18_0-0028552-00000.ubdaq", std::ios::binary);
  binFile.open("2StreamTest-SN-seb03-2021_10_11_23_23_53-0028554-00000.ubdaq", std::ios::binary);


  // WriteToBinFile.open("TP.bin",std::ios::binary);

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
	      std::cout << "RH frame :****** " << std::dec << (frame3 & 0xffffff) << std::endl;
            }
	    else if ((framebitsToskip-frame2)<0){
	    frame3 = (frame<<12)+(frame1<<6)+(frame2); 
	    //Subtract 2^6-1 from frame number to take care of roll over
	    std::cout << "RH frame :****** " << std::dec << (frame3 & 0xffffff)-63 << std::endl;
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
	      std::cout << "LH frame :***** " << std::dec << (frame3 & 0xffffff) << std::endl;
            }

	    if ((framebitsToskip-frame2)<0){
	      std::cout << "diff. : " << (framebitsToskip-frame2)<< " and dec is: " << std::dec <<  (framebitsToskip-frame2) << std::endl;

	      frame3 = (frame<<12)+(frame1<<6)+(frame2);
	      std::cout << "LH frame :****** " << std::dec << (frame3 & 0xffffff)-63 << std::endl;
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
	std::cout << "FEM number : " << std::dec << fem << std::endl;
      }

      if(first16b>>12 == 0x1){
	channel = (first16b & 0x3f);
	std::cout <<  " Channel Number: " << std::dec << channel << std::endl;

	adcval=0;
	tot=0;
	intgrl=0;
	amp=0;
      }

      else if (first16b>>14 == 01){
	if(tot!=0 and amp!=0 and intgrl!=0){

	  std::cout <<"************* First 16 bits loop *********" << std::endl;                                
	  std::cout << "Final adc val: " << std::dec  << amp << std::endl;                                        
	  std::cout << "tot: " <<  tot << std::endl;                                                             
	  std::cout << "intgrl: " << std::dec << intgrl << std::endl;                                               
	  std::cout << "time: " << std::dec << timetick << std::endl;    
	}
	timetick =  first16b & 0x3fff ;
	std::cout << "time first" << std::dec << timetick << std::endl;                                          

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
	std::cout <<  " Channel last: " << std::dec << channel << std::endl;
	adcval=0;
	tot=0;
	intgrl=0;
	amp=0;
	//timetick=0;                                                                                       
      }

       else if (last16b>>14 == 01){
	 if(tot!=0 and amp!=0 and intgrl!=0){
	   std::cout <<"************* Last 16 bits loop *********" << std::endl;                                
	   std::cout << "Final adc val: " << std::dec  << amp << std::endl;                                   
	   std::cout << "tot: " <<  tot << std::endl;                                                           
	   std::cout << "intgrl: " << std::dec << intgrl << std::endl;                                           
	   std::cout << "time: " << std::dec << timetick << std::endl; 
	 }
	 timetick =  last16b & 0x3fff ;
	 std::cout << "time last " << std::dec << timetick << std::endl; 
	 adcval=0;
	 tot=0;
	 intgrl=0;
	 amp=0;
       }
       else if (last16b>>12 == 0x2){
	 tot+=1;
	 adcval=(last16b & 0xfff);
	 if (adcval > amp){
	   amp= adcval; //(first16b & 0xfff);                                                
                                                                                                                  
	 }
	 intgrl += (last16b & 0xfff);
       }
       else if (last16b>>12 == 0x3){
	 tot+=1;
	 adcval=(last16b & 0xfff);
	 if (adcval > amp){
	   amp= adcval; //(first16b & 0xfff);                                                              
                                                                                                                    
	 }
	 intgrl += (last16b & 0xfff);
       }


    

      else{
	continue;      
}

    }
  }//closed while loop on reading a binary file 
  
}
