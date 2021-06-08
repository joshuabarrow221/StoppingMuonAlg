#!/usr/bin/env python3
#Class for Michel e- trigger in uB, Harrison Siegel, Columbia University 2021

import numpy as np
import ROOT
import operator
import math

class prototypeMichelTrigger_maxADC_EXTboxes:
	"""Offline trigger for horizontal muon and michel e- tracks"""

	def __init__(self, deadch_f):
		self.TPlist = []
		self.firsthit = []
		self.first_index = []
		#self.TPlistt1 = []
		#self.TPlistt2 = []
		#self.numchnls = numchnl #3456 = number of wires collection plane uB, 8256 = number of total TPC channels
		self.deadch = []#0 if dead, 1 if not
		self.colstart = 4800#start of collection chnls
		self.colend = 8255#end of collection chnls
		self.colwid = self.colend - self.colstart
		d = open(deadch_f,"r")
		for l in d:
			if int(l.split()[1]) < 2:
				self.deadch.append(0)  
			else:
				self.deadch.append(1)
		self.boxwidch = 96 
		self.boxwidtime = 1150
		self.boxlistch = range(self.colstart,self.colend+self.boxwidch,self.boxwidch)#boxlists used to create subregions within collection plane
		print("self.boxlistch =" + str(self.boxlistch))
		self.boxlistchlen = len(self.boxlistch)
		#print("self.boxlistchlen = " + str(self.boxlistchlen))
		self.boxlisttime = range(3200,7800,self.boxwidtime)
		print("self.boxlisttime =" + str(self.boxlisttime))
		##print("Trigger object created")

	def getdeadch_list(self):
		return self.deadch

