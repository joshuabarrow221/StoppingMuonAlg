#Read TPs from manually generated TP file and stitch TPs to form a drift region {2.3ms} worth 4600 time ticks, reading 3 frames at a time from the uBooNE data runs. Channel mapping is also implemented here.   
#D.Kalra (dkalra@nevis.columbi.edu) (dk3172@columbia.edu) (October 25, 2021)

#import matplotlib.pyplot as plt
#import matplotlib
import numpy as np
#add data transfer systems 
import zmq
import json
import time
#import pandas as pd
import cProfile
port = 6665

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)

#Command to convert binary to hex-dump file: hexdump -v -e '8/4 "%08X ""\n"' BINARYFILE 

#f=open("testnominal_folded28554_head_threeframes", "r")
#f=open("testnominal_folded28554_25frames", "r")

pr = cProfile.Profile()
#pr.enable()
f=open("testnominal_folded28554_head_testmore25frames", "r")

cratenum=2

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
channellist=[]
timelist=[]
mainlist=[]
femlist=[]
tplistamp=[]
tplisttot=[]
tplistint=[]
tplistintInd=[]
tplistintCol=[]
x=[]
y=[]
z=[]
chlarchlist=[]
larchnlNum = 0
larchnlNumInd = 0
larchnlNumCol = 0
min1=1
tmin=0
tmax=3200
tdrift=4600
tdiff=tmax-tmin
tDiff=tdrift-tdiff
stitchedTP= []
thisFrameList=[]
td=0
skipFrame=False
tmin2=0
tdiff2=tmax-tmin
tDiff2=tdrift-tdiff2
tdiffa=tmax-tmin
tDiffa=tdrift-tdiffa
ntdlist=[]
driftincrement=True
FirstTime=True
changeMin=False
channellist2=[]
stitchedTP2=[]
goToNextFrame=False
tminp=0
frmcntby3 = 3
frmcntby2 = 2
frmcntby0 = 0
tmin_eo1 = 0
tdiff_eo1 = tmax-tmin_eo1
tDiff_eo1=tdrift-tdiff_eo1

tmin_eo2 = 0
tdiff_eo2 = tmax-tmin_eo2
tDiff_eo2=tdrift-tdiff_eo2

tmin_eo3 = 0
tdiff_eo3 = tmax-tmin_eo3
tDiff_eo3=tdrift-tdiff_eo3
tdiff_sf1 = tmax-tmin_eo1
tDiff_sf1=tdrift-tdiff_eo1
minp2 = 0
framelistp = []
frame11=0
framelistfull1=[]
tdiffP =tdiff
hitlist=[]                                                                                                                                
colplstart = 2976
step = 96
hitlist_firstslice=[]
hitlist_secondslice=[]
hitlist_thirdslice=[]
hitlist_fourslice=[]
hitlist_fifthslice=[]
tplistinduction = []
tplistcollection=[]
stitchedTP_part1 = []
stitchedTP_part2 = []
 
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

def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary
            

now = time.time()

#pr.enable()

