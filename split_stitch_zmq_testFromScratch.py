#Read TPs from manually generated TP file and stitch TPs to form a drift region {2.3ms} worth 4600 time ticks, reading 3 frames at a time from the uBooNE data runs. Channel mapping is also implemented here.   
#D.Kalra (dkalra@nevis.columbi.edu) (dk3172@columbia.edu) (October 25, 2021)

#import matplotlib.pyplot as plt
#import matplotlib
import numpy as np
#add data transfer systems 
import zmq
import json
import time
import pandas as pd
import cProfile
port = 6665

#context = zmq.Context()
#socket = context.socket(zmq.PUB)
#socket.bind("tcp://*:%s" % port)

#Command to convert binary to hex-dump file: hexdump -v -e '8/4 "%08X ""\n"' BINARYFILE 

#f=open("testnominal_folded28554_head_threeframes", "r")
#f=open("testnominal_folded28554_25frames", "r")

pr = cProfile.Profile()
#pr.enable()

#f=open("zmq/testnominal_folded28554_head_testmore25frames", "r")

cratenum=2
min1p=0
tmin=0
tmax=3200
tdrift=4600
tdiff=tmax-tmin
tDiff=tdrift-tdiff
stitchedTP= []
thisFrameList=[]
td=0
tmin2=0
tdiff2=tmax-tmin
tDiff2=tdrift-tdiff2
tdiffa=tmax-tmin
tDiffa=tdrift-tdiffa

FirstTime=True
changeMin=False
channellist2=[]
stitchedTP2=[]
tminp=0
frmcntby3 = 3
#frmcntby2 = 2


frmcntby0 = 0
tmin_eo1 = 0
tdiff_eo1 = tmax-tmin_eo1
tDiff_eo1=tdrift-tdiff_eo1

tmin_eo2 = 0
tdiff_eo2 = tmax-tmin_eo2
tDiff_eo2=tdrift-tdiff_eo2

tmin_eo3 = 0
tdiff_eo3 = tmax-tmin_eo3
tDiff_eo3=tdrift-tdiff_eo3
tdiff_sf1 = tmax-tmin_eo1
tDiff_sf1=tdrift-tdiff_eo1
minp2 = 0
framelistp = []
frame11=0
framelistfull1=[]
tdiffP =tdiff
hitlist=[]                                                                                                                                
colplstart = 2976
step = 96

stitchedTP_part1 = []
stitchedTP_part2 = []

tdiffP2=tdiff
tdiffP3=tdiff

def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary
            
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
#pr.enable()
print("start time :", now)

#tplistCol.append([min1p, frame, femm, channel,int(larchnlNumCol), timetick, int(intgrl), int(tot), int(amp)])
#NEW to use: #tplistCol.append([min1p, frame, femm, int(larchnlNumCol), timetick, int(intgrl), int(tot), int(amp)])