#	def readFile(self, f_str):#for text file input
#		f = open(f_str,"r")
#		chnl = 0
#		time = 0
#		intgrl = 0
#		view = -1
#		for l in f:
#			if (l.split()[0]=="channel"):
#				chnl = int(l.split()[1])
#			if (l.split()[0]=="view"):
#				view = int(l.split()[1])
#			if (l.split()[0]=="firstTick"):
#				time = int(l.split()[1])
#			if (l.split()[0]=="integralsum" and view == 2):
#				intgrl = int(l.split()[1])
#				self.loadTPs(chnl,time,intgrl,0,view)

	#def openFile(self,f_str):#DOESN'T SEEM TO WORK, open ROOT file and assign TP tree to object t
	#	f=ROOT.TFile.Open(f_str)
	#	t = f.Get("tpm/event_tree")
	#	return t

	def readFile(self, t, event):#for root file input, load TPs from tree t for given event number
		#max_ADC_uplim = 50000#not used currently
		#nEntries = t.GetEntries()
		#event_len = []
		#oldl = 0
		#newl = 0
		#for e in range(0,nEntries):
		self.TPlist = []
		self.firsthit = []
		self.first_index = []
		t.GetEntry(event)
		for q in range(0,t.channel.size()):
			if (t.view[q]==2):
				max_ADC = t.max_ADC[q]
				#if max_ADC > max_ADC_uplim:
				#	continue
				ch = t.channel[q]
				intgrl = t.integral_sum[q]
				intgrlN = t.integral_over_n[q]
				tot = t.tot[q]
				first_t = t.first_tick[q]
				if (first_t >= 3200 and first_t <= 7800):#2.3 ms drift, with what we think is the correct offset including the buffer
					self.loadTPs(ch, first_t, intgrl, intgrlN, max_ADC, tot)
			#	if (first_t >= 3200 and first_t <= 5500):#2.3 ms drift, with what we think is the correct offset including the buffer
			#		self.TPlistt1.append([chnl, first_tick, intgrl, intgrlN, maxADC, tot])
			#	if (first_t >= 5501 and first_t <= 7800):#2.3 ms drift, with what we think is the correct offset including the buffer
			#		self.TPlistt2.append([chnl, first_tick, intgrl, intgrlN, maxADC, tot])
		self.TPlist = sorted(self.TPlist, key = operator.itemgetter(0))#sort TPs by channel
		braggE = 27500
		#print("LENGTH CHECK = " + str(len(self.TPlist)))
		boxchcnt = 1
		#maxindex = 0
		maxTP = 0
		#filteredlist = [TP[2] for TP in self.TPlist]
		#filteredlist = [(idx,TPfilt) for idx, TPfilt in enumerate(self.TPlist)]#list to be used for subregion max ADC TP searches
		templist = []
		sublist = []
		#print("filteredlist[1:3] = " + str(filteredlist[1:3]))
		timeind = []
		for a in range(4600/self.boxwidtime+1):
			timeind.append(3200 + a*self.boxwidtime)
		#print("timeind = " + str(timeind))
		#print("self.boxlistch " + str(self.boxlistch))
		TPlistlen = len(self.TPlist)-1
		for n in np.arange(len(self.TPlist)):
			#print(self.TPlist[n])
			if self.TPlist[n][0]> self.boxlistch[boxchcnt] or n==TPlistlen:
				if len(templist)==0:
					while self.TPlist[n][0]> self.boxlistch[boxchcnt]: 
						boxchcnt +=1
				
				else:
					#print("subregion cleared")
					#print("boxchcnt = " + str(boxchcnt))
					#print("templist =" + str(templist))
				#	boxchcnt+=1
					for a in range(len(timeind)-1):
						sublist = []
						#print("timeind a = " + str(timeind[a]))
						for i in templist:
							if (i[1] >= timeind[a] and i[1] < timeind[a+1]):
								sublist.append(i)
						#print("sublist =" + str(sublist))
						if len(sublist)>0:		
							maxTP = max(sublist,key=operator.itemgetter(2))
							#print("maxindex" + str(maxindex))
							#print("maxTP " + str(maxTP))
						#	print("sublist[maxindex] " + str(sublist[maxindex]))
						#	print("sublist[maxindex][0] " + str(sublist[maxindex][0]))
						#	print("self.TPlist[sublist[maxindex][0]] = " + str(self.TPlist[sublist[maxindex][0]]))
							if (maxTP[2]>braggE):
								#self.firsthit.append(self.TPlist[sublist[maxindex][0]])
								#self.first_index.append(sublist[maxindex][0])
								self.firsthit.append(maxTP)
					templist = []
			#print("boxchcnt = " + str(boxchcnt))
			if self.TPlist[n][0]<=self.boxlistch[boxchcnt]:
				templist.append(self.TPlist[n])
			#print("index = " + str(index))
			#print("TP = " + str(TP))
			#print("TP[0] = " +str(TP[0]))
			#print("self.boxlistch[boxchcnt%self.boxlistchlen] = " +str(self.boxlistch[boxchcnt%self.boxlistchlen]))
		for h in self.firsthit:
			for z in np.arange(len(self.TPlist)):	
				if h == self.TPlist[z]:
					self.first_index.append(z)
		#print("self.firsthit = " + str(self.firsthit))
		#print("self.first_index = " + str(self.first_index))
		#print("self.TPlist length = " + str(len(self.TPlist)))
		#print("np.arange(len(self.TPlist)) = " + str(np.arange(len(self.TPlist))))
		testlist = []
		for u in self.first_index:
			testlist.append(self.TPlist[u])
		#print("testlist = " + str(testlist))
			#newl = t.channel.size()
			#event_len.append(newl-oldl)
			###print(newl-oldl)
			#oldl = newl
			#for ch in t.channel:
				###print "Channel = " +str(ch)
	#	oldl=0
		###print(event_len)
		#for i in range(0,len(event_len)):
		#l = event_len[i]
		#for k in range (0,event):
		#	oldl += event_len[k]
		#l = event_len[event]
		#oldl += l

	def getNumEvents(self, t):
		nEntries = t.GetEntries()
		return nEntries
		

	def loadTPs(self, chnl, first_tick, intgrl, intgrlN, maxADC, tot):
		self.TPlist.append([chnl, first_tick, intgrl, intgrlN, maxADC, tot])

	def printTPs(self):
		for i in self.TPlist:
			print(i)

	def getTPlist(self):
		return self.TPlist

	def clearTPs(self):
		self.TPlist = []

	def searchMichel(self):
		#looking for horizontal tracks initiated in first or last chnl and bragg peak
		#returns False if bragg peak not found, True if found

		#peakfound = False
		trigtot = 0
		peaklist = []
		#contiguous_tolerance = 3
		hitE = 0
		time_diff = 30 #time difference between hits when checking for contiguous mu hits in adjacent channels
		deadwidthscale = 8#scale of how wide time search gets after dead jumps
		slopecm_scale = 0.04/0.3#time ticks to cm = 1/25, channels to cm = 0.3
		
		#mipE = 17000 #approximately max integrated ADC of mip
		#braggE = 20000 #amount by which ADC needs to exceed mip when checking for elements of bragg peak
		#braggE = 15000
		braggE = 27500
		tracklen = 26
		kinkangle = 10#not being used currently, but should be minimum angle to successfully trigger
		#peak = 0 # highest ADC intgrl hit within Bragg peak 
		#extrabraggchnls = 5 #number of channels to search beyond peak before settling on chosen hit as peak

		#self.TPlist = sorted(self.TPlist, key = operator.itemgetter(0,1))#sort TPs by channel,then by start time tick
		#lims = [self.colstart,self.colend]
		#box1 = [x for x in list if x <= limit]

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

		#TPcnt = 0 #tally of TPs for determining TP density
		#chcnt = 0 #measuring width of TP window box in channels
		#time_max = 0#time min and max for determining height of TP window
		#time_min = 0

		horiz_noise_cnt = 0
		horiz_tolerance = 8
		horiz_tb = 0
		horiz_tt = 0

			
			
			
	#	if (len(self.TPlist)>0):
	#		M = (max(self.TPlist, key = lambda w: w[2]))[2]
	#	if (M>braggE):
	#		for q in np.arange(len( self.TPlist)):#look for hits to start search for muon track	
	#			if (self.TPlist[q][2]== M):#find max ADC
				#if ((self.TPlist[q][2]== max(self.TPlist, key = lambda w: w[2])[2] and (self.TPlist[q][5]==max(self.TPlist, key = lambda w: w[5])[5])):#find max ADC and max TOT
					#print ("MMMMM")
	#				self.firsthit.append(self.TPlist[q])	
	#				self.first_index.append(q)
		if (self.firsthit!=[]):
			#print(self.firsthit)
			for i,Q in zip(self.firsthit,self.first_index):
				#print("STARTING SEARCH")
				#print("start hit = " + str(i))
				ch = i[0] #current channel in loop
				deadcnt = 0 #number of deadchannels we've skipped
				#chnlwid = 0 #for contiguous tolercance > 2
				slope = 0 #needed for deadchannel skipping
				##print("self.firsthit = " +str(self.firsthit))
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
				#forward check for track first
				for q in np.arange(Q,len(self.TPlist),1):#loop through all TPs (which are ordered by channel), check if current TP j is iin the channel ch+1	
					if (frontfound == True):
						break
				#for j in self.TPlist:	
					j = self.TPlist[q]#current hit in list being considered
					#if (j[0]<(ch+1)):
					#	continue
					#else:
					#	TPcnt += 1
					if (j[0]>=(ch+2)):
						ch = n[0]
						if (hitfound==False):#check for missed hits
