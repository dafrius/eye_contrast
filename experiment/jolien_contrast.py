

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 14:41:32 2022

@author: schuurmans
"""


# %% Package imports
import os
import numpy as np
import numpy.random as rnd
from psychopy import visual, event, core, gui, data, monitors
from PIL import Image # this is used to manipulate images and do the alpha-blending
import PsiMarginal # this is important because it is actually importing from another file in the same folder (PsiMarginal.py)
import csv


# %% Paths
stimPath="exp_imgs"
maskPath="masks"
dataPath="data"
asfx='.png'

# %% Monitor setup 



# Subject Info

exp_name = 'Eye Contrast'
exp_info = {
        'participant': '',
        'gender': ('male', 'female'),
        'age':'',
        'screenwidth(cm)': '59',
        'screenresolutionhori(pixels)': '1920',
        'screenresolutionvert(pixels)': '1080',
        'refreshrate(hz)': '60' #ViewPixx - Change this (120)
        }

dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)
    

# If 'Cancel' is pressed, quit
if dlg.OK == False:
    core.quit()
        
# Get date and time
exp_info['date'] = data.getDateStr()
exp_info['exp_name'] = exp_name



mon = monitors.Monitor('Dell') #Pulls out photometer calibration settings by name.  
# Change this if you are using the ViewPixx (you should find the proper name in PsychoPy Monitor Center)
mon.setDistance(57)
mon.setWidth(float(50)) # Cm width
horipix = 1920
vertpix = 1080
framerate = 60
scrsize = (float(horipix),float(vertpix))
framelength = 1000/(float(framerate))
mon.setSizePix(scrsize)
mon.setDistance(57)
mon.setWidth(50)
mon.setSizePix(scrsize)



# %% Open a window
win = visual.Window(monitor = mon, 
                    size = scrsize,
                    color='grey',
                    units='deg', #you can change this to pixels/cm
                    fullscr=True,
                    allowStencil=True,
                    screen=1)
# Hide the cursor when the window is opened
win.mouseVisible=False

# %% Timing
IBW=3 #the wait between the blocks
#IBW=0.1
ISI = [.7, .8, .9, 1, 1.1, 1.2]
#ISI=[.01, .02]
FixT = 500
IntT = 500
TargetT = 500
MaskT = 200
FixFrame = int(FixT/framelength)
IntFrame = int(IntT/framelength)
ImFrame = int(TargetT/framelength)
MaskFrame = int(MaskT/framelength)


# %% Fixation Cross
fixation = visual.ShapeStim(win, 
    vertices=((0, -0.3), (0, 0.3), (0,0), (-0.3,0), (0.3, 0)),
    lineWidth=3,
    closeShape=False,
    lineColor="black"
    )

# %% Pulling images out, putting them in a variable
# We take all the images in the folder and put them in a list
imlist=os.listdir(os.path.join(stimPath))
masklist=os.listdir(os.path.join(maskPath))
ims=[]
ims2=[]
masks=[]
#we create the new variable, called ims, which contains all the pixel information of all the images
for i in range(0, len(imlist)):
    ims.append(Image.open(os.path.join(stimPath,imlist[i]), mode="r"))
    ims2.append({'imname':imlist[i],'image':Image.open(os.path.join(stimPath,imlist[i]), mode="r")})
    masks.append(Image.open(os.path.join(maskPath,masklist[i]), mode="r"))
# we convert it into numpy arrays
ims = np.array([np.array(im) for im in ims])
masks = np.array([np.array(mask) for mask in masks])/256







# Contexts and Eyes to be used
mencxts = ['123','44' ,'17','125', '52','145','160','24','46','2','151', '49','147','146','25' , '7']
meneyes=  ['100','125','38', '9' ,'148', '66','76' ,'2' ,'93','8', '87','146','25' ,'7'  ,'147','55']
womcxts = ['139','103','197','135','111','192','131','129','65','41','208','20','96','13','225','128']
womeyes = ['197','135','103','192','216','220','37','94','208','20','65','13','225','128','96','30']
    
# All the images to be shown
# this loop basically does this selection for the above lists (mencxts, meneyes, womcxts, womeyes):
    # [cxt]+[eye]
    # 0+1
    # 0+0
    # 1+1
    # 1+0
    # 2+3
    # 2+2
    # 3+3
    # 3+2
    #  .
    #  .
# to make the combinations of the images we have and put them in a list to use later.
# Second part of the loop (just Iso eyes) goes through the eyes list and adds them to the list as well.)

imnow =[]
for sex in ['men','wom']:    
    for eyes,cxts in zip(range(1,len(meneyes)+1,2), range(0,len(mencxts)+1,2)):
        for cxtind in range(2):
            for eyeind in range(0,-2,-1):
                if sex == 'men':
                    imnow.append(mencxts[cxts+cxtind]+'-'+meneyes[eyes+eyeind]+'.png')
                else:
                    imnow.append(womcxts[cxts+cxtind]+'-'+womeyes[eyes+eyeind]+'F.png')
        for eyeind in range(0,-2,-1): # adding iso eyes
            if sex == 'men':
                imnow.append(meneyes[eyes+eyeind]+'_eyes.png')
            else:
                imnow.append(womeyes[eyes+eyeind]+'_eyes.png')
                
# imnow now has:
    # F0E1
    # F0E0
    # F1E1
    # F1E0
    # E0
    # E1
    # F2E3
    # F2E2
    # F3E3
    # F3E2
    # E2
    # E3
    # in that order


# Creating the trials with balanced number of conditions, orientations, image occurrences using the order above
# adding isos to the dataset changed the format alittle bit, now here I need to change it every 6 items.
combos_new={'ssup': [] , 'ssinv': [],'sdup': [], 'sdinv': [],
    'dsup': [], 'dsinv': [],'ddup': [], 'ddinv': [],
    'isosup': [], 'isosinv': [],'isodup': [], 'isodinv': []}

for ori in ['up', 'inv']:
        for imgroup in range(3,len(imnow),6):
            for im1 in range(4):
                for im2 in range(4):
                    condition=''
                    orientation = ori
                    for cxteye in range(2):
                        if imnow[imgroup-im1].split('-')[cxteye] == imnow[imgroup-im2].split('-')[cxteye]:
                            condition+='s'
                        else:
                            condition+='d'           
                    combos_new[condition+ori].append({'im1name':imnow[imgroup-im1],'im2name':imnow[imgroup-im2],'cond':condition,'ori':orientation,
                        'mask':imnow[imgroup-im1].split('.')[0]+'_mask.png',
                        'rt':0, 'acc':0, 'contrast':0, 'trialno':0})
        for i in range(2):
            for imgroup in range(5, len(imnow), 6):
                for im1 in range(2):
                    for im2 in range(2):
                        orientation = ori
                        if imnow[imgroup-im1] == imnow[imgroup-im2]:
                            condition='isos'
                        else:
                            condition='isod'
                        combos_new[condition+ori].append({'im1name':imnow[imgroup-im1],'im2name':imnow[imgroup-im2],'cond':condition,'ori':orientation,
                        'mask':imnow[imgroup-im1].split('.')[0]+'_mask.png',
                        'rt':0, 'acc':0, 'contrast':0, 'trialno':0})




# here we shuffle trials from each condition within the condition block
for cond in combos_new.keys(): 
    rnd.shuffle(combos_new[f"{cond}"])



# Making sure all big blocks have equal number of each condition
# 8 big blocks, each have 6 miniblocks of length 16, 
# each miniblock has different condition

# in a single miniblock, we want only the same condition
# 16 trials
# 6 miniblocks (one for each condition (s*up,d*up,iso*up,s*inv,d*inv,iso*inv))
# 8 big blocks.


miniblock_length=16
n_miniblocks=6
n_bigblocks=8
blocks=[]
tempblock=[]
for ori in ['up','inv']:
    for cond in ['s','d','iso']:
        for ctr in range(0,len(combos_new['ssup']),int(miniblock_length/2)):
            for i in range(int(miniblock_length/2)):
                tempblock.append(combos_new[f"{cond}s{ori}"][ctr+i])
                tempblock.append(combos_new[f"{cond}d{ori}"][ctr+i])
            rnd.shuffle(tempblock)
            blocks.append(tempblock)
            tempblock=[]

# we now created 48 miniblocks, in the correct order 
# [same up * 8, diff up * 8, iso up * 8, same inv * 8, diff inv * 8, iso inv * 8]
# and we need to make big blocks (a block made of 6 miniblocks) with each 
# condition once in it.



blocks2=[]
bigblock=[]
for bigs in range(8):
    for block in range(0,len(blocks),8):
        bigblock.append(blocks[block+bigs])
    rnd.shuffle(bigblock)
    blocks2.append(bigblock)
    bigblock=[]
    
# you should go to Helene for this something something something


final_blocks=[]
for i in range(len(blocks2)):
    for j in range(len(blocks2[i])):
        final_blocks.append(blocks2[i][j])


# expectedResult = [d for d in exampleSet if d['type'] in keyValList]
# exTrials= data.TrialHandler(combos, nReps=1, method='sequential', originPath=dataPath)
    

# %% Printing things to check ####
# fieldnames=list(combos_new['ssup'][0].keys())
# f = open('combos9.csv','w',encoding='UTF8', newline='')
# writer2=csv.DictWriter(f, fieldnames=fieldnames)
# writer2.writeheader()
# a=0
# for block in final_blocks:
#     for trial in block:
#         writer2.writerow(trial)
#         a+=1
#         print(a)
# f.close()


# %% Shortcut to make Psi Staircases
def makePsi(nTrials=128, start_thresh=1.5): # start_thresh is signal strength in percentage
# Image visibility ranges between 1.5 and 40, logarithmically, 40 possibilities.
    staircase = PsiMarginal.Psi(stimRange=np.geomspace(start_thresh,40,40,endpoint=True),
            Pfunction='Weibull', nTrials=nTrials,
            threshold=np.geomspace(start_thresh,40,40, endpoint=True), 
            thresholdPrior=('normal',5,5), slope=np.geomspace(0.5, 20, 50, endpoint=True),
            guessRate=0.5, slopePrior=('gamma',3,6), lapseRate=0.05, lapsePrior=('beta',2,20), marginalize=True)
    return staircase
# nTrials is trials PER staircase
# sigma is slope

# initialize a staircase for each condition


#[f"{cond}s{ori}"]

sameup=makePsi()
diffup=makePsi()
isoup=makePsi()
sameinv=makePsi()
diffinv=makePsi()
isoinv=makePsi()

# %% Occlude function


def occlude(image, back, signal):
    # we take the contrast and luminance of the eye region, excluding the background
    #eyecontrast = np.std(image[60:540,140:300], ddof=1)
    #luminance=np.average(image[:])
    # we create an Alpha channel array for the image, fill it with 255s
    srcImg=image
    srcHeight, srcWidth = srcImg.shape[:]
    srcA = np.full([srcHeight,srcWidth], 255)
    # we initiate the occluder, as an image with same size as the source image,
    # fill it with zeros
    # and make an alpha channel for it.
    backImg=back
    backHeight, backWidth = backImg.shape[:]
    backA = np.full([backHeight, backWidth], 255)
    
    # alpha at its highest is 255, so we initiate another variable for that 
    # for easier operations later.
    fullAlpha=255 #needs to be 255
    # we reduce the Alpha transparency of the range of pixels that occluder 
    # will overlap
    srcA[:, :] = fullAlpha -((100-signal)/100*fullAlpha)
    backA[:, :] = ((100-signal)/100*fullAlpha)
    #we blend them, merge into a single image
    blend=(srcImg*(srcA/255))+(backImg*(backImg/255))
    return blend

blend = occlude(ims[1],masks[5],50)
Image.fromarray(blend.astype('uint8'))

# %% Final arrangements before showing it
bitmap1 = visual.ImageStim(win, size=[7.05,8.38], interpolate=True) 
bitmap2 = visual.ImageStim(win, size=[7.05,8.38], interpolate=True) 
bitmap_mask = visual.ImageStim(win, size=[7.05,8.38], interpolate=True)
change_clock = core.Clock()
rt_clock = core.Clock()

# %% Opening a file for writing the data
if not os.path.isdir(dataPath):
    os.makedirs(dataPath)
fieldnames=list(blocks[0][0].keys())
data_fname = exp_info['participant'] + '_' + exp_info['age'] + '_' + exp_info['gender'][0] + '_' + exp_info['date'] + '.csv'
data_fname = os.path.join(dataPath, data_fname)
f = open(data_fname,'w',encoding='UTF8', newline='')
writer=csv.DictWriter(f, fieldnames=fieldnames)
writer.writeheader()

def block_break(block_no):
    timer=3
    # timer=1
    blocktext = visual.TextStim(
                    win=win,
                    height=.5,
                    font="Palatino Linotype",
                    alignHoriz='center'
                    )   
    timertext = visual.TextStim(win=win,
            height=.5, 
            pos=[0,-5],
            font="Palatino Linotype",
            alignHoriz = 'center')
    if block_no % 6 == 0:
        timer=20
        # timer=0
    blocktext.text="""Please take a short rest before the next block.
    You can press "SPACE" to start again 
    after """ + str(timer) + """ seconds when you are ready.

    Block: """ + str(block_no) + """/48"""
    for time in range(timer):
        timer-=1
        blocktext.draw()
        timertext.text=""":""" + str(timer)
        timertext.draw()
        core.wait(1)
        win.flip()
        if timer == 0:
            timertext.text="""READY"""
            blocktext.draw()
            timertext.draw()
            win.flip()
    keys = event.waitKeys(keyList=['space','escape'])
    if 'escape' in keys:
        win.close()
        f.close()
    win.flip()
    core.wait(2)
                           


# fieldnames=list(blocks[0][0].keys())
# f = open('blocks.csv','w',encoding='UTF8', newline='')
# writer2=csv.DictWriter(f, fieldnames=fieldnames)
# writer2.writeheader()
# for block in final_blocks:
#     for trial in block:
#         writer2.writerow(trial)


# We draw the text explaining what we will show
instructions = visual.TextStim(
    win=win,
    pos=[0,6],
    wrapWidth=None,
    height=.5,
    font="Palatino Linotype",
    alignHoriz='center'
    )

    
instructions.text = """
In this experiment, you will see two faces (or eyes) displayed one after another.\n 
Your task is to report whether the eye region (eyes and brows) \n of the subsequently showed faces were identical or different."""
instructions.draw()

instructions2=instructions
instructions2.text = """
If the eye regions are the SAME, press "S", if they are different, press "L"\n\n 

