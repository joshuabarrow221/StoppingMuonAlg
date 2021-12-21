#Code to produce TPs from SN hex-formatted file and write the TPS in hex-file in specified format
#Code developed by Daisy Kalra (dkalra@nevis.columbia.edu) October 25, 2020
import matplotlib.pyplot as plt
import matplotlib.colors as clrs
import matplotlib.cm as cm
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import matplotlib
import numpy as np
import csv
import operator
import sys

#Command to convert binary to hex-dump file: hexdump -v -e '8/4 "%08X ""\n"' BINARYFILE 
#input file name: hexdump from SN binary
#f=open("hexnominal28554","r")
f=open(sys.argv[1],"r")

#output file name: to write TPs
#outf = open("nominal28554","w")  
outf=open(sys.argv[2],"w")

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
hdrcnt1=0
femcnt=0
amp = 0
N = 11
channel=0
larchnlNum=0
timetick=0
larchnlNumInd=0
larchnlNumCol=0
framelist=[]
framelistfull=[]
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
minFrame=0
frmcntr=0
chnholdR=0#"A"
chnholdL=0#"A"
timeholdR=0#"A"
timeholdL=0#"A"
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
tmin2=0
tdiff2=tmax-tmin
tDiff2=tdrift-tdiff2
tdiffa=tmax-tmin
tDiffa=tdrift-tdiffa
ntdlist=[]
driftincrement=True
FirstTime=True

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
cratenum=2
CrateID=2

minFrame=0
changeMin=False
channellist2=[]
min1=1
stitchedTP2=[]
goToNextFrame=False
tminp=0

intgrl1 = 0
intgrl1 = 0
#INTGRL1 = 0
zintgrl = 0
hintgrl = 0
INTGRL = 0

ztot = 0
htot = 0
TOT = 0

zamp = 0
hamp = 0
AMP = 0

zintgrl1 = 0
hintgrl1 = 0
INTGRL1 = 0

ztot1 = 0
htot1 = 0
TOT1 = 0

zamp1 = 0
hamp1 = 0
AMP1 = 0

zintgrl2 = 0
hintgrl2 = 0
INTGRL2 = 0

ztot2 = 0
htot2 = 0
TOT2 = 0

zamp2 = 0
hamp2 = 0
AMP2 = 0

zintgrl3 = 0
hintgrl3 = 0
INTGRL3 = 0

ztot3 = 0
htot3 = 0
TOT3 = 0

zamp3 = 0
hamp3 = 0
AMP3 = 0

TOTlist = []
AMPlist = []
INTGRLlist = []


TOTlist1 = []
AMPlist1 = []
INTGRLlist1 = []
conststr1 = "C"
conststr = "C"

#chtimeword1 = 0
#chtimeword = 0


#with open('test', 'w') as outf:

#outf = open("nominal28554","w")

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
                if hdrcnt == 1:
                    #print("hdrcnt1: "+str(wf))
                    outf.write(wf+' ' )
                    #outf.write('')
                if hdrcnt == 3:
                    #print("hdrcnt3: "+str(wf))
                    outf.write(wf+' ')
                if hdrcnt == 4:
                    #print("hdrcnt4: "+str(wf))
                    outf.write(wf+' ')
                if hdrcnt == 5:
                    #print("hdrcnt5: "+str(wf))
                    outf.write(wf+' ')
                    frame=int(wrh[1:], 16) + int(wlh[1:], 16)
                    hexframe =  hex(frame)
                    #print("Frame is:" +str(frame))
                    #print("Hex Frame is:" + str(hexframe))
                    framelistfull.append(frame)
                if hdrcnt == 6:
                    #print("hdrcnt6: "+str(wf))
                    outf.write(wf+' ')
                if hdrcnt == 7:
                    #print("hdrcnt7: "+str(wf))
                    outf.write(wf+' ')

                   
            if (wf[0:2] == "F1" and wf[4:8] == "FFFF"):
                femm=int(wlb[-5:], 2)
                outf.write(wf+' ')
            elif wf == "E0000000":
                outf.write(wf+' ')
                hdrcnt = 0
            else:
                if wrh[0] == "1":
                    outf.write(wf+' ')
                    channel=int(wrb[-6:],2)
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
                    outf.write(wf+' ')  
                    timetick=int(wrb[2:],2)
                    timelist.append(timetick)
                    tot = 0
                    intgrl = 0
                    amp=0

                elif (wrh[0] == "2"):
                    tot+=1
                    adc=int(wrb[-12:],2)
                    if int(wrb[-12:],2)>amp:
                        amp = int(wrb[-12:],2)
                    intgrl += int(wrb[-12:],2)

                elif (wrh[0] == "3"):  
                    tot+=1                                                                             
                    adc=int(wrb[-12:],2)                                                   
                    if int(wrb[-12:],2)>amp:                                                              
                        amp = int(wrb[-12:],2)                                                        
                    intgrl += int(wrb[-12:],2)
                    tplistint.append([frame, femm, channel,int(larchnlNum), timetick, int(intgrl), int(tot), int(amp)])
                    conststra = "C000"
                    htot = hex(tot).upper().lstrip("0X")
                    ztot = str(htot).zfill(3)
                    TOT = conststr+ztot
                    #TOTlist.append(TOT)
                    hamp = hex(amp).upper().lstrip("0X")
                    zamp = str(hamp).zfill(3)
                    AMP = conststr+zamp
                    #AMPlist.append(AMP)
                    hintgrl = hex(intgrl).upper().lstrip("0X")
                    zintgrl = str(hintgrl).zfill(3)
                    INTGRL = conststr+zintgrl
                    outf.write(TOT+AMP+' ')
                    #print("right hex 3 intgrl 16-bit: "+str(INTGRL))
                    if (len(INTGRL)==4):
                        INTGRL = conststra+INTGRL
                        outf.write(INTGRL+' ')
                        INTGRLlist.append(INTGRL)
                        #print("Right hex 3 intgrl list: "+str(INTGRLlist))

                    elif (len(INTGRL)==5):
                        first = "C00"
                        second = INTGRL[1:2]
                        third = "C"
                        four = INTGRL[2:5]
                        INTGRL = first+second+third+four
                        outf.write(INTGRL+' ')
                        INTGRLlist.append(INTGRL)
                        #print("Right hex 3 intgrl list: "+str(INTGRLlist))
                    elif(len(INTGRL)==6):
                        first = "C0"
                        second = INTGRL[1:3]
                        third = "C"
                        four = INTGRL[3:6]
                        INTGRL = first+second+third+four
                        outf.write(INTGRL+' ')
                        INTGRLlist.append(INTGRL)

                    elif(len(INTGRL)==7):
                        first = "C"
                        second = INTGRL[1:4]
                        third = "C"
                        four = INTGRL[4:7]
                        INTGRL = first+second+third+four
                        outf.write(INTGRL+' ')
                        INTGRLlist.append(INTGRL)


                if wlh[0] == "1":
                    #print("chnl left: "+str(wf))
                    outf.write(wf+' ')
                    channel=int(wlb[-6:],2)
                    #print("left channel: "+str(channel))
                    larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                    if (channel >= 0 and channel < 32):
                        larchnlNumInd =str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                    else:
                        larchnlNumCol =str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                    tot=0
                    intgrl=0
                    amp=0

                elif wlb[0:2] == "01":
                    outf.write(wf+' ')
                    timetick=int(wlb[2:],2)
                    tot = 0
                    intgrl = 0
                    amp=0

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
                    tplistint.append([frame, femm, channel,int(larchnlNum), timetick, int(intgrl), int(tot), int(amp)])
                    conststra = "C000"
                    htot = hex(tot).upper().lstrip("0X")
                    ztot = str(htot).zfill(3)
                    TOT = conststr+ztot
                    #TOTlist.append(TOT)
                    hamp = hex(amp).upper().lstrip("0X")
                    zamp = str(hamp).zfill(3)
                    AMP = conststr+zamp
                    #AMPlist.append(AMP)
                    hintgrl = hex(intgrl).upper().lstrip("0X")
                    zintgrl = str(hintgrl).zfill(3)
                    INTGRL = conststr+zintgrl
                    outf.write(TOT+AMP+' ')
                    #print("left  hex 3 intgrl 16-bit: "+str(INTGRL))
                    if (len(INTGRL)==4):
                        INTGRL = conststra+INTGRL
                        outf.write(INTGRL+' ')                                                                                  
                        INTGRLlist.append(INTGRL)
                        #print("left hex 3 intgrl list: "+str(INTGRLlist))

                    elif (len(INTGRL)==5):
                        first = "C00"
                        second = INTGRL[1:2]
                        third = "C"
                        four = INTGRL[2:5]
                        INTGRL = first+second+third+four
                        outf.write(INTGRL+' ')
                        INTGRLlist.append(INTGRL)
                        #print("left hex 3 intgrl list: "+str(INTGRLlist))

                    elif(len(INTGRL)==6):
                        first = "C0"
                        second = INTGRL[1:3]
                        third = "C"
                        second = INTGRL[1:3]
                        third = "C"
                        four = INTGRL[3:6]
                        INTGRL = first+second+third+four
                        outf.write(INTGRL+' ')
                        INTGRLlist.append(INTGRL)

                    elif(len(INTGRL)==7):
                        first = "C"
                        second = INTGRL[1:4]
                        third = "C"
                        four = INTGRL[4:7]
                        INTGRL = first+second+third+four
                        outf.write(INTGRL+' ')
                        INTGRLlist.append(INTGRL)

print("tplist: "+str(len(tplistint)))

#sed 's/\([^ ]*\) /\1\n/' test | fold -w 63 > test1
