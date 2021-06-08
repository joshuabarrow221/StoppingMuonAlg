#Originally written by XXXXX
#Used for testing and demonstration by J. L. Barrow
#06/2021
#Scripts will be changed for multipronged triggering

#!/usr/bin/env python3
#Fake signal to test MichelTrigger.py

import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import ROOT

sys.path.append(".")

#from MichelTrigger import MichelTrigger
from prototypeMichelTrigger_maxADC_EXTboxes import prototypeMichelTrigger_maxADC_EXTboxes
#from prototypeMichelTrigger import prototypeMichelTrigger
from datetime import datetime

start = datetime.now()
trig_eff = 0
#chnlno = 3456 #number collection channels
#ubchnltot = 8256 #numbr of total uB chnls

#chnloffset =ubchnltot-chnlno #starting number of collection channels within full uB channel range
#trig = prototypeMichelTrigger_maxADCnoEXTboxes("MCC9_channel_list.txt")
trig = prototypeMichelTrigger_maxADC_EXTboxes("MCC9_channel_list.txt")
#trig = prototypeMichelTrigger("MCC9_channel_list.txt")
#f_str = "Merged_TriggerPrimitiveOfflineAnalyzer_v2.0_hist.root"#signal
f_str = "Merged_TriggerPrimitiveOfflineAnalyzer_hist_EXT.root"#EXT only
#f_str = "MergedTPs_stopmu_MCOnly_4_27_21.root"#MC signal only 13k events
#f_str = "TPsMerged_thrugomuon_5_13_21.root"#thrugomuno Corsika Background 70k events
print("Opening " + f_str)
f=ROOT.TFile.Open(f_str)
t = f.Get("tpm/event_tree")
#t = trig.openFile(f_str)
#print("TEST t.GetEntries() = " + str(t.GetEntries()))
numEvents = trig.getNumEvents(t)
kinkangle_top = []
kinkangle_mid = []
kinkangle_bottom = []
trigtot = 0
trigtotlist = []
#trig_result1 = 0
#trig_result2 = 0
#trig_result3 = 0
#trig_result4 = 0
#trig_result5 = 0
print("Total number of events = " + str(numEvents))
#for x in range(0,1000):
nE = 500
for x in range(0,nE):#numEvents
	#print("Event = " + str(x))
	if (x%100 == 0):
		print(str(float(x)*100.0/float(numEvents)) +"% completed")
	trig.readFile(t,x)
	#trig_result1,trig_result2,trig_result3, trig_result4, trig_result5 = trig.searchMichel()
	trigtot,peaklist = trig.searchMichel()
	if (trigtot>0):
		trig_eff+=1
		print("Event triggered on = " + str(x))
		print("trigtot = " + str(trigtot))
		trigtotlist.append(trigtot)
		#kinkangle_top.append(trig_result3)
		#kinkangle_mid.append(trig_result4)
		#kinkangle_bottom.append(trig_result5)
	#trig.clearTPs()
	

trig_eff = float(trig_eff)/float(numEvents)*100.0
print("Total number of events = " +str(numEvents))
print("Total of events run over = " +str(nE))
print("Percent of events triggered on = " +str(trig_eff))
finish = datetime.now()
print("Start time = " + str(start))
print("Finish time = " + str(finish))
hist_bins = np.linspace(0,20,21)
hist_trigtot = plt.hist(trigtotlist,bins=hist_bins)
plt.ylabel("Triggered Events")
plt.title("Number of Triggers Sent Per Single EXT Event Using Subregions")
plt.xlabel("Number of Triggers")
plt.savefig("histogram_numtrigssubregions_EXT_6_3_2021.png", bbox_inches='tight')
plt.show()
#plt.show()
#h_mid = plt.hist(kinkangle_mid,bins=hist_bins)
#plt.ylabel("Triggered Events")
#plt.title("Mid Kink Angle of Triggered EXT Events")
#plt.xlabel("Kink Angle (Degrees)")
#plt.savefig("histogram_kinkanglemid_selected50degreesEXT_6_2_2021.png", bbox_inches='tight')
#plt.show()
#h_top = plt.hist(kinkangle_top,bins=hist_bins)
#plt.ylabel("Triggered Events")
#plt.title("Top Kink Angle of Triggered EXT Events")
#plt.xlabel("Kink Angle (Degrees)")
#plt.savefig("histogram_kinkangletop_selected50degreesEXT_6_2_2021.png", bbox_inches='tight')
#plt.show()
#h_bottom = plt.hist(kinkangle_bottom,bins=hist_bins)
#plt.ylabel("Triggered Events")
#plt.title("Bottom Kink Angle of Triggered EXT Events")
#plt.xlabel("Kink Angle (Degrees)")
#plt.savefig("histogram_kinkanglebottom_selected50degreesEXT_6_2_2021.png", bbox_inches='tight')
#plt.show()
#plt.title("Density of TPs in Triggered MC Only Events")
