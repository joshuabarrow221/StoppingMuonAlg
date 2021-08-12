import matplotlib.pyplot as plt
import matplotlib.colors as clrs
import matplotlib.cm as cm
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import matplotlib
import numpy as np
import csv
import operator

f = open("SN_0026659_Nominal_Seb02_Some","r")

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
listcol=[]
main=[]

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
CrateID=2
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
            elif wf == "E0000000":
                hdrcnt = 0
            else:
                if wrh[0] == "1":
                    channel=int(wrb[-6:],2)
                    #channellist.append(channel)                                                                                                          
                    larchnlNum = str(chMap.CrateFEMCh2PlaneWire(CrateID,femm, channel))
                    if (channel >= 0 and channel < 32):
                        larchnlNumInd = str(chMap.CrateFEMCh2PlaneWire(CrateID,femm, channel))
                    else:
                        larchnlNumCol = str(chMap.CrateFEMCh2PlaneWire(CrateID,femm, channel))
                        listcol.append(int(larchnlNumCol))

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
                    mainlistind.append([frame,femm,channel,int(larchnlNumInd),timetick,intgrl,tot,amp])
                    mainlistcol.append([frame,femm,int(larchnlNumCol),timetick,intgrl,tot,amp])
                    if (intgrl!=0 and tot!=0 and amp!=0):
                        main.append([frame,femm,channel,int(larchnlNum), timetick,intgrl,tot,amp])

                if wlh[0] == "1":
                    channel=int(wlb[-6:],2)
                    #channellist.append(channel)                                                                                                          
#                    larchnlNum = int(chMap.CrateFEMCh2PlaneWire(int(CrateID),int(femm), int(channel)))                                                  
                    larchnlNum = str(chMap.CrateFEMCh2PlaneWire(CrateID,femm, channel))
                    if (channel >= 0 and channel < 32):
                        larchnlNumInd =str(chMap.CrateFEMCh2PlaneWire(CrateID,femm, channel))
                    else:
                        larchnlNumCol =str(chMap.CrateFEMCh2PlaneWire(CrateID,femm, channel))
                        listcol.append(int(larchnlNumCol))

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
                    mainlistcol.append([frame,femm,int(larchnlNumCol),timetick,intgrl,tot,amp])
                    if (intgrl!=0 and tot!=0 and amp!=0):
                        main.append([frame,femm,channel,int(larchnlNum), timetick,intgrl,tot,amp])
                    



thisFrame=0
tmin=0
tmax=3200
tdrift=4600
tdiff=tmax-tmin
tDiff=tdrift-tdiff
stitchedTP=[]
thisFrameList=[]
td=0
skipFrame=False
tmin2=tDiff
tdiff2=tmax-tmin
tDiff2=tdrift-tdiff
ntdlist=[]
driftincrement=True

for it,ht in enumerate(mainlist): 
    thisFrameList.append(ht[0])
   
