#code to run Trigger Algorithm which takes Stitched TP as input list
#D.Kalra dkalra@nevis.columbia.edu 
import numpy as np
import csv
import operator
import ROOT
import math

CrateID = 2
mainlist = []
mainlistind = []
mainlistcol = []
main        = []
#stitchedTP  = inputTP #[]
#self.stitchedTP2  = []
inputTP=[[2, 4, 32, 2976, 1075, 78844, 19, 1020, 2, 2], [2, 4, 32, 2976, 1075, 10609, 19, 1020, 2, 2], [2, 4, 32, 2976, 1075, 10609, 2, 2417, 2, 2], [2, 4, 33, 2977, 285, 20962, 5, 482, 2, 2], [2, 4, 33, 2977, 285, 2373, 5, 482, 2, 2], [2, 4, 33, 2977, 285, 2373, 0, 2373, 2, 2], [2, 4, 33, 2977, 285, 29154, 7, 482, 2, 2], [2, 4, 33, 2977, 285, 3303, 7, 482, 2, 2], [2, 4, 33, 2977, 285, 3303, 0, 3303, 2, 2], [2, 4, 33, 2977, 1079, 86585, 21, 569, 2, 2], [2, 4, 33, 2977, 1079, 10757, 21, 569, 2, 2], [2, 4, 33, 2977, 1079, 10757, 2, 2565, 2, 2], [2, 4, 34, 2978, 1088, 70194, 17, 562, 2, 2], [2, 4, 34, 2978, 1088, 8834, 17, 562, 2, 2], [2, 4, 34, 2978, 1088, 8834, 2, 642, 2, 2], [2, 4, 34, 2978, 1139, 8670, 2, 478, 2, 2], [2, 4, 34, 2978, 1139, 955, 2, 478, 2, 2], [2, 4, 34, 2978, 1139, 955, 0, 955, 2, 2], [2, 4, 35, 2979, 305, 8662, 2, 470, 2, 2], [2, 4, 35, 2979, 305, 935, 2, 470, 2, 2], [2, 4, 35, 2979, 305, 935, 0, 935, 2, 2], [2, 4, 35, 2979, 1091, 78634, 19, 810, 2, 2], [2, 4, 35, 2979, 1091, 10163, 19, 810, 2, 2], [2, 4, 35, 2979, 1091, 10163, 2, 1971,2, 2], [2, 4, 36, 2980, 1102, 87011, 21, 995, 2, 2], [2, 4, 36, 2980, 1102, 11219, 21, 995, 2, 2], [2, 4, 36, 2980, 1102, 11219, 2, 3027, 2, 2]]
thisFrameList = []
framelist = []
firsthit = []
first_index = []
tdlist = []

inputTP = sorted(inputTP, key = operator.itemgetter(3))

colstart2 = 2976
colend2 = 3456
colend = 3456
boxwidch2 = 96
boxlistch2 = range(colstart2,colend2+boxwidch2,boxwidch2)
boxlistchlen2 = len(boxlistch2)
#stitchedTPlistlen = len(self.stitchedTP)-1
stitchedTPlistlen = len(inputTP)-1
templist =[]
sublist = []
boxchcnt = 1
braggE = 2750
maxTP = 0
#firsthit = []
filtertdlist = []
maxadctrigtot2=0
trigtot = 0
beforeangletrigtot=0
peaklist = []
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
        
if len(templist)>0:
    maxTP = max(templist,key=operator.itemgetter(5))
    if (maxTP[5]>braggE):
        firsthit.append(maxTP)
        #print(self.firsthit)