#							print("Missing hits in track ended search")
							break
						if (self.deadch[ch+1] == 0 and j[0]!=ch+1):
						#if (self.deadch[ch+1] == 0 and j[0]>(ch+2)):
							if(p[0]==i[0]):
								slope = 0
							elif(p[0]==sf[0]):
								slope = float(p[1]+p[5]/2-i[1]-i[5]/2)/float(p[0]-i[0])
							else:
								slope = float(p[1]+p[5]/2-sf[1]-sf[5]/2)/float(p[0]-sf[0])
							deadcnt = 0
							while (self.deadch[ch+1]==0 and (ch+1)<self.colend):
								ch+=1
#								print("Skipping through dead channel:"+str(ch))
								deadcnt+=1	
							#print("deadcnt =" + str(deadcnt))
							p[1]=p[1]+np.floor(float(slope)*float(deadcnt))
						if (hitfound==True):
							#print("Track hit found = " + str(n))
							braggcnt+=1
								#print("braggcnt = " + str(braggcnt))
							#elif(braggcnt>0 and p[2]<braggE):
							#	braggcnt = 0
							if (braggcnt == 3):
								sf = n
							#	print("sf found = " + str(sf))
							if (braggcnt >= tracklen/2):
								frontfound = True	
								#chcnt = j[0]-1
								frontslope_top = float(n[1]+n[5]-sf[1]-sf[5])/float(n[0]-sf[0])
								frontslope_mid = float(n[1]+n[5]/2-sf[1]-sf[5]/2)/float(n[0]-sf[0])
								frontslope_bottom = float(n[1]-sf[1])/float(n[0]-sf[0])
							p = n
							#ch=j[0]-1
						#else:#gap jumping
							#print("ch "+str(j[0]))
					#		if(p[0]==i[0]):
					#			slope = 0
					#		else:
					#			slope = float(p[1]-i[1])/float(p[0]-i[0])
					#		chnlwid = j[0]-ch-1
					#		#print("chnlwid " + str(chnlwid))
					#		temp_t = p[1] + np.floor(float(slope)*float(chnlwid))
					#		#print("temp_t " + str(temp_t))
					#		time_diff = 30*np.ceil(float(chnlwid)/float(deadwidthscale))
					#		if (abs(temp_t-j[1])<=time_diff):
					#			#print("great success")
					#			p[1]=temp_t
					#			ch=j[0]-1
						hitfound = False
						t_jt = 0
						t_jb = 0
						t_pt = 0
						t_pb = 0