while True:
    dat = socket.recv_json()
    readTP = json.loads(dat)
    print("receiving...")
    now1 = time.time()                                                                                                                               
    print("start time :", now1)
    #print("Len: "+str(len(readTP)))
    #print("ReadTP: "+str(readTP[0]))
    #time.sleep(100)
    min1p=readTP[0][0]
    print("minp: "+str(min1p))
    # min1p=min1p+frmcntby0    
    #if(readTP[0][1]>0 and readTP[0][1] == readTP[0][0]+frmcntby3):
    for tps in readTP:
        #print("TPis: "+str(tps) + " , and tp0: " +str(tps[0]))
        if(tps[1]==min1p):
            if(FirstTime==True): 
                td=min1p
                tmin2=0
                tminp=tmin
                tmin=tmin2
                tmax=3200
                tdrift=4600
                tdiff=tmax-tmin
                tdiff_sf1 =tdiff
                tDiff=tdrift-tdiff
                tDiff_sf1 =tDiff
                if(tps[4]>=tmin and  tps[4]<=tmax):
                    #stitchedTP=[]
                    #stitchedTP.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                    if (td==min1p):
                        stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])  
                    elif(td==min1p+1):
                        stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                    #print("Stitched TP: "+str(stitchedTP))
                    #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                    tmin_eo1=tDiff
                    tmax=3200
                    tdiff_eo1=tmax-tmin_eo1
                    tDiff_eo1=tdrift-tdiff_eo1

            else: #if not first time
                td=min1p
                tmin=tmin_eo3
                tmax=3200
                tdiff=tdiff_eo3 #tmax-tmin #tdiff2
                tdiff_sf1 = tdiff
                tDiff=tDiff_eo3 #tdrift-tdiff #tDiff2
                tDiff_sf1 = tDiff
                if(len(stitchedTP2)!=0):
                    if(td==min1p):
                        #stitchedTP=[]
                        #stitchedTP.extend(stitchedTP2)
                        if (td==min1p):
                            stitchedTP_part1.extend(stitchedTP2)
                        elif(td==min1p+1):
                            stitchedTP_part2.extend(stitchedTP2)
                        #print("Stitched TP: "+str(stitchedTP))
                        #print("len of stTP HERE: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                        stitchedTP2=[]
                        #print("Stitched TP Here: "+str(stitchedTP))
                if(tDiff==3200):
                    if(tps[4]>=tminp and  tps[4]<=tDiff):
                        #stitchedTP=[]
                        #stitchedTP.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                        if (td==min1p):
                            stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                        elif(td==min1p+1):
                            stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                        #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5], readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                        #print("Stitched TP: "+str(stitchedTP))
                        #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                        tmin_eo1=tminp
                        tmax=3200
                        tdiff_eo1=tmax-tmin_eo1
                        tDiff_eo1=tdrift-tdiff_eo1

                elif(tDiff<3200):
                    if(tps[4]>=tminp and  tps[4]<=tDiff):
                        #stitchedTP=[]
                        #stitchedTP.append([tps[1], tps[2], tps[3], tps[4]+tdiff, tps[5], tps[6], tps[7], td, cratenum])
                        if (td==min1p):
                            stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4]+tdiff, tps[5], tps[6], tps[7], td, cratenum])
                        elif(td==min1p+1):
                            stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4]+tdiff, tps[5], tps[6], tps[7], td, cratenum])
                        #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5]+tdiff, readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                        #print("Stitched TP: "+str(stitchedTP))
                        #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                        tmin_eo1=tDiff
                        tmax=3200
                        tdiff_eo1=tmax-tmin_eo1
                        tdiff_sf1 = tdiff_eo1
                        tDiff_eo1=tdrift-tdiff_eo1
                        tDiff_sf1 = tDiff_eo1

                    else:
                        td=min1p+1
                        #stitchedTP=[]
                        #stitchedTP.append([tps[1], tps[2], tps[3], tps[4]-tDiff, tps[5], tps[6], tps[7], td, cratenum])
                        if (td==min1p):
                            stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4]-tDiff, tps[5], tps[6], tps[7], td, cratenum])
                        elif(td==min1p+1):
                            stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4]-tDiff, tps[5], tps[6], tps[7], td, cratenum])
                        #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5]-tDiff, readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])

                        #print("Stitched TP: "+str(stitchedTP))
                        #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                        td=min1p
                        tmin_eo1=tDiff
                        tmax=3200
                        tdiff_eo1=tmax-tmin_eo1
                        tdiff_sf1 = tdiff_eo1
                        tDiff_eo1=tdrift-tdiff_eo1
                        tDiff_sf1 = tDiff_eo1

                elif(tDiff>3200):
                    tmin2=tminp
                    tmin=tmin2
                    tmax=3200
                    tdiffP = tdiff
                    tdiff=tdiff+(tmax-tmin)
                    tdiff_sf1 = tdiff
                    tDiff=tdrift-tdiff
                    tDiff_sf1 = tDiff
                    if(tps[4]>=tmin and  tps[4]<=tmax):
                        #stitchedTP=[]
                        #stitchedTP.append([tps[1], tps[2], tps[3], tps[4]+tdiffP, tps[5], tps[6], tps[7], td, cratenum])
                        if (td==min1p):
                            stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4]+tdiffP, tps[5], tps[6], tps[7], td, cratenum])
                        elif(td==min1p+1):
                            stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4]+tdiffP, tps[5], tps[6], tps[7], td, cratenum])
                        #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5]+tdiffP, readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])

                        #print("Stitched TP: "+str(stitchedTP))
                        #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                        td=min1p
                        tmin_eo1=tDiff
                        tmax=3200
                        tdiff_eo1=tmax-tmin_eo1
                        tDiff_eo1=tdrift-tdiff_eo1


        if(tps[1]==min1p+1):
            FirstTime=False
            #print("mid")
            tmin2=tminp
            tmin=tmin2
            tmax=3200
            tdiff= tdiff_sf1 #tdiff_eo1
            tdiffP2 = tdiff
            tDiff= tDiff_sf1 #tDiff_eo1
            #print("tDiff: "+str(tDiff))
            if(tDiff==3200):
                #print("mid1")
                if(tps[4]>=0 and  tps[4]<=tDiff):
                    #stitchedTP=[]
                    #print("mid2")
                    #stitchedTP.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                    if (td==min1p):
                        stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                    elif(td==min1p+1):
                        stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                    #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5], readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                    #print("Stitched TP: "+str(stitchedTP))

                    #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                    tmin_eo2=tminp
                    tmax=3200
                    tdiff_eo2=tmax-tmin_eo2
                    tDiff_eo2=tdrift-tdiff_eo2
            elif(tDiff<3200):
                #print("mid3")
                if(tps[4]>=tminp and  tps[4]<=tDiff):
                    #print("mid4")
                    #stitchedTP=[]

                    #stitchedTP.append([tps[1], tps[2], tps[3], tps[4]+tdiff, tps[5], tps[6], tps[7], td, cratenum])
                    if (td==min1p):
                        stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4]+tdiff, tps[5], tps[6], tps[7], td, cratenum])
                    elif(td==min1p+1):
                        stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4]+tdiff, tps[5], tps[6], tps[7], td, cratenum])

                    #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5]+tdiff, readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                    #print("Stitched TP: "+str(stitchedTP))
                    #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                    tmin_eo2=tmin_eo1#tDiff
                    tmax=3200
                    tdiff_eo2=tmax-tmin_eo2
                    tDiff_eo2=tdrift-tdiff_eo2
                else:
                    #print("mid5")
                    td=min1p+1
                    #stitchedTP=[]

                    #stitchedTP.append([tps[1], tps[2], tps[3], tps[4]-tDiff, tps[5], tps[6], tps[7], td, cratenum])
                    if (td==min1p):
                        stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4]-tDiff, tps[5], tps[6], tps[7], td, cratenum])
                    elif(td==min1p+1):
                        stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4]-tDiff, tps[5], tps[6], tps[7], td, cratenum])

                    #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5]-tDiff, readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                    #print("Stitched TP: "+str(stitchedTP))
                    #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                    td=min1p
                    tmin_eo2=tmin_eo1 #tDiff
                    tmax=3200
                    tdiff_eo2=tmax-tmin_eo2
                    tDiff_eo2=tdrift-tdiff_eo2
            elif(tDiff>3200):
                #print("mid6")
                td=min1p+1
                tmin2=tminp
                tmin=tmin2
                tmax=3200
                tdiff=tdiff+(tmax-tmin)
                tDiff=tdrift-tdiff
                if(tps[4]>=tmin and  tps[4]<=tmax):
                    #stitchedTP=[]
                    #print("mid7")

                    #stitchedTP.append([tps[1], tps[2], tps[3], tps[4]+tdiffP2, tps[5], tps[6], tps[7], td, cratenum])
                    if (td==min1p):
                        stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4]+tdiffP2, tps[5], tps[6], tps[7], td, cratenum])
                    elif(td==min1p+1):
                        stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4]+tdiffP2, tps[5], tps[6], tps[7], td, cratenum])
                    #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5]+tdiffP2, readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                    #print("Stitched TP: "+str(stitchedTP))
                    #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                    td=min1p
                    tmin_eo2=tminp #tmin_eo1 #tDiff
                    tmax=3200
                    tdiff_eo2=tdiff #tmax-tmin_eo2
                    tDiff_eo2=tDiff

        if(tps[1]==min1p+2):    
            tmin=tmin_eo2
            tmax=3200
            tdiff=tdiff_eo2
            tdiffP3=tdiff
            tDiff=tDiff_eo2
            if(tDiff==3200):
                if(tps[4]>=tminp and  tps[4]<=tDiff):
                    #stitchedTP=[]

                    #stitchedTP.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                    if (td==min1p):
                        stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                    elif(td==min1p+1):
                        stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4], tps[5], tps[6], tps[7], td, cratenum])
                    #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5], readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                    #print("Stitched TP: "+str(stitchedTP))
                    #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                    tmin_eo3=tminp                                                           
                    tmax=3200
                    tdiff_eo3=tmax-tmin_eo3
                    tDiff_eo3=tdrift-tdiff_eo3

            elif(tDiff<3200):
                if(tps[4]>=tminp and  tps[4]<=tDiff):
                    td=min1p+1
                    #stitchedTP=[]

                    #stitchedTP.append([tps[1], tps[2], tps[3], tps[4]+tdiff, tps[5], tps[6], tps[7], td, cratenum])
                    if (td==min1p):
                        stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4]+tdiff, tps[5], tps[6], tps[7], td, cratenum])
                    elif(td==min1p+1):
                        stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4]+tdiff, tps[5], tps[6], tps[7], td, cratenum])
                    #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5]+tdiff, readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                    #print("Stitched TP: "+str(stitchedTP))
                    #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
                    td=min1p
                    tmin_eo3=tDiff
                    tmax=3200
                    tdiff_eo3=tmax-tmin_eo3
                    tDiff_eo3=tdrift-tdiff_eo3
                else:
                    #print("check")
                    td=min1p+3
                    stitchedTP2.append([tps[1], tps[2], tps[3], tps[4]-tDiff, tps[5], tps[6], tps[7], td, cratenum])
                    #stitchedTP2.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5]-tDiff, readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                    #print("StTP2Len: " +str(len(stitchedTP2)))
                    td=min1p
                    tmin_eo3=tDiff
                    tmax=3200
                    tdiff_eo3=tmax-tmin_eo3
                    tDiff_eo3=tdrift-tdiff_eo3
            elif(tDiff>3200):
                tmin2=tminp
                tmin=tmin2
                tmax=3200
                tdiff=tdiff+(tmax-tmin)
                tDiff=tdrift-tdiff
                if(tps[4]>=tmin and  tps[4]<=tmax):
                    #stitchedTP=[]
                    #stitchedTP.append([tps[1], tps[2], tps[3], tps[4]+tdiffP3, tps[5], tps[6], tps[7], td, cratenum])
                    if (td==min1p):
                        stitchedTP_part1.append([tps[1], tps[2], tps[3], tps[4]+tdiffP3, tps[5], tps[6], tps[7], td, cratenum])
                    elif(td==min1p+1):
                        stitchedTP_part2.append([tps[1], tps[2], tps[3], tps[4]+tdiffP3, tps[5], tps[6], tps[7], td, cratenum])
                    #stitchedTP.append([readTP[0][1], readTP[0][2], readTP[0][4], readTP[0][5]+tdiffP3, readTP[0][6], readTP[0][7], readTP[0][8], td, cratenum])
                    #print("Stitched TP: "+str(stitchedTP))
                    td=min1p
                    tmin_eo3=tDiff
                    tmax=3200
                    tdiff_eo3=tmax-tmin_eo3
                    tDiff_eo3=tdrift-tdiff_eo3



    #print("len of stTP: "+str(len(stitchedTP)) + " , " +str(len(stitchedTP2)))
    #STP_df = pd.DataFrame(stitchedTP)
    #print("tp: "+str(tplistCol))                                                                                    
    #print("check STP df: ", STP_df)
    #STP_send_data = json.dumps(stitchedTP)                                                                           
    #osocket.send_json(STP_send_data) 
    #STP_send_data = json.dumps(stitchedTP).encode('utf8')
    #socket.send(STP_send_data)


    #for dr in stitchedTP:
     #   if(dr[7]==min1p):
      #      stitchedTP_part1.append([dr[0],dr[1],dr[2],dr[3],dr[4],dr[5],dr[6],dr[7],dr[8]])
       # elif(dr[7]==min1p+1):
        #    stitchedTP_part2.append([dr[0],dr[1],dr[2],dr[3],dr[4],dr[5],dr[6],dr[7],dr[8]])
    STP_df1 = pd.DataFrame(stitchedTP_part1)
    print("len of stTP 1:  " +str(len(stitchedTP_part1)) + "part2 len: "+ str(len(stitchedTP_part2)))
    #print("check STP df1: ", STP_df1)
    STP_send_data1 = json.dumps(stitchedTP_part1)
    osocket.send_json(STP_send_data1)
    end = time.time()
    print("End time1 :", end)
    STP_df2 = pd.DataFrame(stitchedTP_part2)
    #print("check STP df2: ", STP_df2)
    STP_send_data2 = json.dumps(stitchedTP_part2)
    osocket.send_json(STP_send_data2)
    end1 = time.time()
    print("End time :", end1)
    stitchedTP.clear()
    stitchedTP_part1.clear()
    stitchedTP_part2.clear()
    end2 = time.time()
    print("End time :", end2)


