#Decode the binary supernova (SN) file and plot the trigger primitives calculated from SN ROIs in channel vs time tick. Calculates TPs for a particular frame number which can be chosen in the starting (using variable "fr"). To plot Time Over Threshold or max. amplitude, change the setting inplotting section
#D.Kalra (dkalra@nevis.columbi.edu) (dk3172@columbia.edu) (June 22, 2021)                                      

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
f = open("SN_0026592","r")
scale = 16 ## equals to hexadecimal                   
fr=780                     ##frame number to compare
#whichTP="tplisttot"
num_of_bits = 16

tot = 0
intgrl = 0
intgrlN = 0
nsamps = 0
hdrcnt = 0
amp = 0
N = 11
framelist=[]
channellist=[]
timelist=[]
tplistint=[]
tplistamp=[]
tplisttot=[]

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
                            #print("FRAMENUM = " + str(int(wrh[1:], 16)) + str(int(wlh[1:], 16)))
                          #  framelist.append(str(frame))
                            #print("Frame List: "+str(framelist))
        #                       print("FRAME NUM = " + str(wrh[1:]) + str(wlh[1:]))                                                                                                  
                elif wf == "E0000000":
                        hdrcnt = 0
                else:
                        if wrh[0] == "1":
                                #For a particular Frame Number,
                                #if (frame==fr):
                                #channel is in lower 6 bits
                                channel=int(wrb[-6:],2)
                                #channellist.append(channel)
                                tot = 0
                                intgrl = 0
                                intgrlN = 0
                                amp = 0
                                nsamps = 0

                        elif wrb[0:2] == "01":
                                #if (frame==fr):
                                        #timetick is in lower 14 bits
                                timetick=int(wrb[2:],2)
                                #timelist.append(timetick)                                        
                                tot = 0
                                intgrl = 0
                                intgrlN = 0
                                amp = 0
                                nsamps = 0
                        elif wrh[0] == "2":
                                #For non-huffman coded ADC words, ADC value in lower 12 bits
                                #if (frame==fr):
                                tot+=1
                                if int(wrb[-12:],2)>amp:
                                        amp = int(wrb[-12:],2)
                                intgrl += int(wrb[-12:],2)
                                if nsamps<=N:
                                        intgrlN += int(wrb[-12:],2)
                                        nsamps +=1


                        elif wrh[0] == "3":
                                #ADC value of the last sample of  waveform packet in 0:11 bits
                                #if(frame==fr):
                               # value1=(wrb[-12:],2)
                                        #print("value 0011 is:"+str(value1))
                                tot+=1
                                if int(wrb[-12:],2)>amp:
                                        amp = int(wrb[-12:],2)
                                intgrl += int(wrb[-12:],2)
                                if nsamps<=N:
                                        intgrlN += int(wrb[-12:],2)
                                        nsamps += 1
                                print("TOT = " + str(tot))
                                print("INT = " + str(intgrl))
                                print("INTN = " + str(intgrlN))
                                print("AMP = " + str(amp))
                                if(frame==fr):
                                        tplistamp.append([channel, timetick, amp])
                                        tplistint.append([channel, timetick, intgrl])
                                        tplisttot.append([channel, timetick, tot])
 
                        if wlh[0] == "1":
                                #if (frame==fr):
                                channel=int(wlb[-6:],2)
                                tot = 0
                                intgrl = 0
                                intgrlN = 0
                                amp = 0
                                nsamps = 0
                        elif wlb[0:2] == "01":
                                #if (frame==fr):
                                timetick=int(wlb[2:],2)                                    
                                tot = 0
                                intgrl = 0
                                intgrlN = 0
                                amp = 0
                                nsamps = 0
                        elif wlh[0] == "2":
                                #if (frame==fr):
                                tot+=1
                                if int(wlb[-12:],2)>amp:
                                        amp = int(wlb[-12:],2)
                                intgrl += int(wlb[-12:],2)
                                        #if nsamps<=N:
                                         #       intgrlN += int(wlb[-12:],2)
                                          #      nsamps += 1


                        elif wlh[0] == "3":
                                #if(frame==fr):
                                tot+=1
                                if int(wlb[-12:],2)>amp:
                                        amp = int(wlb[-12:],2)
                                intgrl += int(wlb[-12:],2)
                                if(frame==fr):
                                        tplistamp.append([channel, timetick, amp])
                                        tplistint.append([channel, timetick, intgrl])
                                        tplisttot.append([channel, timetick, tot])



#print(" TPList: "+str(tplistint))
print("Length of TPList: "+str(len(tplistint)))
#print("Length of intgrl TPList: "+str(len(tp2list)))
#print("Length of tot TPList: "+str(len(tp3list)))
#print("TP tot list:= "+str(tp3list[0]))


xlist_even=[]
ylist_even=[]
zlist_even=[]
xlist_odd=[]
ylist_odd=[]
zlist_odd=[]

for pl in tplistint:
        if (pl[0]>30 and pl[0]<64):
                xlist_even.append(pl[0])
                ylist_even.append(pl[1])
                zlist_even.append(pl[2])
                #print(xlist_even)
                #print(ylist_even)
                #print(zlist_even)

cm = plt.cm.get_cmap('Dark2')
tp_adc=plt.scatter(xlist_even, ylist_even, c=zlist_even,vmin=min(zlist_even),vmax=max(zlist_even), s=20, cmap=cm, label="collection wire data")
plt.colorbar(tp_adc)
#plt.ylim(2000,4000)                                                                                    
plt.xlabel("Channel")                                                                                  
plt.ylabel("Time ticks")                                                                               
plt.title("Frame"+str(fr)+", TPs from SN [Collection Plane Only]")                                                
plt.show()