#					print("Current ch = " + str(ch))
					if (j[0]==ch+1):
						###print("Checking TP" + str(j))
						###print("Time diff = "+ str(abs(i[1]-j[1])<=time_diff))
						###print("Chnl contig = " + str(j[0] == (ch+1)))
						t_jt = j[1]+j[5]
						t_jb = j[1]
						t_pt = p[1]+p[5]
						t_pb = p[1]
						if ( (t_jb>=t_pb and t_jb<=t_pt) or (t_jt>=t_pb and t_jt<=t_pt) or (t_pt<=t_jt and t_pb>=t_jb)) :
							#print("Considering hit "+str(j))
							if (horiz_noise_cnt == 0):
								horiz_tb = t_pb
								horiz_tt = t_pt
							if (j[0]==n[0]):#throw out events with more than one TP in a channel in the track
						#		print("Break due to multiple TPs in channel")
								break
								#return (False,0,0,0,0)
							hitfound = True
							###print("Possible track hit found = " + str(j))
							##print("time_diff =" + str(time_diff))
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
							

				#backward check
				ch = i[0] #current channel in loop
				##print("self.firsthit = " +str(self.firsthit))
				p = i #previous hit confirmed in track in previous channel
				n = i #current hit considered best fit for next hit in track in channel after p
				t_jt = 0
				t_jb = 0
				t_pt = 0
				t_pb = 0
				deadcnt = 0 #number of deadchannels we've skipped
				#chnlwid = 0 #for contiguous tolercance > 2
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
					for q in np.arange(Q,-1,-1):#loop through all TPs (which are ordered by channel), check if current TP j is iin the channel ch+1	
					#for j in self.TPlist:	
						j = self.TPlist[q]#current hit in list being considered
				#		if (j[0]>(ch-1)):
				#			continue
				#		else:
				#			TPcnt += 1
						if(j[0]<=(ch-2)):
							ch = n[0]
							if (hitfound==False):#check for missed hits
#								print("Missing hits in track ended search")
								break
							if (self.deadch[ch-1] == 0 and j[0]!=ch-1):
							#if (self.deadch[ch-1] == 0 and j[0]<(ch-2)):
								if(p[0]==i[0]):
									slope = 0
								elif(p[0]==sb[0]):
									slope = float(p[1]+p[5]/2-i[1]-i[5]/2)/float(p[0]-i[0])
								else:
									slope = float(p[1]+p[5]/2-sb[1]-sb[5]/2)/float(p[0]-sb[0])
								deadcnt = 0
								while (self.deadch[ch-1]==0 and (ch-1)>self.colstart):
									ch-=1
