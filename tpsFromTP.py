#Decode the binary trigger primitive file and plot the trigger primitives in channel vs time tick.Code to test the uBooNE data runs. Channel mapping is also implemented here.   
#D.Kalra (dkalra@nevis.columbi.edu) (dk3172@columbia.edu) (June 22, 2021)

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

#Command to convert binary to hex-dump file: hexdump -v -e '8/4 "%08X ""\n"' BINARYFILE 
f = open("TP_multiFEMs_fakedata_test","r")
#f = open("TP_0026678","r")  #input is hex-dump file


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
chlarchlist=[]
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
                frame = int(wrh[1:], 16) + int(wlh[1:], 16)
                framelist.append(frame)
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
                #larchnlNum = str(chMap.CrateFEMCh2PlaneWire(cratenum,femm, channel))
                #print("FRAME NUM = " + str(int(frmb[0:18]+wlb[4:10],2)))
                #print("CHNL lh= "+str(wlh)+"channel is: " + str(channel))
                #print("binary = " + str(wlb))
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
                timetick=int(wlb[2:],2)
                timelist.append(timetick)
                #print("TIMETICK lb = " + str(timetick))
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
                if(amp!=0 and tot!=0 and intgrl!=0):
                    #tplistamp.append([channel, timetick, int(amp)])
                    #tplisttot.append([channel, timetick, int(tot)])
                    tplistint.append([frame, femm, channel,int(larchnlNum), timetick, int(intgrl), int(tot), int(amp)])
                    #print("TOT = " + str(tot))
                    #print("INT = " + str(intgrl))
                    #print("INTN = " + str(intgrlN))
                    #print("AMP = " + str(amp))
                    #print("Frame:" + str(frame))
                    #print("FEM:"+str(femm))
                    #mainlist.append([frame,femm,channel, timetick,intgrl,tot,amp])
                    tpcnt = 0
                    tot = ""
                    intgrl = ""
                    intgrlN = ""
                    amp = ""
                    nsamps = ""
    

#print(framelist)
#print(femlist)#
#print(len(channellist))
#print(channellist)
#print(chlarchlist)
#print(len(channellist))
##print(len(chlarchlist))
#print(len(timelist))

#print(len(tplistint))
#print(tplistint)
#print(len(mainlist))
#print(len(mainlist[0]))
#print(mainlist[0])
#print(mainlist[1])
#print(mainlist[10])
#print(mainlist[15])

xlist=[]
ylist=[]
zlist=[]


frmNUM=2
femNUM=5
##tplistint.append([frame, femm, channel, timetick, int(intgrl), int(tot), int(amp)])
for content in tplistint:
    if (content[0]==frmNUM):
        xlist.append(content[2])
        ylist.append(content[4])
        zlist.append(content[5])
    
#print("XList:"+str(xlist))

#print(len(tplistint))
print(len(xlist))
print(len(ylist))
print(len(zlist))
#print(xlist[0])
#print(xlist[1])

my_cmap = plt.cm.get_cmap('viridis')
tp_adc=plt.scatter(xlist, ylist, c=zlist, s=20, cmap=my_cmap)
#tp_adc=plt.scatter(mainlist[2],mainlist[3])
plt.colorbar(tp_adc)
plt.xlabel("LArSoft Channel")                                                 
plt.ylabel("Time ticks")
#plt.xlim(2210,2260) 
#print("hereeeeeeee")
#plt.title("Frame "+str(frmNUM)+", FEM-"+str(femNUM)+", TP: ROI integral, NominalRun")               
plt.title("Frame "+str(frmNUM)+",TP: ROI integral, Modif.Conf.Run")
plt.show()
