#Read TPs from manually generated TP file and stitch TPs to form a drift region {2.3ms} worth 4600 time ticks, reading 3 frames at a time from the uBooNE data runs. Channel mapping is also implemented here.   
#D.Kalra (dkalra@nevis.columbi.edu) (dk3172@columbia.edu) (October 25, 2021)

#import matplotlib.pyplot as plt
#import matplotlib
#import numpy as np
#import pandas as pd
#add data transfer systems 
#import zmq
import json
import time
#import pandas as pd
#import cProfile
#port = 6665
import sys

f=open(sys.argv[1],"r")
cratenum=2

outf=open(sys.argv[2],"w")

scale = 16 ## equals to hexadecimal
num_of_bits = 16
tot = 0
intgrl = 0
intgrlN = 0
tpcnt = 0
hdrcnt = 0
amp = 0
frm = 0
frmb = 0
femm=0
framelist=[]
tplistintCol=[]
chlarchlist=[]
larchnlNum = 0
larchnlNumInd = 0
larchnlNumCol = 0
tplistinduction=[]
tplistcollection = []
min1=1
tmin=0
tmax=3200
tdrift=4600
tdiff=tmax-tmin
thisFrameList=[]
td=0
min1p=0
frmcntby0 = 0 
class ChannelMap:
    def __init__(self, mapfile):
        self.mapfile = mapfile
        self.table_readout2larsoft = {} # The keys are the trio crate, FEM, channels                                                  
        self.table_larsoft2readout = {} # The keys are plane, wire number                                                                 
        with open(mapfile) as inf:
            for line in inf.readlines():
                crate, fem, ch, plane, wire = line.split()
                #self.table_readout2larsoft[(int(crate), int(fem), int(ch))] = int(wire)# [plane, int(wire)]                               
                self.table_readout2larsoft[(int(crate), int(fem), int(ch))] = int(wire)
                self.table_larsoft2readout[(plane, int(wire))] = [int(crate), int(fem), int(ch)]
    def CrateFEMCh2PlaneWire(self, crate, fem, ch):
    #def CrateFEMCh2PlaneWire(self, crate, ch):                                                                                      
            
        try:
                #mydict = self.table_readout2larsoft[(int(crate), int(fem), int(ch))]                                                     
                #return list(mydict.keys())                                                                                             
                return self.table_readout2larsoft[(int(crate), int(fem), int(ch))]
        except KeyError:
            return 0 #["", -1]                                                                                                           

    def PlaneWire2CrateFEMCh(self, plane, wire):
        try:
            return self.table_larsoft2readout[(plane, int(wire))]
        except KeyError:
            return [-1, -1, -1]

chMap = ChannelMap("ChnlMap.txt")
cratenum=2
framelistfull = []
framelist2 = 0
tdiffP2=tdiff
tdiffP3=tdiff
frmcnt=0
frmstep=0

def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary
            

now = time.time()

#pr.enable()

print("start time :", now)
for r in range(25):
    #start_time = time.time()
    #print("start time1 :", start_time)
    for l in f:
        words = l.split()
        NumOfWords = len(words)
        for w in range(0,NumOfWords):
            wf = l.split()[w]
            wrh = l.split()[w][4:]
            wlh = l.split()[w][0:4]
            wrb = bin(int(wrh, scale))[2:].zfill(num_of_bits)
            wlb = bin(int(wlh, scale))[2:].zfill(num_of_bits)
            #wrd = int(wrh, 16)
            #wld = int(wlh, 16)
            #print("Wrb: "+str(wrb[0:2]))
            #print("Wlb: "+str(wlb[0:2]))
            if (wf[0] == "F" or wrh[0]=="1" or wlh[0]=="1"):
                hdrcnt += 1
                #if hdrcnt == 1:
                    #print("hdr1: "+str(wf))
                if hdrcnt == 5:
                    #print("wf 5 hdr: "+str(wf))
                    femheader1=wrb[4:]
                    femheader2=wlb[4:]
                  
                if hdrcnt == 8:
                    #print("wf is :"+str(wf))
                    if (wrh[0] == "1"):
                        chnlheader=[wlh[1:],wrh[1:]]
                        frame2=int(wrb[-12:-6],2)
                        chnlheader_b=wrb[-12:-6] #[10:]                                                                                                            
                        frameword_b=femheader1+femheader2[0:6]+chnlheader_b
                        frame=int((frameword_b),2)
                        framelist.append(frame)
                        min1p=min(framelist)+frmstep

            if (wf[0:2] == "F1" and wf[4:8] == "FFFF"):
                femm=int(wlb[-5:], 2)


            elif wf == "E0000000":
                hdrcnt = 0
                #print("TP list len at EOF" + str(len(tplistcollection)))
                frend=time.time()
                #print("Frameend: "+str(frend))

            else:
                #print("Check len of framelist: "+str(framelist))
                if(int(len(framelist))>0):
                    for frm in range(min1p, min1p+3):  #if min1=1, 1,2,3 not to 4
                        if wrh[0] == "1":
                            channel = int(wrb[-6:],2)
                            #channellist.append(channel)
                            larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                            tpcnt = 0
                            tot = ""
                            intgrl = ""
                            intgrlN = ""
                            amp = ""
                            nsamps = ""
                        if wlh[0] == "1":
                            channel = int(wlb[-6:],2)
                            #channellist.append(channel)
                            larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))

                            tpcnt = 0
                            tot = ""
                            intgrl = ""
                            intgrlN = ""
                            amp = ""
                        if wrb[0:2] == "01":
                            timetick=int(wrb[2:],2)
                        if wlb[0:2] == "01":
                            #print(wlb)
                            timetick=int(wlb[2:],2)
                            #timelist.append(timetick)
                        if wlh[0] == "C":
                            tpcnt +=1
                        if tpcnt == 1:
                            tot = int(wlh[1:],16)
                        if tpcnt == 3:
                            intgrl = str(wlh[1:]) #str(int(str(wlh[1:])+intgrl,16)) #str(int(str(wlh[1:])+intgrl,16))
                        if wrh[0] == "C":
                            tpcnt +=1
                        if tpcnt == 2:
                            #print("tpcnt2: "+str(wrh) + " full: " + str(wf))
                            amp = str(int(wrh[1:],16))
                        if tpcnt == 4:
                            intgrl = str(int(intgrl+str(wrh[1:]),16)) #str(wrh[1:]) #str(wrh[1:])
                            tplistinduction.append([frame, femm, int(larchnlNum), timetick, int(intgrl), int(tot), int(amp)])
                            
                            tpcnt = 0                                                               
                            tot = ""                                                                                
                            intgrl = ""                                                                             
                            intgrlN = ""                                                                            
                            amp = ""                                                                                
                            nsamps = ""  
                
#f.close()

#with open('output.txt', 'w') as fInd:     
json.dump(tplistinduction, outf)

