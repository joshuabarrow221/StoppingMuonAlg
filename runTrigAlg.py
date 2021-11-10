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


sys.path.append(".")

from TriggerAlg import TriggerAlg
from datetime import datetime
start = datetime.now()

inputTP=[]
#tp = GenerateTP("ChnlMap.txt")

tp = TriggerAlg("NameofInputTPList")
peaklist = tp.maxADCtp()
finish = datetime.now()

#print (len(mainlistcol))
#print(len(stitchedTP))
#print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!! FIRST HIT !!!!!!!!!!!!!!!!!!!!!!! : " +str(firsthit) )
#framelist = tp.frameinfo()
#print(framelist)
#for x in framelist:
#    print(x)

print("Start: " + str(start))
#print("Mid1: " + str(mid1))
#print("Mid2: " + str(mid2))
print("Finish: " + str(finish))
print(finish-start)