#Loop over frames
for n in range(min(thisFrameList)+1,len(framelist)+1):
    if(skipFrame==False):
        td+=1
    if (skipFrame==True):
        td+=1
        skipFrame=False
        print("skipframe is True!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        continue  
    tmin=tmin2
    tmax=3200
    tdiff= tmax-tmin 
    tDiff= tdrift-tdiff
    for i,h in enumerate(mainlist):
        print("Number "+str(i) + " has Main list is: "+str(h))
        if(n==min(thisFrameList)+1): 
            tmin=0
            tmax=3200
            tdrift=4600
            tdiff=tmax-tmin
            tDiff=tdrift-tdiff
            if(h[0]==n-1):
                if(h[4]>=tmin and h[4]<=tmax):
                    stitchedTP.append([h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],td])
            if(tdiff != 4600):
                if(h[0]==n):
                    if(h[4]>=tmin and h[4]<=tDiff):
                        stitchedTP.append([h[0],h[1],h[2],h[3],h[4]+tdiff,h[5],h[6],h[7],td]) 
          

        elif(n==len(framelist)): 
            if(h[0]==n-1):
                if(h[4]>=tmin and h[4]<=tmax):
                    stitchedTP.append([h[0],h[1],h[2],h[3],h[4]-tmin,h[5],h[6],h[7],td])
                    
            if(tdiff != 4600):
                if(tDiff<=3200):
                    if(h[0]==n):
                        if(h[4]>=0 and h[4]<=tDiff):
                            stitchedTP.append([h[0],h[1],h[2],h[3],h[4]+tdiff,h[5],h[6],h[7],td])
                           
                else:
                    continue

        elif(n>min(thisFrameList)+1): 
            tDiff=tdrift-tdiff  
            if(h[0]==n-1):
                if(h[4]>=tmin and h[4]<=tmax):
                    stitchedTP.append([h[0],h[1],h[2],h[3],h[4]-tmin,h[5],h[6],h[7],td])

            if(tdiff != 4600):
                if(tDiff<=3200):
                    if(h[0]==n):
                        if(h[4]>=0 and h[4]<=tDiff):
                            stitchedTP.append([h[0],h[1],h[2],h[3],h[4]+tdiff,h[5],h[6],h[7],td])
                            tmin2=tDiff

                elif(tDiff>3200):
                    tdiff2=tdiff
                    tDiff2=tDiff
                    skipFrame=True
                    if(h[0]==n):
                        if(h[4]>=0 and h[4]<=tmax):
                            stitchedTP.append([h[0],h[1],h[2],h[3],h[4]+tdiff2,h[5],h[6],h[7],td])
                    tdiff2=tdiff2+(tmax-0)
                    tDiff2=tdrift-tdiff2
                    if((tmax-0)!=4600):
                        if(h[0]==n+1):
                            if(h[4]>=0 and h[4]<=tDiff2):
                                stitchedTP.append([h[0],h[1],h[2],h[3],h[4]+tdiff2,h[5],h[6],h[7],td])
                                tmin2=tDiff2
                            

#frame,femm,channel,int(larchnlNum), timetick,intgrl,tot,amp
xlist=[]
ylist=[]
zlist=[]

driftNum=2

for content in stitchedTP:
    if(content[8]==driftNum):
        xlist.append(content[3])
        ylist.append(content[4])
        zlist.append(content[5])

my_cmap = plt.cm.get_cmap('viridis')
tp_adc=plt.scatter(xlist, ylist, c=zlist, s=20, cmap=my_cmap)
plt.colorbar(tp_adc)
plt.xlabel("LArSoft Channel")                                                                                                
plt.ylabel("Timetick")
plt.title("Drift "+str(driftNum)+", TP: ROI Integral., NominalRun") # FEM-"+str(femNUM)+", TP: ROI integral, NominalRun")  

plt.show()


#print(int(larchnlNumCol))
#print(listcol)
femcnt=0
hitlist=[]
colplstart = 2976
step = 96
hitlist_firstslice=[]
hitlist_secondslice=[]
hitlist_thirdslice=[]
hitlist_fourthslice=[]
hitlist_fifthslice=[]

hitlist_all=[]

   

for i, ch in enumerate(mainlistcol):
    if (int(ch[2]) >= colplstart and int(ch[2]) < colplstart+step):
        hitlist_firstslice.append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])
        #hitlists[0].append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])
    elif(int(ch[2]) >= colplstart+step and int(ch[2]) < colplstart+(2*step)):
        hitlist_secondslice.append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])
        #hitlists[1].append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])
    elif(int(ch[2]) >= colplstart+(2*step) and int(ch[2]) < colplstart+(3*step)):
        hitlist_thirdslice.append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])
        #hitlists[2].append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])
    elif(int(ch[2]) >= colplstart+(3*step) and int(ch[2]) < colplstart+(4*step)):
        hitlist_fourthslice.append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])
        #hitlists[3].append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])
    elif(int(ch[2]) >= colplstart+(4*step) and int(ch[2]) < colplstart+(5*step)):
        hitlist_fifthslice.append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])
        #hitlists[4].append([ch[0],ch[1],ch[2],ch[3],ch[4],ch[5],ch[6]])

#print(len(hitlist_firstslice))
#print(len(hitlist_secondslice))
#print(len(hitlist_thirdslice))
#print(len(hitlist_fourthslice))
#print(len(hitlist_fifthslice))

hitlist_all.append(hitlist_firstslice)
hitlist_all.append(hitlist_secondslice)
hitlist_all.append(hitlist_thirdslice) 
hitlist_all.append(hitlist_fourthslice)
hitlist_all.append(hitlist_fifthslice)


#print(hitlist_all[1])
#print(len(hitlist_all[1]))
#print(len(hitlist_all[2]))
#print(len(hitlist_all[3]))
#print(len(hitlist_all[4]))