templist = []
boxchcnt = 1
#for n in np.arange(len(self.stitchedTP)):
for n in np.arange(len(inputTP)):
    if (inputTP[n][3]> boxlistch2[boxchcnt] or n==stitchedTPlistlen):
        if len(templist)==0:
            while inputTP[n][3] > boxlistch2[boxchcnt]:
                boxchcnt +=1
                #print("boxcnt is: "+str(boxchcnt))
        else:
            #print("len of tmplist in else: "+str(len(templist)))
            if len(templist)>0:
                maxTP = max(templist,key=operator.itemgetter(5))
                print("MaxTP: "+str(maxTP))
                if (maxTP[5]>braggE):
                    firsthit.append(maxTP)
                    #print(self.firsthit)
                    
            templist = []
    if (inputTP[n][3] <= boxlistch2[boxchcnt]):
        templist.append(inputTP[n])
            

    for h in firsthit:
        for z in np.arange(len(inputTP)):
            if h == inputTP[z]:
                first_index.append(z)
    if (firsthit!=[]):
        for i,Q in zip(firsthit,first_index):
            ch = i[0] #current channel in loop                                                                                                                                                                  
            deadcnt = 0 #number of deadchannels we've skipped                                                                                                                                                   
            slope = 0 #needed for deadchannel skipping                                                                                                                                                          
            p = i #previous hit confirmed in track in previous channel                                                                                                                                          
            n = i #current hit considered best fit for next hit in track in channel after p                                                                                                                     
            sf = i #TP to calculate slope forward                                                                                                                                                               
            sb = i #TP to calculate slope backward                                                                                                                                                              
            time_max = p[1]+p[5]
            time_min = p[1]
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
            #print("Here!!!!!!!!!")
            for q in np.arange(Q,len(inputTP),1):
                #print("Here   111    !!!!!!!!!")
                if (frontfound == True):
                    break
                j = inputTP[q]
                if (j[0]>=(ch+2)):
                    #print("Here  2222   !!!!!!!!!")
                    ch = n[0]
                    if (hitfound==False):#check for missed hits                                                                                                                                                 
                        break
                    if (deadch[ch+1] == 0 and j[0]!=ch+1):
                        if(p[0]==i[0]):
                            slope = 0
                        elif(p[0]==sf[0]):
                            slope = float(p[1]+p[5]/2-i[1]-i[5]/2)/float(p[0]-i[0])
                        else:
                            slope = float(p[1]+p[5]/2-sf[1]-sf[5]/2)/float(p[0]-sf[0])
                        deadcnt = 0
                        while (deadch[ch+1]==0 and (ch+1)<colend):
                            ch+=1
                            deadcnt+=1
                            print("Skipping through dead channel:"+str(ch))
                        p[1]=p[1]+np.floor(float(slope)*float(deadcnt))
                    if (hitfound==True):
                        print("Here  33333   !!!!!!!!!")
                        braggcnt+=1
                        if (braggcnt == 3):
                            sf=n
                        if (braggcnt >= tracklen/8):
                            frontfound = True
                            print("FRONT found !!!!!!")
                            frontslope_top = float(n[1]+n[5]-sf[1]-sf[5])/float(n[0]-sf[0])
                            frontslope_mid = float(n[1]+n[5]/2-sf[1]-sf[5]/2)/float(n[0]-sf[0])
                            frontslope_bottom = float(n[1]-sf[1])/float(n[0]-sf[0])
                        p = n
                    hitfound = False
                    t_jt = 0
                    t_jb = 0
                    t_pt = 0
                    t_pb = 0

                if(j[0] == ch+1):
                    print("Here  4444   !!!!!!!!!")
                    t_jt = j[1]+j[5]
                    t_jb = j[1]
                    t_pt = p[1]+p[5]
                    t_pb = p[1]
                    if ( (t_jb>=t_pb and t_jb<=t_pt) or (t_jt>=t_pb and t_jt<=t_pt) or (t_pt<=t_jt and t_pb>=t_jb)) :
                        if (horiz_noise_cnt == 0):
                            horiz_tb = t_pb
                            horiz_tt = t_pt
                        if (j[0]==n[0]):
                            break
                        hitfound = True
                        n = j
                        if (abs(t_jb - horiz_tb) <=1) or (abs(t_jt - horiz_tt) <=1):
                            horiz_noise_cnt+=1
                            if (horiz_noise_cnt>horiz_tolerance):
                                break
                        else:
                            horiz_noise_cnt = 0
                        if (t_jt > time_max):
                            time_max = t_jt
                        if (t_jb < time_min):
                            time_min = t_jt
            ch = i[0]
            p = i #previous hit confirmed in track in previous channel                                                                                                                                       
            n = i #current hit considered best fit for next hit in track in channel after p                                                                                                                    \
                    
            t_jt = 0
            t_jb = 0
            t_pt = 0
            t_pb = 0
            deadcnt = 0 #number of deadchannels we've skipped                                                                                                  
            slope = 0 #needed for deadchannel skipping                                                                                                                                                         \
                    
            ##print("self.firsthit = " +str(self.firsthit))                                                                                                                                                    \
                
            #sf = i #TP to calculate slope forward                                                                                                                                                             \
                
            #sb = i #TP to calculate slope backward                                                                                                                                                             
            hitfound = False
            temp_t = 0
            horiz_noise_cnt = 0
            horiz_tb = 0
            horiz_tt = 0
            if (frontfound == True):
                for q in np.arange(Q,-1,-1):
                    j = inputTP[q]
                    if(j[0]<=(ch-2)):
                        ch = n[0]
                        if (hitfound==False):
                            break
                        if (deadch[ch-1] == 0 and j[0]!=ch-1):
                            if(p[0]==i[0]):
                                slope = 0
                            elif(p[0]==sb[0]):
                                slope = float(p[1]+p[5]/2-i[1]-i[5]/2)/float(p[0]-i[0])
                                #               print("bkwrd slope if p0=sb0: "+str(slope))                                                                                                                     \
                                        
                            else:
                                slope = float(p[1]+p[5]/2-sb[1]-sb[5]/2)/float(p[0]-sb[0])
                                #              print("bkwrd slope in else: "+str(slope))                                                                                                                       \
                                    
                            deadcnt = 0
                            while (deadch[ch-1]==0 and (ch-1)>colstart):
                                ch-=1
                                print("bkwrd loop Skipping through dead channel:"+str(ch))
                                deadcnt+=1
                            #            print("bkwrd deadcnt =" + str(deadcnt))                                                                                                              
                            p[1]=p[1]-np.floor(float(slope)*float(deadcnt))
                        if (hitfound==True):
                            braggcnt+=1
                            if (braggcnt == tracklen/2+3):
                                sb = n
                            if (braggcnt >= tracklen):
                                backslope_top = float(n[1]+n[5]-sb[1]-sb[5])/float(n[0]-sb[0])
                                backslope_mid = float(n[1]+n[5]/2-sb[1]-sb[5]/2)/float(n[0]-sb[0])
                                backslope_bottom = float(n[1]-sb[1])/float(n[0]-sb[0])
                                print("slopes back: "+str(backslope_top)+" , "+str(backslope_mid)+" , "+str(backslope_bottom))
                                frontangle_top = math.degrees(math.atan(slopecm_scale*float(frontslope_top)))
                                backangle_top = math.degrees(math.atan(slopecm_scale*float(backslope_top)))
                                frontangle_mid = math.degrees(math.atan(slopecm_scale*float(frontslope_mid)))
                                backangle_mid = math.degrees(math.atan(slopecm_scale*float(backslope_mid)))
                                frontangle_bottom = math.degrees(math.atan(slopecm_scale*float(frontslope_bottom)))
                                backangle_bottom = math.degrees(math.atan(slopecm_scale*float(backslope_bottom)))
                                if (abs(frontangle_mid-backangle_mid)>0 and abs(frontangle_top-backangle_top)>0 and abs(frontangle_bottom-backangle_bottom)>0):
                                    beforeangletrigtot += 1
                                    print("Angle > 0")
                                if (abs(frontangle_mid-backangle_mid)>30 and abs(frontangle_top-backangle_top)>30 and abs(frontangle_bottom-backangle_bottom)>30):
                                    trigtot += 1
                                    print("Angle > 30")
                                    print("Bragg peak TP found at " +str(i))
                                    peaklist.append(i)
                                    break
                                else:
                                    break
                            p = n
                        hitfound = False
                        t_jt = 0
                        t_jb = 0
                        t_pt = 0
                        t_pb = 0
                    if(j[0]==ch-1):
                        t_jt = j[1]+j[5]
                        t_jb = j[1]
                        t_pt = p[1]+p[5]
                        t_pb = p[1]
                        if ( (t_jb>=t_pb and t_jb<=t_pt) or (t_jt>=t_pb and t_jt<=t_pt) or (t_pt<=t_jt and t_pb>=t_jb)) :
                            if (horiz_noise_cnt == 0):
                                horiz_tb = t_pb
                                horiz_tt = t_pt
                            if (j[0]==n[0]):
                                break
                            hitfound=True
                            n = j
                            if (abs(t_jb - horiz_tb) <=1) or (abs(t_jt - horiz_tt) <=1):
                                horiz_noise_cnt+=1
                                if (horiz_noise_cnt>horiz_tolerance):
                                    break
                            else:
                                horiz_noise_cnt = 0
                            if (t_jt > time_max):
                                time_max = t_jt
                            if (t_jb < time_min):
                                time_min = t_jt


