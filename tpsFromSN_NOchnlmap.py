#Decode the binary supernova (SN) file and plot the trigger primitives calculated from SN ROIs in channel vs time tick. Code totest fake-data runs.                                                     
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
f = open("SN_multiFEMs_fakedata_test","r") #input i shex-dump file
scale = 16 
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
adclist=[]


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
                fem=int(wlb[-5:], 2)
                #print("FEM is"+str(fem))
            elif wf == "E0000000":
                hdrcnt = 0
            else:
                if wrh[0] == "1":
                    channel=int(wrb[-6:],2)
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
                    mainlist.append([frame,fem,channel, timetick,intgrl])                                                                                       

                if wlh[0] == "1":
                    channel=int(wlb[-6:],2)
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
                    mainlist.append([frame, fem,channel, timetick,intgrl])
                    

#print(framelist)
#print(mainlist[0])
#print(mainlist[1])
#print(len(mainlist))
#print(fem)
xlist=[]
ylist=[]
zlist=[]
frmNUM=1
femNUM=5
for content in mainlist:
    if(content[0]==frmNUM): # and content[1]==femNUM):
        xlist.append(content[2])
        ylist.append(content[3])
        zlist.append(content[4])

#print(len(xlist))
#print(len(ylist))
#print(len(zlist))
#print(mainlist)


#print(len(tplist))

my_cmap = plt.cm.get_cmap('viridis') 
tp_adc=plt.scatter(xlist, ylist, c=zlist, s=20, cmap=my_cmap) 
plt.colorbar(tp_adc) 
#plt.xlim(min(xlist_even),max(xlist_even))                                                                                                    
plt.xlabel("Channel")                                                                                                                         
plt.ylabel("Time ticks")   
#plt.title("Frame "+str(frmNUM)+", FEM-"+str(femNUM)+", TP: ROI integral, NominalRun")
plt.title("Frame "+str(frmNUM)+",TP: ROI integral, Fake-data Run") 
plt.show() 