Press SPACE key to continue.
"""

instructions2.pos=[0,0]
instructions2.draw()

win.flip()
keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)

# %% Trial loop
i=0
block_no = -1
for block in final_blocks:
    block_no += 1
    if block_no > 0:
        block_break(block_no)
    for trial in block:
        if trial['ori']=='up':
            ori=180
            if trial['cond'][0] == 's' :
                while sameup.xCurrent == None:
                    pass # hang in this loop until the psi calculation has finished
                visibility = sameup.xCurrent
            elif trial['cond'][0] == 'd':
                while diffup.xCurrent == None:
                    pass
                visibility = diffup.xCurrent
            elif trial['cond'][0] == 'i':
                while isoup.xCurrent == None:
                    pass
                visibility = isoup.xCurrent
        else:
            ori=0
            if trial['cond'][0] == 's':
                while sameinv.xCurrent == None:
                    pass # hang in this loop until the psi calculation has finished
                visibility = sameinv.xCurrent
            elif trial['cond'][0] == 'd':
                while diffinv.xCurrent == None:
                    pass
                visibility = diffinv.xCurrent
            elif trial['cond'][0] == 'i':
                while isoinv.xCurrent == None:
                    pass
                visibility = isoinv.xCurrent
            
        im1=np.array(Image.open(os.path.join(stimPath,trial['im1name'])))
        im2=np.array(Image.open(os.path.join(stimPath,trial['im2name'])))
        mask=(np.array(Image.open(os.path.join(maskPath,trial['mask']))))/256
        im1us=occlude(im1,visibility)
        im1=(im1us-127.5)/127.5
        im2us=occlude(im2,visibility)
        im2=(im2us-127.5)/127.5
        mask_occluded=occlude(mask, visibility)
        maskfinal=(mask_occluded-127.5)/127.5 # .5 is the midvalue so you'd do (x-.5)/.5
        
        bitmap1.setOri(ori)
        bitmap2.setOri(ori)
        bitmap_mask.setOri(ori)
        
        # you don't need this
        if trial['ori']== 'up':
            eyeleveling=-1.18 
            # eyeleveling=-1.38
        else:
            eyeleveling=1.18
            # eyeleveling=1.38
        
        bitmap1.pos=(0,eyeleveling) #142+284/2 (5.1 is equal to 142 pixels, then we add half of the horizontal size (7/2) because pos. takes the center to the defined location.)
        bitmap2.pos=(0,eyeleveling)
        bitmap_mask.pos=(0,eyeleveling)
        
        
        
        
         
        bitmap1.setImage(im1)
        bitmap2.setImage(im2)
        bitmap_mask.setImage(maskfinal)
        
        for nFrames in range(FixFrame): # 600 ms.
                fixation.draw()
                win.flip()
                
        for nFrames in range(IntFrame):  # 500 ms
                win.flip()
            
        for nFrames in range(ImFrame): # 500 ms
                bitmap1.draw()
                win.flip()
                    
        for nFrames in range(MaskFrame): # 200 ms
               bitmap_mask.draw() # We don't have a mask right now
               win.flip()
               
               
        bitmap2.draw()
        win.flip()
        change_clock.reset()
        rt_clock.reset()
                                        
        # Wait until a response, or until time limit.
        # keys = event.waitKeys(maxWait=timelimit, keyList=['s','l', 'escape'])
                 
        keys = event.waitKeys(keyList=['s','l','escape','p'])     
        if keys:
            rt = rt_clock.getTime()
            # fixation.clearTextures()
            
        bitmap1.clearTextures()
        bitmap2.clearTextures()
        win.flip()
        
        if not keys:
            keys = event.waitKeys(keyList=['s','l','escape'])
            rt = rt_clock.getTime()
                           
        acc = 0
        if keys:
            if 'escape' in keys:
                f.close()
                win.close()
                # exTrials.saveAsWideText('Exp_full' + '.csv', delim=',')
                win.mouseVisible=True
                break
            elif 's' in keys and (trial['cond'] == 'ss' or trial['cond'] == 'ds' or trial['cond'] == 'isos'): # is same
                acc = 1
            elif 'l' in keys and (trial['cond'] == 'sd' or trial['cond'] == 'dd' or trial['cond'] == 'isod'): # is different
                acc = 1         
                
        trial['acc']=acc
        trial['rt']=rt
        trial['contrast']=visibility
        trial['trialno']=i
        # exTrials.addData('acc', acc)
        # exTrials.addData('rt', rt)
        # exTrials.addData('visib',visibility)
        i+=1

        # Update staircase        

        if ori==180:
            if trial['cond'][0] == 's' :
                sameup.addData(acc)
            elif trial['cond'][0] == 'd':
                diffup.addData(acc)
            elif trial['cond'][0] == 'i':
                isoup.addData(acc)
        else:
            if trial['cond'][0] == 's':
                sameinv.addData(acc)
            elif trial['cond'][0] == 'd':
                diffinv.addData(acc)
            elif trial['cond'][0] == 'i':
                isoinv.addData(acc)
        writer.writerow(trial)

f.close()
# exTrials.saveAsWideText('Exp_full' + '.csv', delim=',')
win.close()
win.mouseVisible=True

