#import matplotlib.pyplot as plt
#import matplotlib
import numpy as np
import sys
import json
#Command to convert binary to hex-dump file: hexdump -v -e '8/4 "%08X ""\n"' BINARYFILE 
#f = open("TP_multiFEMs_fakedata_test","r")
#f = open("TP_0026678","r")  #input is hex-dump file

f=open(sys.argv[1],"r")
#cratenum=7                                                                                                                                                    
outf=open(sys.argv[2],"w")


scale = 16 ## equals to hexadecimal
num_of_bits = 16
tot = 0
intgrl = 0
#intgrlN = 0
tpcnt = 0
hdrcnt = 0
amp = 0
frm = 0
frmb = 0
framelist=[]
channellist=[]
timelist=[]
mainlist=[]
femlist=[]
tplistamp=[]
tplisttot=[]
tplistint=[]
x=[]
y=[]
z=[]
femm=0
frame=0
frame1=0
framelist1=[]
channel=0
larchnlNum=0
timetick=0
tot=0
amp=0
chlarchlist=[]
femheader1=0
class ChannelMap:
    def __init__(self, mapfile):
        self.mapfile = mapfile
        self.table_readout2larsoft = {} # The keys are the trio crate, FEM, channels                                                  
        self.table_larsoft2readout = {} # The keys are plane, wire number                                                                 
        with open(mapfile) as inf:
            for line in inf.readlines():
                #crate, fem, ch, plane, wire = line.split()
                plane, wire , crate, fem, ch = line.split()
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
cratenum=sys.argv[3]
print(cratenum)

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
        if (wf[0]=="F" or wrh[0]=="1" or wlh[0]=="1"):
            hdrcnt += 1
            if (hdrcnt == 5 and wf[0]=="F"):
                femheader1=wrb[4:]
                femheader2=wlb[4:]
                #print("hdr 5: "+str(wf))
                frame1 = int(wrh[1:], 16) + int(wlh[1:], 16)
                framelist1.append(frame1)
                #print("hdr frame: "+str(frame1))
            if hdrcnt == 8:
                #print("8hdr: "+str(wf))
                if(wrh[0] == "1" and femheader1!=0):
                    chnlheader=[wlh[1:],wrh[1:]]
                    frame2=int(wrb[-12:-6],2)
                    chnlheader_b=wrb[-12:-6]
                    frameword_b=femheader1+femheader2[0:6]+chnlheader_b
                    frame=int((frameword_b),2)
                    framelist.append(frame)
                    #print("Frame: "+str(frame))
                    
                #print("Frame: " + str(frame))
                #print("Frame: "+str(frame))
                #if ((str(int(wrh[1:], 16)) + str(int(wlh[1:], 16))) != str(frm)):
                 #   frm = int(wrh[1:]+wlh[1:], 16)
                  #  frmlist.append(frm)
                   # frmb = bin(int(wrh[1:]+wlh[1:], 16))[2:].zfill(24)
                    #print("FRAME NUM = " + frm + " bin    " + frmb)
                    #print("FRAME NUM = " + str(int(wrh[1:], 16)) + str(int(wlh[1:], 16)))
                    #print("FRAME NUM = " + str(wrh[1:]) + str(wlh[1:]))

        if (wf[0:2] == "F1" and wf[4:8] == "FFFF"):
            femm=int(wlb[-5:], 2)
            femlist.append(femm)    
            #print("FEM is: "+str(femm))


        elif wf == "E0000000":
            hdrcnt = 0

        else:

            if wrh[0] == "1":
                channel = int(wrb[-6:],2)
                channellist.append(channel)
                larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                chlarchlist.append([femm, channel, larchnlNum])
                #frame=int(frmb[0:18]+wrb[4:10],2)
                #larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                #print("FRAME NUM = " + str(int(frmb[0:18]+wrb[4:10],2)))
                #print("CHNL rh= "+str(wrh)+"channel is:" + str(channel))
                #print("binary = " + str(wrb))
                tpcnt = 0
                tot = 0
                intgrl = 0
                intgrlN = ""
                amp = 0
                nsamps = ""
            if wlh[0] == "1":
                channel = int(wlb[-6:],2)
                channellist.append(channel)
                larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                chlarchlist.append([femm, channel, larchnlNum])
                #larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                #print("FRAME NUM = " + str(int(frmb[0:18]+wlb[4:10],2)))
                #print("CHNL lh= "+str(wlh)+"channel is: " + str(channel))
                #print("binary = " + str(wlb))
                tpcnt = 0
                tot = 0
                intgrl = 0
                intgrlN = ""
                amp = 0
            if wrb[0:2] == "01":
                timetick=int(wrb[2:],2)
                timelist.append(timetick)
                #print("TIMETICK rb = " + str(timetick))
            if wlb[0:2] == "01":
                timetick=int(wlb[2:],2)
                timelist.append(timetick)
                #print("TIMETICK lb = " + str(timetick))
            if wlh[0] == "C":
                tpcnt +=1
            if tpcnt == 1:
                tot = int(wlh[1:],16)
            if tpcnt == 3:
                intgrl = str(int(str(wrh[1:])+intgrl,16))#intgrl = str(wlh[1:])+intgrl,16 #str(int(str(wlh[1:])+intgrl,16))
            if tpcnt == 5:
                intgrlN = str(int(str(wlh[1:])+intgrlN,16))
            if wrh[0] == "C":
                tpcnt +=1
            if tpcnt == 2:
                intgrl = str(wrh[1:]) #str(wrh[1:])
            if tpcnt == 4:
                intgrlN = str(wrh[1:])
            if tpcnt == 6:
                amp = int(wrh[1:],16)
                if(amp!=0 and tot!=0 and frame>0):
                    #tplistamp.append([channel, timetick, int(amp)])
                    #tplisttot.append([channel, timetick, int(tot)])
                    tplistint.append([frame, femm, int(larchnlNum), timetick, int(intgrl), tot, amp])
                    #print(tplistint)
                    #print("TOT = " + str(tot))
                    #print("INT = " + str(intgrl))
                    #print("INTN = " + str(intgrlN))
                    #print("AMP = " + str(amp))
                    #print("Frame:" + str(frame))
                    #print("FEM:"+str(femm))
                    #mainlist.append([frame,femm,channel, timetick,intgrl,tot,amp])
                    tpcnt = 0
                    tot = 0
                    intgrl = ""
                    intgrlN = ""
                    amp = 0
                    nsamps = ""


json.dump(tplistint, outf)


