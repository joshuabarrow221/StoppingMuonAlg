#Code to check on the frame numbers using TP stream data files.                                                               
#D.Kalra (dkalra@nevis.columbi.edu) (dk3172@columbia.edu) (June 22, 2021)                                                      
#Command to convert binary to hex-dump file: hexdump -v -e '8/4 "%08X ""\n"' BINARYFILE 

f = open("TP_fakedata_incbuffer_June30","r") #input is hex-dump file
scale = 16 ## equals to hexadecimal                                                                                            
num_of_bits = 16
tot = 0
intgrl = 0
intgrlN = 0
nsamps = 0
hdrcnt = 0
amp = 0
N = 11
frame=0
mask=0
wordMasked=0
headerlist=[]
frame1=0
frame2=0
femheader=[]
chnlheader=[]

for l in f:
        #print(l)                                                                                      
        words = l.split()
        NumOfWords = len(words)
        for w in range(0,NumOfWords):
                wf = l.split()[w]
                #print(wf)                                                                                                     
                wrh = l.split()[w][4:]
                wlh = l.split()[w][0:4]
                wrb = bin(int(wrh, scale))[2:].zfill(num_of_bits)                                                            

                wlb = bin(int(wlh, scale))[2:].zfill(num_of_bits)
                if (wf[0]=="F" or wrh[0]=="1" or wlh[0]=="1"):
                        hdrcnt += 1
                        if (hdrcnt == 5):
                                #print(wlh)
                                femheader1=wrb[4:]
                                femheader2=wlb[4:]
                                femh=wrh[1:]+wlh[1:]
                                #print("FEM header is :" + str(femh))
                                #print("FEM header is(rtol) :" + str(femheader1))
                                #print("FEM header is(ltor) :" + str(femheader2))
                                frame1 = int(wrh[1:], 16) + int(wlh[1:], 16)
                                #print("FRAMENUM FEMHeader = " + str(frame1))
                        if (hdrcnt == 12):
                                #print("lh"+str(wlh))
                                if (wlh[0] == "1"):
                                        #print("chnl lh: "+str(wlh))
                                        chnlheader=[wlh[1:],wrh[1:]]
                                        #chnlheader_b1=wlb[4:]
                                        #chnlheader_b2=wrb[4:] ##[4:]
                                        #chnlheader_b=wlb[4:]+wrb[4:]
                                        #print("Chnl header: R:" + str(chnlheader_b2))
                                        #print("Chnl header: L:" + str(chnlheader_b1))
                                        #print(chnlheader[1])
                                        frame2=int(wlb[-12:-6],2)
                                        #print("FRAMENUM CHNLHeader = " + str(frame2))
                                        chnlheader_b=wlb[-12:-6] #[10:]
                                        #print(chnlheader_b)
                                        #print(wrb)
                                        #print(femheader)
                                        #print(frame1)
                                        #print(frame2)
                                        if(frame1 == frame2):
                                                print("FRAMENUM FEMHeader = " + str(frame1)) 
                                        elif(frame1 != frame2):
                                                print("Mismatch in frame numbers! Lets calculate masked frame number")
                                                #print("Frame1: " + str(frame1))
                                                #print("Frame2: " + str(frame2))
                                                #print("Left 12 bits:" + str(femheader1))
                                                #print("Mid 6 bits: "+ str(femheader2[0:6]))
                                                #print("Right 6 bits:" + str(chnlheader_b)) #"0:6])
                                                #print(chnlheader_b[0:6])
                                                #frameword_b=femheader1+femheader2[-12:-6]+chnlheader_b #[6:] #0:6]
                                                frameword_b=femheader1+femheader2[0:6]+chnlheader_b 
                                                #frameword_lh="F"+chnlheader[1]
      #                                          frameword_rh=femheader[1]
                                                #print("NewFrameWord binary: " + str(frameword_b))
                                                maskedframe=int((frameword_b),2)
                                                print("Masked Frame is: " + str(maskedframe))

                elif (wf == "E0000000"):
                        hdrcnt = 0
