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

gammamu = 4
gammasd = 2
slps = [0.01, 0.2, 0.5, 4]
thresholdpriormus = [0.1]
thresholdpriorsds = [80, 100]
trialbreaks = [2, 3]

for slp in slps:
    for trialbreak in trialbreaks:
        for thresholdpriormu in thresholdpriormus:
            for thresholdpriorsd in thresholdpriorsds:
                def makePsi(nTrials=32):
                # Image visibility ranges between 2 and 40, logarithmically, 40 possibilities.
                    staircase = PsiMarginal.Psi(stimRange=np.geomspace(2,40,40,endpoint=True),
                            Pfunction='cGauss', nTrials=nTrials,
                            threshold=np.geomspace(0.1,40,25, endpoint=True), #thresholdPrior=('gamma',3,35),
                            thresholdPrior=('normal',thresholdpriormu,thresholdpriorsd), #slope=5,#
                            slope=slp,slopePrior=('gamma',gammamu, gammasd),# slopePrior=('gamma',2,0.3), # with these values, the contrast starts at ~15 and can end up at ~2 in 32 trials.
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
                      if i % trialbreak == 0:
                          print(congup.xCurrent)
                          congup.addData(1)
                          while congup.xCurrent == None:
                              pass                                      
                          a.append(congup.xCurrent)
                          n_i.append(len(a))
                          congup.addData(0)
                          while congup.xCurrent == None:
                              pass
                          a.append(congup.xCurrent)
                          n_i.append(len(a))
                      else:
                          print(congup.xCurrent)
                          congup.addData(1)
                          while congup.xCurrent == None:
                              pass
                          a.append(congup.xCurrent)
                          n_i.append(len(a))
                          congup.addData(1)
                          while congup.xCurrent == None:
                              pass
                          a.append(congup.xCurrent)
                          n_i.append(len(a))
                plt.plot(n_i,a)
                str1='gammamu='+str(gammamu)+',gammasd='+str(gammasd)+', \n slp='+str(slp)+',%'+str(trialbreak)+',thr_mu='+str(thresholdpriormu)+',thr_sd='+str(thresholdpriorsd)
                str2='gammamu='+str(gammamu)+',gammasd='+str(gammasd)+',slp='+str(slp)+',%'+str(trialbreak)+',thr_mu='+str(thresholdpriormu)+',thr_sd='+str(thresholdpriorsd)
                plt.title(str1)
                plt.savefig(str2+'.png')
                plt.close()