print("start time :", now)
for r in range(25):
    start_time = time.time()
    print("start time :", start_time)
    for l in f:
        words = l.split()
        NumOfWords = len(words)
        for w in range(0,NumOfWords):
            wf = l.split()[w]
            wrh = l.split()[w][4:]
            wlh = l.split()[w][0:4]
            wrb = bin(int(wrh, scale))[2:].zfill(num_of_bits)
            wlb = bin(int(wlh, scale))[2:].zfill(num_of_bits)
            wrd = int(wrh, 16)
            wld = int(wlh, 16)
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
                    femh=wrh[1:]+wlh[1:]
                    #print("wf 5hdr: "+str(wf))                                                                                                                                                                   
                    #frame = int(wrh[1:], 16) + int(wlh[1:], 16)                                                                                                                                                  
                    frame1 = int(wrh[1:], 16) + int(wlh[1:], 16)
                    #print("Frame1 is: "+str(frame1))
                    #framelistfull.append(frame)                                                                                                                                                                  
                if hdrcnt == 8:
                    #print("wf is :"+str(wf))
                    if (wrh[0] == "1"):
                        chnlheader=[wlh[1:],wrh[1:]]
                        frame2=int(wrb[-12:-6],2)
                        chnlheader_b=wrb[-12:-6] #[10:]                                                                                                                                                           
                        #print("Frame2 is: "+str(frame2))
                        if(frame1 == frame2):
                            frame = frame1
                            framelist.append(frame)
                            min1p=min(framelist)
                            #print("Starting Frame is: "+str(framelist))
                            #print("min1p: "+str(min1p))
                        elif(frame1 != frame2):
                            #print("Mismatch in frame numbers! Lets calculate masked frame number")
                            frameword_b=femheader1+femheader2[0:6]+chnlheader_b
                            maskedframe=int((frameword_b),2)
                            #print("Masked Frame is: " + str(maskedframe))
                            frame = maskedframe
                            framelist.append(frame)
                            min1p=min(framelist)
                            #print("Starting Frame is: "+str(framelist))
                            #print("min1p: "+str(min1p))

            if (wf[0:2] == "F1" and wf[4:8] == "FFFF"):
                femm=int(wlb[-5:], 2)
                femlist.append(femm)    
                #print("FEM is: "+str(femm))


            elif wf == "E0000000":
                hdrcnt = 0

            else:
                #print("Check len of framelist: "+str(framelist))
                if(int(len(framelist))>0):
                    for frm in range(min1p, min1p+3):  #if min1=1, 1,2,3 not to 4
                        if wrh[0] == "1":
                            channel = int(wrb[-6:],2)
                            channellist.append(channel)
                            larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                            chlarchlist.append([femm, channel, larchnlNum])
                            if (channel>=0 and channel<32):
                                larchnlNumInd = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                            elif(channel>=32 and channel<64):
                                larchnlNumCol = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                            tpcnt = 0
                            tot = ""
                            intgrl = ""
                            intgrlN = ""
                            amp = ""
                            nsamps = ""
                        if wlh[0] == "1":
                            channel = int(wlb[-6:],2)
                            channellist.append(channel)
                            larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                            chlarchlist.append([femm, channel, larchnlNum])
                            if (channel>=0 and channel<32):
                                larchnlNumInd = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                            elif(channel>=32 and channel<64):
                                larchnlNumCol = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))

                            tpcnt = 0
                            tot = ""
                            intgrl = ""
                            intgrlN = ""
                            amp = ""
                        if wrb[0:2] == "01":
                            timetick=int(wrb[2:],2)
                            timelist.append(timetick)
                            #print("TIMETICK rb = " + str(timetick))
                        if wlb[0:2] == "01":
                            #print(wlb)
                            timetick=int(wlb[2:],2)
                            timelist.append(timetick)
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
                            tplistint.append([frame, femm, channel,int(larchnlNum), timetick, int(intgrl), int(tot), int(amp)])
                            #print("TPList: "+str(tplistint))
                            tplistinduction.append([frame, femm, channel,int(larchnlNumInd), timetick, int(intgrl), int(tot), int(amp)])
                            tplistcollection.append([frame, femm, channel,int(larchnlNumCol), timetick, int(intgrl), int(tot), int(amp)])
                            tpcnt = 0                                                               
                            tot = ""                                                                                
                            intgrl = ""                                                                             
                            intgrlN = ""                                                                            
                            amp = ""                                                                                
                            nsamps = ""           
                            #tplistint=[]
                            #print("TPList check: "+str(len(tplistint)))
                            #print("TP is: "+str(tplistint))


                        #tplistint.append([frame, femm, channel,int(larchnlNum), timetick, int(intgrl), int(tot), int(amp)])                                           
                    min1p=min1p+frmcntby0
                    if(len(framelist)>0 and framelist[-1]==min(framelist)+frmcntby3):
                        #print("Min1p is: "+str(min1p))
                        #print("TPList is done!! and length is: "+str(len(tplistint)))
                        stitch_time = time.time()
                        print("TP Stitching time: ", stitch_time)
                        for tps in tplistint: #collection:       #tps[0] = tplistint[0] = frame  
                            #print("TP is:"+str(tps) + "minp: "+str(min1p))
                            #print("minp: "+str(min1p))
                            if(tps[0]==min1p):
                                #print("if condition: frame: "+str(tps[0]))
                                #print("len of stitchedTP2: "+str(len(stitchedTP2)))
                                if(FirstTime==True):
                                    td=min1p
                                    tmin2=0
                                    tminp=tmin
                                    tmin=tmin2
                                    tmax=3200
                                    tdrift=4600
                                    tdiff=tmax-tmin
                                    tdiff_sf1 =tdiff
                                    tDiff=tdrift-tdiff
                                    tDiff_sf1 =tDiff
                                    #print("FirstTimeCheck1(fr,tmin,tmax,td,tD): "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + " ," + str(tDiff))
                                    if(tps[4]>=tmin and tps[4]<=tmax):
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4],tps[5],tps[6],tps[7],td,cratenum])
                                        tmin_eo1=tDiff
                                        tmax=3200
                                        tdiff_eo1=tmax-tmin_eo1
                                        tDiff_eo1=tdrift-tdiff_eo1
                                        #print("EO1 firsttime:"+str(tmin_eo1)+", "+str(tdiff_eo1)+", "+str(tDiff_eo1))

                                else:  #if its not first time
                                    #print("hello!!!!!!!!")
                                    td=min1p
                                    tmin=tmin_eo3
                                    tmax=3200
                                    tdiff=tdiff_eo3 #tmax-tmin #tdiff2
                                    tdiff_sf1 = tdiff
                                    tDiff=tDiff_eo3 #tdrift-tdiff #tDiff2
                                    tDiff_sf1 = tDiff
                                    #print("Check1B(fr,tm,tM,td,tD): "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + " ," + str(tDiff))
                                    #print("_sf1: "+str( tdiff_sf1 )+ ", "+str( tDiff_sf1 ))
                                    if(len(stitchedTP2)!=0):
                                        if(td==min1p):
                                            stitchedTP.extend(stitchedTP2)
                                            stitchedTP2=[]  #clear list after transferring everything to another list 
                                            #print("len of stitchedTP after filling info from TP2: "+str(len(stitchedTP)))
                                    if(tDiff==3200):
                                        if(tps[4]>=tminp and tps[4]<=tDiff):
                                            #stitchedTP=[]
                                            stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4],tps[5],tps[6],tps[7],td, cratenum])
                                            #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                            tmin_eo1=tminp
                                            tmax=3200
                                            tdiff_eo1=tmax-tmin_eo1
                                            tDiff_eo1=tdrift-tdiff_eo1
                                            #print("EO1(==3200):"+str(tmin_eo1)+", "+str(tdiff_eo1)+", "+str(tDiff_eo1))
                                    elif(tDiff<3200):
                                        #print("Check1C(fr,tm,tM,td,tD): "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + " ," + str(tDiff))
                                        if(tps[4]>=tminp and tps[4]<=tDiff):
                                            #stitchedTP=[]
                                            stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiff,tps[5],tps[6],tps[7],td, cratenum])
                                            #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                            tmin_eo1=tDiff
                                            tmax=3200
                                            tdiff_eo1=tmax-tmin_eo1
                                            tdiff_sf1 = tdiff_eo1
                                            tDiff_eo1=tdrift-tdiff_eo1
                                            tDiff_sf1 = tDiff_eo1
                                            #print("EO1 tmin, tmax, tdiff, tDiff: "+str(tmin) +","+str(tdiff_eo1)+","+str(tDiff_eo1))
                                            #print("EO1 _sf1: "+str( tdiff_sf1 )+ ", "+str( tDiff_sf1 ))

                                        else:
                                            td=min1p+1
                                            #stitchedTP=[]
                                            stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]-tDiff,tps[5],tps[6],tps[7],td, cratenum])
                                            #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                            td=min1p
                                            tmin_eo1=tDiff
                                            tmax=3200
                                            tdiff_eo1=tmax-tmin_eo1
                                            tdiff_sf1 = tdiff_eo1
                                            tDiff_eo1=tdrift-tdiff_eo1
                                            tDiff_sf1 = tDiff_eo1
                                            #print("EO1 tmin, tmax, tdiff, tDiff: "+str(tmin) +","+str(tdiff_eo1)+","+str(tDiff_eo1))
                                            #print("EO1 _sf1: "+str( tdiff_sf1 )+ ", "+str( tDiff_sf1 ))
                                    elif(tDiff>3200):
                                        tmin2=tminp
                                        tmin=tmin2
                                        tmax=3200
                                        tdiffP = tdiff
                                        tdiff=tdiff+(tmax-tmin)
                                        tdiff_sf1 = tdiff
                                        tDiff=tdrift-tdiff
                                        tDiff_sf1 = tDiff
                                        #print("Check1D on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff) + "tdiffP is:"+str(tdiffP))
                                        #print ("1D _sf1: "+str(tdiff_sf1) + ", "+ str(tDiff_sf1))
                                        if(tps[4]>=tmin and tps[4]<=tmax):
                                            #stitchedTP=[]
                                            stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiffP,tps[5],tps[6],tps[7],td, cratenum])
                                            #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                            #tplistint=[]
                                            td=min1p
                                            tmin_eo1=tDiff
                                            tmax=3200
                                            tdiff_eo1=tmax-tmin_eo1
                                            tDiff_eo1=tdrift-tdiff_eo1
                                            #print("EO1 (>3200) : "+ str(tmin) +", "+str(tdiff_eo1) +", "+str(tDiff_eo1))


                            if(tps[0]==min1p+1):
                                #print("if condition: frame: "+str(tps[0]))
                                FirstTime=False
                                tmin2=tminp
                                tmin=tmin2
                                tmax=3200
                                tdiff= tdiff_sf1 #tdiff_eo1
                                tdiffP2 = tdiff
                                tDiff= tDiff_sf1 #tDiff_eo1
                                #print("Check2A on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff) +"tdiffP2: "+str(tdiff))
                                #print("tmin2 is: "+str(tmin2))

                                if(tDiff==3200):
                                    #print("tDiff found to be 3200!!!! Tricky. Clear everything at this point and start again")
                                    #tplistint = []
                                    #stitchedTP=[]
                                    #stitchedTP2=[]
                                    #FirstTime = True
                                    #print("Check Frame list: "+str(framelist))
                                    if(tps[4]>=0 and tps[4]<=tDiff):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4],tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        tmin_eo2=tminp
                                        tmax=3200
                                        tdiff_eo2=tmax-tmin_eo2
                                        tDiff_eo2=tdrift-tdiff_eo2


                                elif(tDiff<3200):
                                    #print("Check2B on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                    if(tps[4]>=tminp and tps[4]<=tDiff):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiff,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[] 
                                        tmin_eo2=tmin_eo1#tDiff
                                        tmax=3200
                                        tdiff_eo2=tmax-tmin_eo2
                                        tDiff_eo2=tdrift-tdiff_eo2
                                        #print("EO2 (if): "+str(tmin) +", "+str(tdiff_eo2)+" ,"+str(tDiff_eo2))
                                    else:
                                        #print("Check2C on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                        td=min1p+1
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]-tDiff,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[] 
                                        td=min1p
                                        tmin_eo2=tmin_eo1 #tDiff
                                        tmax=3200
                                        tdiff_eo2=tmax-tmin_eo2
                                        tDiff_eo2=tdrift-tdiff_eo2
                                        #print("EO2 (else): "+str(tmin) +", "+str(tdiff_eo2)+" ,"+str(tDiff_eo2))
                                elif(tDiff>3200):
                                    td=min1p+1
                                    tmin2=tminp
                                    tmin=tmin2
                                    tmax=3200
                                    tdiff=tdiff+(tmax-tmin)
                                    tDiff=tdrift-tdiff
                                    #print("Check2D on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                    if(tps[4]>=tmin and tps[4]<=tmax):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiffP2,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[]                                                                                                    
                                        td=min1p
                                        tmin_eo2=tminp #tmin_eo1 #tDiff
                                        tmax=3200
                                        tdiff_eo2=tdiff #tmax-tmin_eo2
                                        tDiff_eo2=tDiff #tdrift-tdiff_eo2
                                        #print("EO2 (2D else>3200): "+str(tmin) +", "+str(tdiff_eo2)+" ,"+str(tDiff_eo2))

                            if(tps[0]==min1p+2):
                                tmin=tmin_eo2
                                tmax=3200
                                tdiff=tdiff_eo2
                                tdiffP3=tdiff
                                tDiff=tDiff_eo2
                                #print("Check3A on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff) +"tdiffP3: "+str(tdiffP3))
                                if(tDiff==3200):
                                    if(tps[4]>=tminp and tps[4]<=tDiff):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4],tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))

                                        tmin_eo3=tminp                                                           
                                        tmax=3200
                                        tdiff_eo3=tmax-tmin_eo3
                                        tDiff_eo3=tdrift-tdiff_eo3
                                        #print("EO3 :" +str(tmin) +", "+str(tdiff_eo3)+" ,"+str(tDiff_eo3))

                                elif(tDiff<3200):
                                    #print("Check3B on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                    if(tps[4]>=tminp and tps[4]<=tDiff):
                                        td=min1p+1
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiff,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[] 
                                        td=min1p
                                        tmin_eo3=tDiff
                                        tmax=3200
                                        tdiff_eo3=tmax-tmin_eo3
                                        tDiff_eo3=tdrift-tdiff_eo3
                                        #print("EO3 (<3200 if):" +str(tmin) +", "+str(tdiff_eo3)+" ,"+str(tDiff_eo3))
                                    else:
                                        #print("Check3C on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + ", "+str(tdiff) + ", " + str(tDiff))
                                        td=min1p+3
                                        #stitchedTP=[]
                                        stitchedTP2.append([tps[0],tps[1],tps[2],tps[3],tps[4]-tDiff,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP2 len for frame:" + str(tps[0]) + " is: " +str(len(stitchedTP2)))
                                        #tplistint=[] 
                                        td=min1p
                                        tmin_eo3=tDiff
                                        tmax=3200
                                        tdiff_eo3=tmax-tmin_eo3
                                        tDiff_eo3=tdrift-tdiff_eo3
                                        #print("EO3 (<3200 else):" +str(tmin) +", "+str(tdiff_eo3)+" ,"+str(tDiff_eo3))

                                elif(tDiff>3200):
                                    tmin2=tminp
                                    tmin=tmin2
                                    tmax=3200
                                    tdiff=tdiff+(tmax-tmin)
                                    tDiff=tdrift-tdiff
                                   #print("Check3D on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                    if(tps[4]>=tmin and tps[4]<=tmax):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiffP3,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[]                                                                                                                
                                        td=min1p
                                        tmin_eo3=tDiff
                                        tmax=3200
                                        tdiff_eo3=tmax-tmin_eo3
                                        tDiff_eo3=tdrift-tdiff_eo3
                                        #print("EO3 (>3200):" +str(tmin) +", "+str(tdiff_eo3)+" ,"+str(tDiff_eo3))

                        xlist=[]                                                                                                                  
                        ylist=[]                                                                                                                 
                        zlist=[]
                        hitlist_firstslice = []
                        driftNum=2
                        #print("len of stitchedTP: "+str(len(stitchedTP)))
                        for content in stitchedTP:
                            #print("CONTENT[3]: "+str(content[3]))
                            if(content[8]==driftNum and content[3]!=0):
                                xlist.append(content[3])
                                ylist.append(content[4])
                                zlist.append(content[5])
                            if (int(content[3]) >= int(colplstart) and int(content[3]) < int(colplstart)+int(step)):
                                hitlist_firstslice.append([content[0], content[1], content[2],content[3],content[4],content[5],content[6],content[7],content[8]])
                                #print("HitSlice: "+str(hitlist_firstslice))
                            elif (int(content[3]) >= int(colplstart)+int(step) and int(content[3]) < int(colplstart)+(2*int(step))):
                                hitlist_secondslice.append([content[0], content[1], content[2],content[3],content[4],content[5],content[6],content[7],content[8]])
                            elif (int(content[3]) >= int(colplstart)+(2*int(step)) and int(content[3]) < int(colplstart)+(3*int(step))):
                                hitlist_thirdslice.append([content[0], content[1], content[2],content[3],content[4],content[5],content[6],content[7],content[8]])
                            elif (int(content[3]) >= int(colplstart)+(3*int(step)) and int(content[3]) < int(colplstart)+(4*int(step))):
                                hitlist_fourslice.append([content[0], content[1], content[2],content[3],content[4],content[5],content[6],content[7],content[8]])
                            elif (int(content[3]) >= int(colplstart)+(4*int(step)) and int(content[3]) < int(colplstart)+(5*int(step))):
                                hitlist_fifthslice.append([content[0], content[1], content[2],content[3],content[4],content[5],content[6],content[7],content[8]])

                        '''if (xlist!=[] and ylist!=[] and zlist!=[]):
                            my_cmap = plt.cm.get_cmap('viridis')
                            tp_adc=plt.scatter(xlist, ylist, c=zlist, s=20, cmap=my_cmap)
                            plt.colorbar(tp_adc)
                            plt.xlabel("LArSoft Channel")
                            plt.ylabel("Timetick")
                            plt.title("Drift "+str(driftNum)+", TP: ROI Integral.,Run 28554")
                            plt.show()'''

                        #print("Len of hitlist: "+str(len(hitlist_firstslice)) + " , " + str(len(hitlist_secondslice)) + " , " + str(len(hitlist_thirdslice)) + " , " +str(len(hitlist_fourslice)) + " , " + str(len(hitlist_fifthslice)))

                        #hitlist_firstslice.append(time.time())
                        #stitchedTP.append(2)
                        for dr in stitchedTP:
                            if(dr[8]==min1p):
                                stitchedTP_part1.append([dr[0],dr[1],dr[2],dr[3],dr[4],dr[5],dr[6],dr[7],dr[8],dr[9]])
                            elif(dr[8]==min1p+1):
                                stitchedTP_part2.append([dr[0],dr[1],dr[2],dr[3],dr[4],dr[5],dr[6],dr[7],dr[8],dr[9]])
                        #print("StitchedTP Len: " + str(len(stitchedTP)) + "part1: " + str(len(stitchedTP_part1)) + "part2: "+ str(len(stitchedTP_part2)))
                        #stitchedTP_part1df = pd.DataFrame(stitchedTP_part1)
                        #print("check TP P1: ", stitchedTP_part1df)
                        #TP1_test = json.dumps(stitchedTP_part1)
                        TP_data_part1 = json.dumps(stitchedTP_part1).encode('utf8')
                        socket.send(TP_data_part1)
                        #TP2_test = json.dumps(stitchedTP_part2)
                        #stitchedTP_part2df = pd.DataFrame(stitchedTP_part2)
                        #print("check TP P2: ", stitchedTP_part2df)
                        TP_data_part2 = json.dumps(stitchedTP_part2).encode('utf8')
                        socket.send(TP_data_part2)
                        #pr.disable()
                        pr.print_stats(sort='time')
                        '''bin_test = dict_to_binary(stitchedTP_part1)
                        bin_test1 = dict_to_binary(stitchedTP_part2)
                        socket.send_string(bin_test)
                        socket.send_string(bin_test1)'''
                        time_stmp2 = time.time()
                        print("time stmp end :", time_stmp2)
                        time_tot = time_stmp2 - now
                        time_tot1 = time_stmp2 - start_time
                        time_stitch = time_stmp2 - stitch_time
                        print("time diff since beginning: ", time_tot)
                        print("time diff since loop: ", time_tot1)
                        print("time diff for each TP:", time_stitch)
                        #print('Sending msg')
                        #print(TP_data)
                        time.sleep(0)

####################Cleartplistint and stitchedTP and start over again
                        tplistint.clear() #=[]
                        tplistcollection.clear()
                        #print("LENGTH of STP: "+str(len(stitchedTP)))
                        #print("TPlist cleared")
                        stitchedTP.clear() #=[]
                        stitchedTP_part1.clear()
                        stitchedTP_part2.clear()
                        #print("stitchedTP, P1, P2 cleared")
                        #print("Double check: tp and stitchTP,P1,P2 list: "+str(len(tplistcollection)) + " , "+ str(len(stitchedTP)) + " , "+ str(len(stitchedTP_part1)) + " , "+ str(len(stitchedTP_part2)) )
                        #print("Check StitchedTP form: "+str(stitchedTP) )
                        frmcntby3=frmcntby3+3


                        #min1p = min1p+3
                        frmcntby0 = frmcntby0 + 3
                        #print("FrameCounter: "+str(frmcntby3) )
                        hitlist_firstslice.clear()  # = []
                        hitlist_secondslice.clear() # = []
                        hitlist_thirdslice.clear()  # = []
                        hitlist_fourslice.clear()   # = []
                        hitlist_fifthslice.clear()  # = []
                        #framelist=[]
                        #print("Framlist cleared: "+str(framelist))


