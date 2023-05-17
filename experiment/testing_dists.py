# -*- coding: utf-8 -*-
"""
Created on Tue May 16 15:25:54 2023

@author: canoluk
"""

# importing the required module
import matplotlib.pyplot as plt
import numpy as np
import PsiMarginal
from psychopy import core

# %% Psi Staircases
def makePsi(nTrials=32):
# Image visibility ranges between 2 and 40, logarithmically, 40 possibilities.
    sigma = np.linspace(0.05, 1, 21)
    staircase = PsiMarginal.Psi(stimRange=np.geomspace(2,40,40,endpoint=True),
            Pfunction='cGauss', nTrials=nTrials,
            threshold=np.geomspace(2,25,25, endpoint=True), #thresholdPrior=('gamma',3,35),
            thresholdPrior=('normal',15,10), #slope=5,#
            slope=sigma,slopePrior=('gamma',4,4),# slopePrior=('gamma',2,0.3), # with these values, the contrast starts at ~15 and can end up at ~2 in 32 trials.
            guessRate=0.5,
            lapseRate=0.05, #lapsePrior=('beta',0.05,0.1), 
            lapsePrior = ('beta', 2,20),
            marginalize=False)
    return staircase
# nTrials is trials PER staircase sigma is slope

congup=makePsi()
print(congup.xCurrent)

a=[]
n_i=[]
for i in range(16):
      if i % 3 == 0:
          core.wait(1)
          print(congup.xCurrent)
          congup.addData(1)
          core.wait(0.5)
          a.append(congup.xCurrent)
          n_i.append(len(a))
          congup.addData(0)
          core.wait(0.5)
          a.append(congup.xCurrent)
          n_i.append(len(a))
      else:
          core.wait(1)
          print(congup.xCurrent)
          congup.addData(1)
          core.wait(0.5)
          a.append(congup.xCurrent)
          n_i.append(len(a))
          congup.addData(1)
          core.wait(0.5)
          a.append(congup.xCurrent)
          n_i.append(len(a))
plt.plot(n_i,a)      