#									print("Skipping through dead channel:"+str(ch))
									deadcnt+=1	
								#print("deadcnt =" + str(deadcnt))
								p[1]=p[1]-np.floor(float(slope)*float(deadcnt))
							if (hitfound==True):
								#print("Track hit found = " + str(n))
								braggcnt+=1
								#print("braggcnt = " + str(braggcnt))
								if (braggcnt == tracklen/2+3):
									sb = n
									#print("sb found = " + str(sb))
								if (braggcnt >= tracklen):
								#	chcnt = chcnt - j[0]-1
								#	print("chcnt " + str(chcnt))
								#	timewid = time_max - time_min
								#	print("timewid " + str(timewid))
								#	TPvol = chcnt * timewid
								#	TPdensity = 0
								#	if TPvol!=0:
								#		TPdensity = TPcnt/TPvol
									backslope_top = float(n[1]+n[5]-sb[1]-sb[5])/float(n[0]-sb[0])
									backslope_mid = float(n[1]+n[5]/2-sb[1]-sb[5]/2)/float(n[0]-sb[0])
									backslope_bottom = float(n[1]-sb[1])/float(n[0]-sb[0])
									frontangle_top = math.degrees(math.atan(slopecm_scale*float(frontslope_top)))
									backangle_top = math.degrees(math.atan(slopecm_scale*float(backslope_top)))
									frontangle_mid = math.degrees(math.atan(slopecm_scale*float(frontslope_mid)))
									backangle_mid = math.degrees(math.atan(slopecm_scale*float(backslope_mid)))
									frontangle_bottom = math.degrees(math.atan(slopecm_scale*float(frontslope_bottom)))
									backangle_bottom = math.degrees(math.atan(slopecm_scale*float(backslope_bottom)))
								#	print("frontangle_top = " + str(frontangle_top) + "  backangle_top = " + str(backangle_top))
								#	print("frontangle_mid = " + str(frontangle_mid) + "  backangle_mid = " + str(backangle_mid))
								#	print("frontangle_bottom = " + str(frontangle_bottom) + "  backangle_bottom = " + str(backangle_bottom))
									#if (abs(frontangle_mid-backangle_mid)>13):
									if (abs(frontangle_mid-backangle_mid)>50 and abs(frontangle_top-backangle_top)>50 and abs(frontangle_bottom-backangle_bottom)>50):
									#	print("frontangle_top = " + str(frontangle_top) + "  backangle_top = " + str(backangle_top))
									#	print("frontangle_mid = " + str(frontangle_mid) + "  backangle_mid = " + str(backangle_mid))
									#	print("frontangle_bottom = " + str(frontangle_bottom) + "  backangle_bottom = " + str(backangle_bottom))
										#return (True,TPdensity,abs(frontangle_top-backangle_top),abs(frontangle_mid-backangle_mid),abs(frontangle_bottom-backangle_bottom))
										trigtot += 1
										print("Bragg peak TP found at " +str(i))
								#		print("TPdensity = " + str(TPdensity))
										peaklist.append(i)
										break
									else:
										break
										#return (False, 0, 0,0,0)
								p = n
								#ch=j[0]+1
					#		else:
					#			if(p[0]==i[0]):
					#				slope = 0
					#			else:
					#				slope = float(p[1]+p[5]/2-sb[1]-sb[5]/2)/float(p[0]-sb[0])
					#			chnlwid = ch-1-j[0]
					#		#	print("ch "+str(j[0]))
					#		#	print("chnlwid " + str(chnlwid))
					#			time_diff = 30*np.ceil(float(chnlwid)/float(deadwidthscale))
					#			temp_t = p[1] - np.floor(float(slope)*float(chnlwid))
					#		#	print("temp_t " + str(temp_t))
					#			if (abs(temp_t-j[1])<=time_diff):
					#		#		print("great success")
					#				p[1]=temp_t
					#				ch=j[0]+1
							hitfound = False
							t_jt = 0
							t_jb = 0
							t_pt = 0
							t_pb = 0
#						print("Current ch = " + str(ch))
						if (j[0]==ch-1):
							###print("Checking TP" + str(j))
							###print("Time diff = "+ str(abs(i[1]-j[1])<=time_diff))
							###print("Chnl contig = " + str(j[0] == (ch+1)))
							t_jt = j[1]+j[5]
							t_jb = j[1]
							t_pt = p[1]+p[5]
							t_pb = p[1]
							if ( (t_jb>=t_pb and t_jb<=t_pt) or (t_jt>=t_pb and t_jt<=t_pt) or (t_pt<=t_jt and t_pb>=t_jb)) :
							#	print("Considering hit "+str(j))
								if (horiz_noise_cnt == 0):
									horiz_tb = t_pb
									horiz_tt = t_pt
								if (j[0]==n[0]):
#									print("Break due to multiple TPs in channel")
									break
									#return (False,0,0,0,0)
								hitfound = True
							#	print("hitfound = True for " + str(j))
								###print("Possible track hit found = " + str(j))
								##print("time_diff =" + str(time_diff))
								n = j
								if (abs(t_jb - horiz_tb) <=1) or (abs(t_jt - horiz_tt) <=1):
									horiz_noise_cnt+=1
									if (horiz_noise_cnt>horiz_tolerance):
#										print("Break due to horiz noise")
										break
								else:
									horiz_noise_cnt = 0
								if (t_jt > time_max):
									time_max = t_jt
								if (t_jb < time_min):
									time_min = t_jt
								
		#return (False,0,0,0,0)		
		return (trigtot, peaklist)
