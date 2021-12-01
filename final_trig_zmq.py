import numpy as np
import csv
import operator
#import ROOT
import math

import zmq
import time
import sys
import json
import pandas as pd
import logging

CrateID = 2
'''mainlist = []
mainlistind = []
mainlistcol = []
main        = []'''
#stitchedTP  = inputTP #[]
#self.stitchedTP2  = []
#inputTP=[[2, 4, 32, 2976, 1075, 78844, 19, 1020, 2, 2], [2, 4, 32, 2976, 1075, 28609, 19, 1020, 2, 2], [2, 4, 32, 2976, 1075, 10609, 2, 2417, 2, 2], [2, 4, 33, 2977, 285, 20962, 5, 482, 2, 2], [2, 4, 33, 3075, 285, 32373, 5, 482, 2, 2], [2, 4, 33, 3076, 285, 2373, 0, 2373, 2, 2], [2, 4, 33, 3077, 285, 29154, 7, 482, 2, 2]]
#, [2, 4, 33, 2977, 285, 3303, 7, 482, 2, 2], [2, 4, 33, 2977, 285, 3303, 0, 3303, 2, 2], [2, 4, 33, 2977, 1079, 86585, 21, 569, 2, 2], [2, 4, 33, 2977, 1079, 10757, 21, 569, 2, 2], [2, 4, 33, 2977, 1079, 10757, 2, 2565, 2, 2], [2, 4, 34, 2978, 1088, 70194, 17, 562, 2, 2], [2, 4, 34, 2978, 1088, 8834, 17, 562, 2, 2], [2, 4, 34, 2978, 1088, 8834, 2, 642, 2, 2], [2, 4, 34, 2978, 1139, 8670, 2, 478, 2, 2], [2, 4, 34, 2978, 1139, 955, 2, 478, 2, 2], [2, 4, 34, 2978, 1139, 955, 0, 955, 2, 2], [2, 4, 35, 2979, 305, 8662, 2, 470, 2, 2], [2, 4, 35, 2979, 305, 935, 2, 470, 2, 2], [2, 4, 35, 2979, 305, 935, 0, 935, 2, 2], [2, 4, 35, 2979, 1091, 78634, 19, 810, 2, 2], [2, 4, 35, 2979, 1091, 10163, 19, 810, 2, 2], [2, 4, 35, 2979, 1091, 10163, 2, 1971,2, 2], [2, 4, 36, 2980, 1102, 87011, 21, 995, 2, 2], [2, 4, 36, 2980, 1102, 11219, 21, 995, 2, 2], [2, 4, 36, 2980, 1102, 11219, 2, 3027, 2, 2]]
'''thisFrameList = []
framelist = []
firsthit = []
first_index = []
tdlist = []'''

#inputTP = sorted(inputTP, key = operator.itemgetter(3))

colstart2 = 2976
colend2 = 3456
colend = 3456
boxwidch2 = 96
boxlistch2 = range(colstart2,colend2+boxwidch2,boxwidch2)
boxlistchlen2 = len(boxlistch2)
print("box list ch: "+str(boxlistch2) + " , len: "+str(boxlistchlen2))
#stitchedTPlistlen = len(self.stitchedTP)-1
#stitchedTPlistlen = len(inputTP)-1
#print("Input tp len:" +str(stitchedTPlistlen))
'''templist =[]
sublist = []'''
boxchcnt = 1
braggE = 27500
maxTP = 0
#firsthit = []
#filtertdlist = []
maxadctrigtot2=0
trigtot = 0
beforeangletrigtot=0
#peaklist = []
#contiguous_tolerance = 3                                                                             
hitE = 0
time_diff = 30 #time difference between hits when checking for contiguous mu hits in adjacent channels
deadwidthscale = 8#scale of how wide time search gets after dead jumps
slopecm_scale = 0.04/0.3#time ticks to cm = 1/25, channels to cm = 0.3                                                                               
braggE = 27500
tracklen = 26
kinkangle = 10#not being used currently, but should be minimum angle to successfully trigger                                                                
hitfound = False
frontfound = False
frontslope_top = 0
backslope_top = 0
frontslope_mid = 0
backslope_mid = 0
frontslope_bottom = 0
backslope_bottom = 0
temp_t = 0
ch = 0
deadcnt = 0
slope = 0
p = 0
n = 0
sf = 0 #TP to calculate slope forward                                                                                                                      
sb = 0 #TP to calculate slope backward                                                                                                                     
braggcnt = 0
t_jt = 0
t_jb = 0
t_pt = 0
t_pb = 0
horiz_noise_cnt = 0
horiz_tolerance = 8
horiz_tb = 0
horiz_tt = 0
#        first_index = []
deadch = []
d = open("MCC9_channel_list.txt","r")
for l in d:
    if int(l.split()[1]) < 2:
        deadch.append(0)
    else:
        deadch.append(1)
        
