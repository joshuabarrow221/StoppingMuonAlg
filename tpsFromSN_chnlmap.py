#Decode the binary supernova (SN) file and plot the trigger primitives calculated from SN ROIs in channel vs time tick. Code to test the uBooNE data runs. Channel mapping is also implemented here.
#D.Kalra (dkalra@nevis.columbi.edu) (dk3172@columbia.edu) (June 22, 2021)  


import matplotlib.pyplot as plt
import matplotlib.colors as clrs
import matplotlib.cm as cm
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import matplotlib
import numpy as np
import csv
import operator


#Command to convert binary to hex-dump file: hexdump -v -e '8/4 "%08X ""\n"' BINARYFILE 
f = open("SN_Nominal_0026639_test","r")#input is hex-dump file.
#f = open("SN_0026592_test","r")

 
scale = 16
femm=0
frame=0 
num_of_bits = 16
fem=0
tot = 0
intgrl = 0
intgrlN = 0
nsamps = 0
hdrcnt = 0
femcnt=0
amp = 0
N = 11
channel=0
larchnlNum=0
timetick=0
larchnlNumInd=0
larchnlNumCol=0
framelist=[]
channellist=[]
larchannellist=[]
timelist=[]
tplist=[]
tplistint=[]
tplistamp=[]
tplisttot=[]
femlist=[]
totlist=[]
fig, ax = plt.subplots(1)
channelfilterlist=[]
larchnlNumfilterlist=[]
timefilterlist=[]
mainlist=[]
mainlistind=[]
mainlistcol=[]
adclist=[]

#Channel Mapping
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
#Need to change the cratenumber for various SEBs
cratenum=1

#Refer to sbn docdb 17726 for the data-format
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
            if (wf[0]=="F"):
                hdrcnt += 1
                if hdrcnt == 5:
                    frame=int(wrh[1:], 16) + int(wlh[1:], 16)
                    framelist.append(frame)
            if (wf[0:2] == "F1" and wf[4:8] == "FFFF"):
                femm=int(wlb[-5:], 2)
                #femlist.append(femm)
                #print("FEM is"+str(femm))
            elif wf == "E0000000":
                hdrcnt = 0
            else:
                if wrh[0] == "1":
                    channel=int(wrb[-6:],2)
                    #channellist.append(channel)
                    larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                    if (channel >= 0 and channel < 32):
                        larchnlNumInd = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                    else:
                        larchnlNumCol = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                    
                    #larchnlNum = int(chMap.CrateFEMCh2PlaneWire(int(cratenum),int(femm), int(channel)))
                    #larchannellist.append(larchnlNum)
                    #print("Channel rh:"+str(channel))
                    #mainlist.append([fem,channel, timetick,intgrl])
                    tot = 0
                    intgrl = 0
                    amp=0

                elif wrb[0:2] == "01":
                    timetick=int(wrb[2:],2)
                    #print("Time rh:"+str(timetick))
                    #mainlist.append([fem,channel, timetick,intgrl])
                    tot = 0
                    intgrl = 0
                    amp=0
                    
                elif (wrh[0] == "2"): # or wrh[0] == "3"):
                    tot+=1
                    adc=int(wrb[-12:],2)
                    if int(wrb[-12:],2)>amp:
                        amp = int(wrb[-12:],2)
                    intgrl += int(wrb[-12:],2)
            
                elif (wrh[0]  == "3"):                                                                                                 
                    tot+=1
                    adc=int(wrb[-12:],2)
                    if int(wrb[-12:],2)>amp:
                        amp = int(wrb[-12:],2)
                    intgrl += int(wrb[-12:],2)
                    #print("TP rh: "+str(intgrl))
                    tplist.append(intgrl)
                    adclist.append(adc)
                    mainlist.append([frame,femm,channel,int(larchnlNum), timetick,intgrl,tot,amp])                                                                                       

                if wlh[0] == "1":
                    channel=int(wlb[-6:],2)
                    #channellist.append(channel)
#                    larchnlNum = int(chMap.CrateFEMCh2PlaneWire(int(cratenum),int(femm), int(channel)))
                    larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                    if (channel >= 0 and channel < 32):
                        larchnlNumInd =str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                    else:
                        larchnlNumCol =str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                    #larchannellist.append(larchnlNum)
                    #print("Channel lh: "+str(channel))
                    #mainlist.append([fem,channel, timetick,intgrl])
                    tot=0
                    intgrl=0
                    amp=0
            
                elif wlb[0:2] == "01":
                    timetick=int(wlb[2:],2)
                    #mainlist.append([fem,channel, timetick,intgrl])
                    tot=0
                    amp=0
                    intgrl=0
                    #print("Time lh: "+str(timetick))

                elif (wlh[0] == "2"):
                    tot+=1
                    adc=int(wlb[-12:],2)
                    if int(wlb[-12:],2)>amp:
                        amp = int(wlb[-12:],2)
                    intgrl += int(wlb[-12:],2)
                elif (wlh[0] == "3"):
                    tot+=1
                    adc=int(wlb[-12:],2)
                    if int(wlb[-12:],2)>amp:
                        amp = int(wlb[-12:],2)
                    intgrl += int(wlb[-12:],2)                    
                    #print("TP lh: "+str(intgrl))
                    tplist.append(intgrl)
                    adclist.append(adc)
                    mainlist.append([frame,femm,channel,int(larchnlNum), timetick,intgrl,tot,amp])
                    mainlistind.append([frame,femm,channel,int(larchnlNumInd),timetick,intgrl,tot,amp])
                    mainlistcol.append([frame,femm,channel,int(larchnlNumCol),timetick,intgrl,tot,amp])


#print(framelist)
#print(femlist)

#print(channellist)
#print(larchannellist)
#print(len(channellist))
#print(len(larchannellist))


#print(mainlist[0])
#print(mainlist)
#print(len(mainlist))
#print(fem)

xlist=[]
ylist=[]
zlist=[]
frmNUM=4
femNUM=6
#0: frame, 1: fem, 2: channel, 3: larchannel, 4: timetick, 5: integral, 6: tot, 7: amp
for content in mainlist:
    if(content[0]==frmNUM and content[5]!=0): # and content[1]==femNUM):
        xlist.append(content[3])
        ylist.append(content[4])
        zlist.append(content[5])

#print(len(xlist))
#print(len(ylist))
#print(len(zlist))
#print(mainlist)

#print(len(tplist))

#xlist = sorted(xlist, key = operator.itemgetter(3))   

my_cmap = plt.cm.get_cmap('viridis') 
tp_adc=plt.scatter(xlist, ylist, c=zlist, s=20, cmap=my_cmap) 
plt.colorbar(tp_adc) 
#plt.xlim(1500,2500)   # for crate 02 1500-2500                                                                                                    
plt.xlabel("LArSoft Channel")                                                                                                                         
plt.ylabel("Timetick")   
plt.title("Frame "+str(frmNUM)+", TP: ROI Integral., NominalRun") # FEM-"+str(femNUM)+", TP: ROI integral, NominalRun")

plt.show() 