'''



                    min1p=min1p+frmcntby0
                    if(len(framelist)>0 and framelist[-1]==min(framelist)+frmcntby3):
                        #print("Min1p is: "+str(min1p))
                        #print("TPList is done!! and length is: "+str(len(tplistint)))
                        stitch_time = time.time()
                        print("TP Stitching time: ", stitch_time)
                        for tps in tplistint: #collection:       #tps[0] = tplistint[0] = frame  
                            #print("TP is:"+str(tps) + "minp: "+str(min1p))
                            #print("minp: "+str(min1p))
                            if(tps[0]==min1p):
                                #print("if condition: frame: "+str(tps[0]))
                                #print("len of stitchedTP2: "+str(len(stitchedTP2)))
                                if(FirstTime==True):
                                    td=min1p
                                    tmin2=0
                                    tminp=tmin
                                    tmin=tmin2
                                    tmax=3200
                                    tdrift=4600
                                    tdiff=tmax-tmin
                                    tdiff_sf1 =tdiff
                                    tDiff=tdrift-tdiff
                                    tDiff_sf1 =tDiff
                                    #print("FirstTimeCheck1(fr,tmin,tmax,td,tD): "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + " ," + str(tDiff))
                                    if(tps[4]>=tmin and tps[4]<=tmax):
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4],tps[5],tps[6],tps[7],td,cratenum])
                                        tmin_eo1=tDiff
                                        tmax=3200
                                        tdiff_eo1=tmax-tmin_eo1
                                        tDiff_eo1=tdrift-tdiff_eo1
                                        #print("EO1 firsttime:"+str(tmin_eo1)+", "+str(tdiff_eo1)+", "+str(tDiff_eo1))

                                else:  #if its not first time
                                    #print("hello!!!!!!!!")
                                    td=min1p
                                    tmin=tmin_eo3
                                    tmax=3200
                                    tdiff=tdiff_eo3 #tmax-tmin #tdiff2
                                    tdiff_sf1 = tdiff
                                    tDiff=tDiff_eo3 #tdrift-tdiff #tDiff2
                                    tDiff_sf1 = tDiff
                                    #print("Check1B(fr,tm,tM,td,tD): "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + " ," + str(tDiff))
                                    #print("_sf1: "+str( tdiff_sf1 )+ ", "+str( tDiff_sf1 ))
                                    if(len(stitchedTP2)!=0):
                                        if(td==min1p):
                                            stitchedTP.extend(stitchedTP2)
                                            stitchedTP2=[]  #clear list after transferring everything to another list 
                                            #print("len of stitchedTP after filling info from TP2: "+str(len(stitchedTP)))
                                    if(tDiff==3200):
                                        if(tps[4]>=tminp and tps[4]<=tDiff):
                                            #stitchedTP=[]
                                            stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4],tps[5],tps[6],tps[7],td, cratenum])
                                            #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                            tmin_eo1=tminp
                                            tmax=3200
                                            tdiff_eo1=tmax-tmin_eo1
                                            tDiff_eo1=tdrift-tdiff_eo1
                                            #print("EO1(==3200):"+str(tmin_eo1)+", "+str(tdiff_eo1)+", "+str(tDiff_eo1))
                                    elif(tDiff<3200):
                                        #print("Check1C(fr,tm,tM,td,tD): "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + " ," + str(tDiff))
                                        if(tps[4]>=tminp and tps[4]<=tDiff):
                                            #stitchedTP=[]
                                            stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiff,tps[5],tps[6],tps[7],td, cratenum])
                                            #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                            tmin_eo1=tDiff
                                            tmax=3200
                                            tdiff_eo1=tmax-tmin_eo1
                                            tdiff_sf1 = tdiff_eo1
                                            tDiff_eo1=tdrift-tdiff_eo1
                                            tDiff_sf1 = tDiff_eo1
                                            #print("EO1 tmin, tmax, tdiff, tDiff: "+str(tmin) +","+str(tdiff_eo1)+","+str(tDiff_eo1))
                                            #print("EO1 _sf1: "+str( tdiff_sf1 )+ ", "+str( tDiff_sf1 ))

                                        else:
                                            td=min1p+1
                                            #stitchedTP=[]
                                            stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]-tDiff,tps[5],tps[6],tps[7],td, cratenum])
                                            #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                            td=min1p
                                            tmin_eo1=tDiff
                                            tmax=3200
                                            tdiff_eo1=tmax-tmin_eo1
                                            tdiff_sf1 = tdiff_eo1
                                            tDiff_eo1=tdrift-tdiff_eo1
                                            tDiff_sf1 = tDiff_eo1
                                            #print("EO1 tmin, tmax, tdiff, tDiff: "+str(tmin) +","+str(tdiff_eo1)+","+str(tDiff_eo1))
                                            #print("EO1 _sf1: "+str( tdiff_sf1 )+ ", "+str( tDiff_sf1 ))
                                    elif(tDiff>3200):
                                        tmin2=tminp
                                        tmin=tmin2
                                        tmax=3200
                                        tdiffP = tdiff
                                        tdiff=tdiff+(tmax-tmin)
                                        tdiff_sf1 = tdiff
                                        tDiff=tdrift-tdiff
                                        tDiff_sf1 = tDiff
                                        #print("Check1D on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff) + "tdiffP is:"+str(tdiffP))
                                        #print ("1D _sf1: "+str(tdiff_sf1) + ", "+ str(tDiff_sf1))
                                        if(tps[4]>=tmin and tps[4]<=tmax):
                                            #stitchedTP=[]
                                            stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiffP,tps[5],tps[6],tps[7],td, cratenum])
                                            #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                            #tplistint=[]
                                            td=min1p
                                            tmin_eo1=tDiff
                                            tmax=3200
                                            tdiff_eo1=tmax-tmin_eo1
                                            tDiff_eo1=tdrift-tdiff_eo1
                                            #print("EO1 (>3200) : "+ str(tmin) +", "+str(tdiff_eo1) +", "+str(tDiff_eo1))


                            if(tps[0]==min1p+1):
                                #print("if condition: frame: "+str(tps[0]))
                                FirstTime=False
                                tmin2=tminp
                                tmin=tmin2
                                tmax=3200
                                tdiff= tdiff_sf1 #tdiff_eo1
                                tdiffP2 = tdiff
                                tDiff= tDiff_sf1 #tDiff_eo1
                                #print("Check2A on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff) +"tdiffP2: "+str(tdiff))
                                #print("tmin2 is: "+str(tmin2))

                                if(tDiff==3200):
                                    #print("tDiff found to be 3200!!!! Tricky. Clear everything at this point and start again")
                                    #tplistint = []
                                    #stitchedTP=[]
                                    #stitchedTP2=[]
                                    #FirstTime = True
                                    #print("Check Frame list: "+str(framelist))
                                    if(tps[4]>=0 and tps[4]<=tDiff):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4],tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        tmin_eo2=tminp
                                        tmax=3200
                                        tdiff_eo2=tmax-tmin_eo2
                                        tDiff_eo2=tdrift-tdiff_eo2


                                elif(tDiff<3200):
                                    #print("Check2B on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                    if(tps[4]>=tminp and tps[4]<=tDiff):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiff,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[] 
                                        tmin_eo2=tmin_eo1#tDiff
                                        tmax=3200
                                        tdiff_eo2=tmax-tmin_eo2
                                        tDiff_eo2=tdrift-tdiff_eo2
                                        #print("EO2 (if): "+str(tmin) +", "+str(tdiff_eo2)+" ,"+str(tDiff_eo2))
                                    else:
                                        #print("Check2C on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                        td=min1p+1
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]-tDiff,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[] 
                                        td=min1p
                                        tmin_eo2=tmin_eo1 #tDiff
                                        tmax=3200
                                        tdiff_eo2=tmax-tmin_eo2
                                        tDiff_eo2=tdrift-tdiff_eo2
                                        #print("EO2 (else): "+str(tmin) +", "+str(tdiff_eo2)+" ,"+str(tDiff_eo2))
                                elif(tDiff>3200):
                                    td=min1p+1
                                    tmin2=tminp
                                    tmin=tmin2
                                    tmax=3200
                                    tdiff=tdiff+(tmax-tmin)
                                    tDiff=tdrift-tdiff
                                    #print("Check2D on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                    if(tps[4]>=tmin and tps[4]<=tmax):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiffP2,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[]                                                                                                    
                                        td=min1p
                                        tmin_eo2=tminp #tmin_eo1 #tDiff
                                        tmax=3200
                                        tdiff_eo2=tdiff #tmax-tmin_eo2
                                        tDiff_eo2=tDiff #tdrift-tdiff_eo2
                                        #print("EO2 (2D else>3200): "+str(tmin) +", "+str(tdiff_eo2)+" ,"+str(tDiff_eo2))

                            if(tps[0]==min1p+2):
                                tmin=tmin_eo2
                                tmax=3200
                                tdiff=tdiff_eo2
                                tdiffP3=tdiff
                                tDiff=tDiff_eo2
                                #print("Check3A on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff) +"tdiffP3: "+str(tdiffP3))
                                if(tDiff==3200):
                                    if(tps[4]>=tminp and tps[4]<=tDiff):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4],tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))

                                        tmin_eo3=tminp                                                           
                                        tmax=3200
                                        tdiff_eo3=tmax-tmin_eo3
                                        tDiff_eo3=tdrift-tdiff_eo3
                                        #print("EO3 :" +str(tmin) +", "+str(tdiff_eo3)+" ,"+str(tDiff_eo3))

                                elif(tDiff<3200):
                                    #print("Check3B on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                    if(tps[4]>=tminp and tps[4]<=tDiff):
                                        td=min1p+1
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiff,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[] 
                                        td=min1p
                                        tmin_eo3=tDiff
                                        tmax=3200
                                        tdiff_eo3=tmax-tmin_eo3
                                        tDiff_eo3=tdrift-tdiff_eo3
                                        #print("EO3 (<3200 if):" +str(tmin) +", "+str(tdiff_eo3)+" ,"+str(tDiff_eo3))
                                    else:
                                        #print("Check3C on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + ", "+str(tdiff) + ", " + str(tDiff))
                                        td=min1p+3
                                        #stitchedTP=[]
                                        stitchedTP2.append([tps[0],tps[1],tps[2],tps[3],tps[4]-tDiff,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP2 len for frame:" + str(tps[0]) + " is: " +str(len(stitchedTP2)))
                                        #tplistint=[] 
                                        td=min1p
                                        tmin_eo3=tDiff
                                        tmax=3200
                                        tdiff_eo3=tmax-tmin_eo3
                                        tDiff_eo3=tdrift-tdiff_eo3
                                        #print("EO3 (<3200 else):" +str(tmin) +", "+str(tdiff_eo3)+" ,"+str(tDiff_eo3))

                                elif(tDiff>3200):
                                    tmin2=tminp
                                    tmin=tmin2
                                    tmax=3200
                                    tdiff=tdiff+(tmax-tmin)
                                    tDiff=tdrift-tdiff
                                   #print("Check3D on tmin, tmax, tdiff, tdrift for frame: "+str(tps[0])+ " is: "+ str(tmin) + " , "+str(tmax) + " , "+str(tdiff) + ", " + str(tDiff))
                                    if(tps[4]>=tmin and tps[4]<=tmax):
                                        #stitchedTP=[]
                                        stitchedTP.append([tps[0],tps[1],tps[2],tps[3],tps[4]+tdiffP3,tps[5],tps[6],tps[7],td, cratenum])
                                        #print("StitchedTP for frame:" + str(tps[0]) + " is: " +str(stitchedTP))
                                        #tplistint=[]                                                                                                                
                                        td=min1p
                                        tmin_eo3=tDiff
                                        tmax=3200
                                        tdiff_eo3=tmax-tmin_eo3
                                        tDiff_eo3=tdrift-tdiff_eo3
                                        #print("EO3 (>3200):" +str(tmin) +", "+str(tdiff_eo3)+" ,"+str(tDiff_eo3))


####################Cleartplistint and stitchedTP and start over again
                        tplistint.clear() #=[]
                        tplistcollection.clear()
                        #print("LENGTH of STP: "+str(len(stitchedTP)))
                        #print("TPlist cleared")
                        stitchedTP.clear() #=[]
                        stitchedTP_part1.clear()
                        stitchedTP_part2.clear()
                        #print("stitchedTP, P1, P2 cleared")
                        #print("Double check: tp and stitchTP,P1,P2 list: "+str(len(tplistcollection)) + " , "+ str(len(stitchedTP)) + " , "+ str(len(stitchedTP_part1)) + " , "+ str(len(stitchedTP_part2)) )
                        #print("Check StitchedTP form: "+str(stitchedTP) )
                        frmcntby3=frmcntby3+3


                        #min1p = min1p+3
                        frmcntby0 = frmcntby0 + 3
                        #print("FrameCounter: "+str(frmcntby3) )
                        hitlist_firstslice.clear()  # = []
                        hitlist_secondslice.clear() # = []
                        hitlist_thirdslice.clear()  # = []
                        hitlist_fourslice.clear()   # = []
                        hitlist_fifthslice.clear()  # = []
                        #framelist=[]
                        #print("Framlist cleared: "+str(framelist))


'''
