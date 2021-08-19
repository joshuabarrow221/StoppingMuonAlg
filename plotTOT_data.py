#!/usr/bin/env python3
#Plotting code for TPs
#Harrison Siegel, Columbia University 2021

import numpy as np
import sys
import matplotlib.colors as clrs
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import ROOT

sys.path.append(".")

from prototypeMichelTrigger_maxADC_EXTboxes import prototypeMichelTrigger_maxADC_EXTboxes


def make_TP_boxes(ax, xdata, ydata, ywid, zdata, facecolor='r',
                     edgecolor='None', alpha=1, my_cmap = cm.get_cmap('viridis')):

	# Loop over data points; create box at each point with normalized color
	norm = clrs.Normalize(min(zdata),max(zdata))
	cmmapable = cm.ScalarMappable(norm, my_cmap)
	#print("MIN ADC " + str(int(min(zdata))))
	#print("MAX ADC " + str(int(max(zdata))))
	cmmapable.set_array(range(int(min(zdata)), int(max(zdata))))
	for x, y, tot, z in zip(xdata, ydata, ywid, zdata):
		ax.add_patch(Rectangle((x - 0.5, y), 1, tot, facecolor = my_cmap(norm(z)), zorder = 10, alpha = alpha, edgecolor = edgecolor))
	# Add collection to axes
	cbar = plt.colorbar(cmmapable)

	return cbar

f_str = "MergedTPs_stopmu_MCOnly_4_27_21.root"
f=ROOT.TFile.Open(f_str)
tree = f.Get("tpm/event_tree")
print("Opening " + f_str)
tree.GetEntry(int(sys.argv[1]))
#print("muon_mctruth_capture_or_decay=="+str(tree.muon_mctruth_capture_or_decay[0]))
#print("muon_mctruth_dau_process=="+str(tree.muon_mctruth_dau_process[0]))

chnlno = 3456 #number collection channels
ubchnltot = 8256 #numbr of total uB chnls
chnloffset =ubchnltot-chnlno #starting number of collection channels within full uB channel range
trig = prototypeMichelTrigger_maxADC_EXTboxes("MCC9_channel_list.txt")
#Set up fake list of TPs to trigger on

#SAMPLE 8: signal-only MC
trig.clearTPs()
x_p = []#for plotting, channel
y_p = []#for plotting, first time tick
z_p = []#for plotting, integrated ADC
tot_p = []#for plotting tot width in y dir
trig.readFile(f_str,int(sys.argv[1]))
#trig.readFile("TPsMergedStopMuMCOnly_5_14_21.root",int(sys.argv[1]))#MC 48k events
#trig.readFile("MergedTPs_stopmu_MCOnly_4_27_21.root",int(sys.argv[1]))#MC only file 13k
#trig.readFile("TriggerPrimitiveAnalyzer_hist_Full750_5_18_21.root",int(sys.argv[1]))#MC only with decay and absorption info
#trig.readFile("horizontalTPstest_TriggerPrimitiveAnalyzer_hist.root",int(sys.argv[1]))#horizontal TP test
#trig.readFile("TPsMerged_4_30_21_signal.root",int(sys.argv[1]))#main overlay file
#trig.readFile("TPsMerged_CorsikaBkgnd_5_11_21.root",int(sys.argv[1]))#Corsika Backgrounds
#trig.readFile("TPtest2_5_13_21.root",int(sys.argv[1]))#test
#trig.readFile("TriggerPrimitiveAnalyzer_hist.root",int(sys.argv[1]))#small MC only file

TPL = trig.getTPlist()
for t in TPL:
	#if t[2]<50000:
	if t[1]>3199 and t[1]<7801:
		x_p.append(t[0])
		y_p.append(t[1])
		z_p.append(t[2])
		tot_p.append(t[5])
#print("X!!")
#print(x_p)
#print("Y!!")
#print(y_p)
#print("Z!!")
#print(z_p)
#print("TPs below")
#trig.printTPs()
#print("\n\n")
#PLOTTING
# Create figure and axes
fig, ax = plt.subplots(1)

minx = min(x_p)
print(minx)
maxx = max(x_p)
miny = min(y_p)
maxy = max(y_p)
#plot dead channels as vertical lines
dead = trig.getdeadch_list()
w = 0
for e in dead:
	if (w==4800 or w==8255):
		plt.axvline(x=w, linewidth = 0.25, c='r',zorder=0)
	if (e == 0 and w<=ubchnltot and w>=4800):
	#if (e == 0 and w<=(maxx+50) and w>=(minx-50)):
	#if (e == 0 and w>=minx and w<=maxx):
		plt.axvline(x=w, linewidth = 0.25, c='grey',zorder=0)
	w+=1
_ = make_TP_boxes(ax,x_p,y_p,tot_p,z_p)
#_.set_label("Total Integrated ADC/TOT")
_.set_label("Total Integrated ADC")
#plt.xlim(minx,maxx)
plt.xlim(minx-10,maxx+10)
plt.ylim(miny*0.95,maxy*1.05)
plt.xlabel("Channel")
plt.ylabel("Time ticks")
plt.title("Michel Event " + str(sys.argv[1]))
#plt.legend(["Michel e- trigger result = " + str(trig_result)])
plt.show()

