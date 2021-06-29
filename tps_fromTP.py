#Decode the binary trigger primitive file and plot the trigger primitives in channel vs time tick. Currently, the scripts plots the integral of SN ROI (one of the TP definition) for frame number 34 (configurable with variable frnum). To plot max. amplitude or Time Over Threshold, one can change in the plotting section for the TPs 
#D.Kalra (dkalra@nevis.columbi.edu) (dk3172@columbia.edu) (June 22, 2021)

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
f = open("TP_0026678","r")
frnum=34
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
frmlist=[]
tplistamp=[]
tplisttot=[]
tplistint=[]
x=[]
y=[]
z=[]
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
        #print(wrd)
        if wf == "FFFFFFFF":
            hdrcnt = 0
        if (wf[0]=="F"):
            hdrcnt += 1
            if hdrcnt == 5:
                if ((str(int(wrh[1:], 16)) + str(int(wlh[1:], 16))) != str(frm)):
                    frm = int(wrh[1:]+wlh[1:], 16)
                    frmlist.append(frm)
                    frmb = bin(int(wrh[1:]+wlh[1:], 16))[2:].zfill(24)
                    #print("FRAME NUM = " + frm + " bin    " + frmb)
                    #print("FRAME NUM = " + str(int(wrh[1:], 16)) + str(int(wlh[1:], 16)))
                    #print("FRAME NUM = " + str(wrh[1:]) + str(wlh[1:]))
        if wrh[0] == "1":
            channel = int(wrb[-6:],2)
            frame=int(frmb[0:18]+wrb[4:10],2)
            print("FRAME NUM = " + str(int(frmb[0:18]+wrb[4:10],2)))
            print("CHNL rh= " + str(int(wrb[-6:],2)))
            #print("binary = " + str(wrb))
            tpcnt = 0
            tot = ""
            intgrl = ""
            intgrlN = ""
            amp = ""
            nsamps = ""
        if wlh[0] == "1":
            channel = int(wlb[-6:],2)
            print("FRAME NUM = " + str(int(frmb[0:18]+wlb[4:10],2)))
            print("CHNL lh= " + str(int(wlb[-6:],2)))
            #print("binary = " + str(wlb))
            tpcnt = 0
            tot = ""
            intgrl = ""
            intgrlN = ""
            amp = ""
        if wrb[0:2] == "01":
            timetick=int(wrb[2:],2)
            print("TIMETICK rb = " + str(int(wrb[2:],2)))
        if wlb[0:2] == "01":
            timetick=int(wlb[2:],2)
            print("TIMETICK lb = " + str(int(wlb[2:],2)))
        if wlh[0] == "C":
                tpcnt +=1
        if tpcnt == 1:
            tot = int(wlh[1:],16)
        if tpcnt == 3:
            intgrl = str(int(str(wlh[1:])+intgrl,16)) #str(int(str(wlh[1:])+intgrl,16))
        if tpcnt == 5:
            intgrlN = str(int(str(wlh[1:])+intgrlN,16))
        if wrh[0] == "C":
            tpcnt +=1
        if tpcnt == 2:
            intgrl = str(wrh[1:]) #str(wrh[1:])
        if tpcnt == 4:
            intgrlN = str(wrh[1:])
        if tpcnt == 6:
            amp = str(int(wrh[1:],16))
            if(frm==frnum):
#            if(intgrl!=0 and intgrlN!=0 and amp!=0 and tot!=0):
                tplistamp.append([channel, timetick, int(amp)])
                tplisttot.append([channel, timetick, int(tot)])
                tplistint.append([channel, timetick, int(intgrl)])
                print("TOT = " + str(tot))
                print("INT = " + str(intgrl))
                print("INTN = " + str(intgrlN))
                print("AMP = " + str(amp))
                print(len(tplistint))
                tpcnt = 0
                tot = ""
                intgrl = ""
                intgrlN = ""
                amp = ""
                nsamps = ""
        if wf == "E0000000":
            hdrcnt = 0



#print(frmlist)
print("Lenof TPList"+ str(len(tplistint)))
xlist=[]
ylist=[]
zlist=[]

for pl in tplistint:
    #if (pl[0]>30 and pl[0]<64):
    xlist.append(pl[0])
    ylist.append(pl[1])
    zlist.append(pl[2])
        #print(xlist)
        #print(ylist)
        #print(zlist)

cm = plt.cm.get_cmap('Dark2')

tp_adc=plt.scatter(xlist, ylist, c=zlist, vmin=min(zlist),vmax=max(zlist), s=20, cmap=cm, label="collection wire data")          

plt.colorbar(tp_adc)
#plt.show()
plt.xlabel("Channel")
plt.ylabel("Time ticks")
#plt.ylim(0,15000)  #to compare with SN TPs
plt.title("Frame"+str(frnum)+", TPs from TP")# [Collection Plane Only]")
plt.show()