#if len(templist)>0:
    #maxTP = max(templist,key=operator.itemgetter(5))
    #if (maxTP[5]>braggE):
        #print("here")
        #firsthit.append(maxTP)
        #print("first hit: "+str(firsthit))
'''inputTPhold = []
templist = []
boxchcnt = 1'''

#zmq setup
context = zmq.Context()
socket = context.socket(zmq.SUB)
osocket = context.socket(zmq.PUB)

port =6665 #subscribe to messages from stitching code
port1=6666 #publish messages to trig. supervisor
socket.connect("tcp://127.0.0.1:%s" % port)
socket.setsockopt(zmq.SUBSCRIBE, b"")
osocket.bind("tcp://127.0.0.1:%s" % port1)

json_message_type = 0x4a534f4e

now = time.time()
print("time_start:", now)

while True:

    dat = socket.recv_json()
    inputTP = json.loads(dat)
    print("receiving...")
    now1 = time.time()
    inputTP = sorted(inputTP, key = operator.itemgetter(3))
    #d1 = pd.DataFrame(jdat)
    #start = datetime.now()
    stitchedTPlistlen = len(inputTP)-1
    inputTPhold = []
    templist = []
    boxchcnt = 1
    peaklist = []
    mainlist = []
    mainlistind = []
    mainlistcol = []
    main        = []
    thisFrameList = []
    framelist = []
    firsthit = []
    first_index = []
    tdlist = []
    templist =[]
    sublist = []
    filtertdlist = []
    checkfakelist = []
    print("time data receiving: ", now1)
    #for n in np.arange(len(self.stitchedTP)):
    for n in np.arange(len(inputTP)):
        #print("input TP: "+str(inputTP[n]) + "n is: "+ str(n))
        if (inputTP[n][3]> boxlistch2[boxchcnt] or n==stitchedTPlistlen):
            #inputTPhold.append(inputTP[n])
            #print("HoldTP: " +str(inputTPhold))
            if len(templist)==0:
                inputTPhold.append(inputTP[n])
                #print("HoldTP: " +str(inputTPhold))
                while inputTP[n][3] > boxlistch2[boxchcnt]:
                    boxchcnt +=1
                    #print("boxcnt is: "+str(boxchcnt) + "boxlistch2: "+ str(boxlistch2[boxchcnt]))
            else:#
                #print("len of tmplist in else: "+str(len(templist)))
                inputTPhold.append(inputTP[n])
                #print("HoldTP: " +str(inputTPhold))
                if len(templist)>0:
                    maxTP = max(templist,key=operator.itemgetter(5))
                    #print("MaxTP: "+str(maxTP))
                    if (maxTP[5]>braggE):
                        firsthit.append(maxTP)
                        #print("first hit: "+str(firsthit))
                        #first_index.append(n)
                        #print("First index : "+str(first_index))
                        #print("len of templist: "+str(len(templist)))
                        templist = []
                        #print("len of templist: "+str(len(templist)))

        if (inputTP[n][3] <= boxlistch2[boxchcnt]):
            #print("check for holdTP: "+str(inputTPhold))
            if (inputTPhold!=[]):
                templist.extend(inputTPhold)
                inputTPhold=[]
            templist.append(inputTP[n])
            #print("templist: "+str(templist) + ", and len: "+str(len(templist)))



    #print("First hit: "+str(firsthit))                                                                                                                      
    for h in firsthit:
        #print("Enter first hit loop")
        for z in np.arange(len(inputTP)):
            #print("Enter loop on input TP")
            if h == inputTP[z]:
                first_index.append(z) 
                #print("First index : "+str(first_index))

    if (firsthit!=[]):
        #print("Check FirstHit: "+str(firsthit))
        for i,Q in zip(firsthit,first_index):
            #print("i and Q: "+str(i) + " , " + str(Q))
            ch = i[3] #current channel in loop
            deadcnt = 0 #number of deadchannels we've skipped  
            slope = 0 #needed for deadchannel skipping
            p = i #previous hit confirmed in track in previous channel                                                                                                                                    
            n = i #current hit considered best fit for next hit in track in channel after p                                                                                                               
            sf = i #TP to calculate slope forward                                                                                                                                                         
            sb = i #TP to calculate slope backward                                                                                                                                                       
            time_max = p[4]+p[6]
            time_min = p[4]
            braggcnt = 0
            frontfound = False
            hitfound = False
            frontslope_top = 0
            backslope_top = 0
            frontslope_mid = 0
            backslope_mid = 0
            frontslope_bottom = 0
            backslope_bottom = 0
            temp_t = 0
            horiz_noise_cnt = 0
            horiz_tb = 0
            horiz_tt = 0
            #frame,femm,channel,int(larchnlNumCol), timetick,int(intgrl), tot, amp, td, crateid --> inputTP
            for q in np.arange(Q,len(inputTP),1):
                if (frontfound == True):
                    break
                j = inputTP[q]
                #print("J is: "+str(j) + "j0 is: "+str(j[3]) + "Ch: "+str(ch))
                if (j[3]>=(ch+2)):
                    #print("Ch>ch+2")
                    ch = n[3]
                    if (hitfound==False):#check for missed hits
                        peaklist=[]
                        peaklist.append(i)
                        for it1 in peaklist:
                            if(len(it1)==10):
                                it1.append(0)
                        #print(len(peaklist))
                        TC = json.dumps(peaklist)
                        osocket.send_json(TC)
                        t1 = time.time()
                        #print("t1:", t1)
                        checkfakelist.append(peaklist)
                        #print("Peaklist: "+str(peaklist))
                        break
                    if (deadch[ch+1] == 0 and j[3]!=ch+1):
                        if(p[3]==i[3]):
                            slope = 0
                        elif(p[3]==sf[3]):
                            slope = float(p[4]+p[6]/2-i[4]-i[6]/2)/float(p[3]-i[3])
                        else:
                            slope = float(p[4]+p[6]/2-sf[4]-sf[6]/2)/float(p[3]-sf[3])
                        deadcnt = 0
                        while (deadch[ch+1]==0 and (ch+1)<colend):
                            ch+=1
                            deadcnt+=1
                            #print("Skipping through dead channel:"+str(ch))
                        p[4]=p[4]+np.floor(float(slope)*float(deadcnt))
                    if (hitfound==True):
                        braggcnt+=1
                        if (braggcnt == 3):
                            sf=n
                        if (braggcnt >= tracklen/8):
                            frontfound = True
                            #print("FRONT found !!!!!!")
                            frontslope_top = float(n[4]+n[6]-sf[4]-sf[6])/float(n[3]-sf[3])
                            frontslope_mid = float(n[4]+n[6]/2-sf[4]-sf[6]/2)/float(n[3]-sf[3])
                            frontslope_bottom = float(n[4]-sf[4])/float(n[3]-sf[3])
                        p = n
                    #else:
                        #peaklist=[]
                        #peaklist.append(i)
                        #for item2 in peaklist:
                            #item2.append(0)
                        #print("Peaklist:" +str(peaklist))
                    hitfound = False
                    t_jt = 0
                    t_jb = 0
                    t_pt = 0
                    t_pb = 0
                if(j[3] == ch+1):
                    #print("Check2")
                    t_jt = j[4]+j[6]
                    t_jb = j[4]
                    t_pt = p[4]+p[6]
                    t_pb = p[4]
                    if ( (t_jb>=t_pb and t_jb<=t_pt) or (t_jt>=t_pb and t_jt<=t_pt) or (t_pt<=t_jt and t_pb>=t_jb)) :
                        #print("Check3")
                        if (horiz_noise_cnt == 0):
                            #print("Check3a")
                            horiz_tb = t_pb
                            horiz_tt = t_pt
                        if (j[3]==n[3]):
                            peaklist=[]
                            peaklist.append(i)
                            for it1 in peaklist:
                                if(len(it1)==10):
                                    it1.append(0)
                            #print(len(peaklist))
                            TC = json.dumps(peaklist)
                            osocket.send_json(TC)
                            t2 = time.time()
                            #print("t2 :", t2)
                            checkfakelist.append(peaklist)
                            #print("Peaklist: "+str(peaklist))
                            break
                        hitfound = True
                        n = j

                        if (abs(t_jb - horiz_tb) <=1) or (abs(t_jt - horiz_tt) <=1):
                            horiz_noise_cnt+=1
                            #print("Check3c")
                            if (horiz_noise_cnt>horiz_tolerance):
                                #print("Check3d")
                                peaklist=[]
                                peaklist.append(i)
                                for item in peaklist:
                                    #print("item"+str(item))                                                                                                        
                                    if(len(item)==10):
                                        item.append(0)
                                #print(len(peaklist))
                                TC = json.dumps(peaklist)
                                osocket.send_json(TC)
                                t3 = time.time()
                                #print("t3 :",t3)
                                checkfakelist.append(peaklist)
                                #print("Peaklist: "+str(peaklist))
                                break
                            else:
                                #peaklist=[]
                                #peaklist.append(i)
                                #for item in peaklist:
                                    #print("item"+str(item))
                                    #if(len(item)==10):
                                        #item.append(0)
                                #print(len(peaklist))
                                    
                                #TC = json.dumps(peaklist)
                                #osocket.send_json(TC)
                                #print("Peaklist: "+str(peaklist))
                                horiz_noise_cnt = 0
                            if (t_jt > time_max):
                                time_max = t_jt
                            if (t_jb < time_min):
                                time_min = t_jt

                #if(j[3] == ch):
                    #peaklist=[]
                    #peaklist.append(i)
                    #for item in peaklist:
                        #item.append(0)
                    #if(len(peaklist)==10):
                    #print("Peaklist: "+str(peaklist))
                
                    

            ch = i[3]
            p = i #previous hit confirmed in track in previous channel                                                                                                                                       
            n = i #current hit considered best fit for next hit in track in channel after p                                                                                                                 
            t_jt = 0
            t_jb = 0
            t_pt = 0
            t_pb = 0
            deadcnt = 0 #number of deadchannels we've skipped                                                                                                  
            slope = 0 #needed for deadchannel skipping                                                                                                                                                     
            ##print("self.firsthit = " +str(self.firsthit))                                                                                                                                                 
            #sf = i #TP to calculate slope forward                                                                                                                                                          
            #sb = i #TP to calculate slope backward                                                                                                                                                             
            hitfound = False
            temp_t = 0
            horiz_noise_cnt = 0
            horiz_tb = 0
            horiz_tt = 0
            if (frontfound == True):
                for q in np.arange(Q,-1,-1):
                    j = inputTP[q]
                    if(j[3]<=(ch-2)):
                        ch = n[3]
                        if (hitfound==False):
                            peaklist=[]
                            peaklist.append(i)
                            for item in peaklist:
                                if(len(item)==10):
                                    item.append(0)
                            #print(len(peaklist))
                            TC = json.dumps(peaklist)
                            osocket.send_json(TC)
                            t4 = time.time()
                            #print("t4: ", t4)
                            checkfakelist.append(peaklist)
                            #print("Peaklist: "+str(peaklist))
                            break
                        if (deadch[ch-1] == 0 and j[3]!=ch-1):
                            if(p[3]==i[3]):
                                slope = 0
                            elif(p[3]==sb[3]):
                                slope = float(p[4]+p[6]/2-i[4]-i[6]/2)/float(p[3]-i[3])

                            else:
                                slope = float(p[4]+p[6]/2-sb[4]-sb[6]/2)/float(p[3]-sb[3])

                            deadcnt = 0
                            while (deadch[ch-1]==0 and (ch-1)>colstart):
                                ch-=1
                                #print("bkwrd loop Skipping through dead channel:"+str(ch))
                                deadcnt+=1
                            #            print("bkwrd deadcnt =" + str(deadcnt))                                                                                                              
                            p[4]=p[4]-np.floor(float(slope)*float(deadcnt))
                        if (hitfound==True):
                            braggcnt+=1
                            if (braggcnt == tracklen/2+3):
                                sb = n
                            if (braggcnt >= tracklen):
                                backslope_top = float(n[4]+n[6]-sb[4]-sb[6])/float(n[3]-sb[3])
                                backslope_mid = float(n[4]+n[6]/2-sb[4]-sb[6]/2)/float(n[3]-sb[3])
                                backslope_bottom = float(n[4]-sb[4])/float(n[3]-sb[3])
                                #print("slopes back: "+str(backslope_top)+" , "+str(backslope_mid)+" , "+str(backslope_bottom))
                                frontangle_top = math.degrees(math.atan(slopecm_scale*float(frontslope_top)))
                                backangle_top = math.degrees(math.atan(slopecm_scale*float(backslope_top)))
                                frontangle_mid = math.degrees(math.atan(slopecm_scale*float(frontslope_mid)))
                                backangle_mid = math.degrees(math.atan(slopecm_scale*float(backslope_mid)))
                                frontangle_bottom = math.degrees(math.atan(slopecm_scale*float(frontslope_bottom)))
                                backangle_bottom = math.degrees(math.atan(slopecm_scale*float(backslope_bottom)))
                                #if (abs(frontangle_mid-backangle_mid)>0 and abs(frontangle_top-backangle_top)>0 and abs(frontangle_bottom-backangle_bottom)>0):
                                    #beforeangletrigtot += 1
                                    #print("Angle > 0")
                                if (abs(frontangle_mid-backangle_mid)>30 and abs(frontangle_top-backangle_top)>30 and abs(frontangle_bottom-backangle_bottom)>30):
                                    trigtot += 1
                                    #print("Angle > 30")
                                    #print("Bragg peak TP found at " +str(i))
                                    peaklist=[]
                                    peaklist.append(i)
                                    for item in peaklist:
                                        if(len(item)==10):
                                            item.append(1)
                                    #print(len(peaklist))
                                    TC = json.dumps(peaklist)
                                    osocket.send_json(TC)
                                    t5 = time.time()
                                    #print("t5 :",t5)
                                    checkfakelist.append(peaklist)
                                    #print("Peaklist: "+str(peaklist))
                                    break
                                else:
                                    for item in peaklist:
                                        if(len(item)==10):
                                            item.append(0)
                                    #print(len(peaklist))
                                    TC = json.dumps(peaklist)
                                    osocket.send_json(TC)
                                    t6 = time.time()
                                    #print("t6 :", t6)
                                    checkfakelist.append(peaklist)
                                    #print("Peaklist: "+str(peaklist))
                                    break
                            p = n
                        #else:   
                            #peaklist=[]
                            #peaklist.append(i)
                            #for item3 in peaklist:
                                #item3.append(0)
                            #print("Peaklist: "+str(peaklist))
                        hitfound = False
                        t_jt = 0
                        t_jb = 0
                        t_pt = 0
                        t_pb = 0
                    if(j[3]==ch-1):
                        t_jt = j[4]+j[6]
                        t_jb = j[4]
                        t_pt = p[4]+p[6]
                        t_pb = p[4]
                        if ( (t_jb>=t_pb and t_jb<=t_pt) or (t_jt>=t_pb and t_jt<=t_pt) or (t_pt<=t_jt and t_pb>=t_jb)) :
                            if (horiz_noise_cnt == 0):
                                horiz_tb = t_pb
                                horiz_tt = t_pt
                            if (j[3]==n[3]):
                                break
                            hitfound=True
                            n = j
                            if (abs(t_jb - horiz_tb) <=1) or (abs(t_jt - horiz_tt) <=1):
                                horiz_noise_cnt+=1
                                if (horiz_noise_cnt>horiz_tolerance):
                                    peaklist=[]
                                    peaklist.append(i)
                                    for item in peaklist:
                                        if(len(item)==10):
                                            item.append(0)
                                    #print(len(peaklist))
                                    TC = json.dumps(peaklist)
                                    osocket.send_json(TC)
                                    t7 = time.time()
                                    #print("t7 :", t7)
                                    checkfakelist.append(peaklist)
                                    #print("Peaklist: "+str(peaklist))
                                    break
                            else:
                                horiz_noise_cnt = 0
                            if (t_jt > time_max):
                                time_max = t_jt
                            if (t_jb < time_min):
                                time_min = t_jt

    if(len(checkfakelist)!=5):
        peaklist=[]
        peaklist.append(i)
        for item in peaklist:
            if(len(item)==10):
                item.append(0)
        TC = json.dumps(peaklist)
        #checkfakelist.append(peaklist)
        osocket.send_json(TC)
        #print(“Peaklist: “+str(peaklist))
        #print("Peaklist: "+str(peaklist))
    checkfakelist.clear()
    time_ = time.time()
    print("time per 5 TC :", time_)
    time_final = time_ - now
    print ("time stamp since beginning:", time_final)
    #print("time stamp since message received ", time_loop)
    time_loop = time_ - now1
    print("time stamp since message received ", time_loop)
    
    peaklist.clear()
