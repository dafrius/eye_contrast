# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 15:04:39 2023

@author: canoluk
"""



# %% Package imports
import os
import numpy as np
import numpy.random as rnd
from psychopy import visual, event, core, gui, data, monitors, tools
from PIL import Image
import PsiMarginal
import csv
#import translators as ts


# %% Image Paths
stimPath="exp_imgs" 
maskPath="masks"
dataPath="data"
pracPath="prac_imgs"
pracmaskPath="prac_scrambles"

# Subject Info

exp_name = 'Eye Contrast'
exp_info = {
        'language' : ('fr','en'),
        'participant': '',
        'gender': ('male', 'female'),
        'age':'',
        'left-handed':False,
        'color_text': '-1',
        'screenwidth(cm)': '49',
        'screenresolutionhori(pixels)': '1920',
        'screenresolutionvert(pixels)': '1200',
        'refreshrate(hz)': '120',
        'prac_length': '6'}

dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)
    

# If 'Cancel' is pressed, quit
if dlg.OK == False:
    core.quit()
        
# Get date and time
exp_info['date'] = data.getDateStr()
exp_info['exp_name'] = exp_name
  
#%% Dictionary with all the instructions
instruction_dictionary = {'instructions1.text' : "Hello, \n\n Before starting, please make sure to find \n a comfortable position to do the task. \n\n Please adjust your chair so that the circle below is at your eye level. \n O \n\n Please try to stable \n as much as possible all along the experiment. \n \n \n Press SPACE key to continue.",
                          'instructions2.text': "In this experiment, two pictures of faces (or eyes) will be presented one after the other, successively. \n They will be displayed either UPRIGHT or INVERTED. \n YOUR TASK is to focus on the eye region (eyes and brows) in both faces \n and tell if they are exactly the same or different across faces. \n \n If the eyes are... \n IDENTICAL, press ""S"" key. \n DIFFERENT, press ""L"" key. \n\n Press a key to continue.",
                          'instructions3.text': "The task is quite difficult. \n We have manipulated the eyes and brows \n to contain varying levels of low contrast. \n You will see eyes in isolation, as well as inserted in various face contexts. \n\n\n\n\n\n Your task is to ignore the face context (when there is one), \n and only focus on the differences in the eye region (eyes and brows). \n\n\n It is important to keep your eyes fixated on the cross throughout the experiment." ,
                          'instructions4.text': "It is important that you are as FAST and CORRECT as possible.\n\n\n\n\n You will be trained with the task in the following practice trials. \n Press SPACE key to continue.",
                          'instructions5.text': "IDENTICAL eyes = ""S"" \n DIFFERENT eyes = ""L"" \n\n\n\n Place index fingers on these response keys before starting the experiment.\n Press SPACE key to start the practice.",
                          'prac1.text': "The task difficulty will increase now. Everything else about the task stays the same. \n\n IDENTICAL eyes = ""S"" \n DIFFERENT eyes = ""L"" \n Press SPACE key to continue the practice.",
                          'prac2.text': "IDENTICAL eyes = ""S"" \n DIFFERENT eyes = ""L""\n\n\n\n\n Press SPACE key to continue the practice.",
                          'pracfinal.text': "Congratulations, you passed the practice!\n You will now start the experiment. \n\n Press SPACE key to start.",
                          'timertext.text':"Ready",
                          'blocktext1.text': "Please take a short break before you start the next block. \n\nYou can press SPACE after ",
                          'blocktext2.text':" seconds to continue when you are ready. \n\n Block:"}

# %% Creation of a function to translate the instructions
# def intoenglish(input_dictionary,language): 
#     instruction_dictionary_english={} 
#     for k,phrase in input_dictionary.items():
#        translater = ts.google(phrase, from_language='fr', to_language=language)
#        instruction_dictionary_english[k] = translater
#     return instruction_dictionary_english

# #Now we translate the instruction if required
# if exp_info['language']!='fr':
#     language = exp_info['language']
#     instruction_dictionary=intoenglish(instruction_dictionary, language) 


# %% Monitor setup 
mon = monitors.Monitor('VPixx020523') #Pulls out photometer calibration settings by name.  
mon.setWidth(float(exp_info['screenwidth(cm)'])) # Cm width
mon.setDistance(57)
horipix = exp_info['screenresolutionhori(pixels)']
vertpix = exp_info['screenresolutionvert(pixels)']
framerate = exp_info['refreshrate(hz)']
scrsize = (float(horipix),float(vertpix))
framelength = 1000/(float(framerate))
mon.setSizePix(scrsize)

# how many rgb values do we lower the brightness
reduce=0

# the candela / metersquare value
cdm2 = (128-reduce)/255*100

# %% Open a window
win = visual.Window(monitor = mon, 
                    size = scrsize,
                    colorSpace = "rgb255",
                    color= [128-reduce, 128-reduce, 128-reduce],
                    units='deg',
                    fullscr=True,
                    allowStencil=True,
                    screen=1)
# Hide the cursor when the window is opened
win.mouseVisible=False

# %% Timing
IBW=3 #the wait between the blocks

ITI = [.7, .8, .9, 1, 1.1, 1.2] # inter-trial interval
# Fixation, Interval, Target, Mask times in ms
FixT, IntT, TargetT, MaskT = 500, 500, 500, 200
#FixT, IntT, TargetT, MaskT = 0, 0, 0, 0

# Fixation, Interval, Target, Mask times in terms of # of frames
FixFrame, IntFrame, ImFrame, MaskFrame = int(FixT/framelength), int(IntT/framelength), int(TargetT/framelength), int(MaskT/framelength)


# %% Fixation
fixation = visual.ShapeStim(win, 
    vertices=((0, -.2), (0, .2), (0,0), (-.2,0), (.2, 0)),
    lineWidth=2,
    closeShape=False,
    lineColor="black"
    )


# visual.ShapeStim(win, 
#     vertices=((0, -0.3), (0, 0.3), (0,0), (-0.3,0), (0.3, 0)),
#     lineWidth=3,
#     closeShape=False,
#     lineColor="black"
#     )

# %% Eye-Face Matching

# Contexts and Eyes to be used, these are arranged in a specific order 
# depending on which eye fits on which face perfectly, and which are the more 
# similar looking eyes as measured by pixel-wise correlations
# e.g., the first and second elements of cxts are matched with first and second
# elements of eyes. the combination of the four creates a 'quad' mixing and
# matching the all possible elements.
mencxts = ['123','44' ,'17','125', '52','145','160','24','46','2','151', '49','147','146','25' , '7']
meneyes=  ['100','125','38', '9' ,'148', '66','76' ,'2' ,'93','8', '87','146','25' ,'7'  ,'147','55']
womcxts = ['139','103','197','135','111','192','131','129','65','41','208','20','96','13','225','128']
womeyes = ['197','135','103','192','216','220','37','94','208','20','65','13','225','128','96','30']
    
# All the images to be shown
# this loop below basically does this selection for the above lists    
# (mencxts, meneyes, womcxts, womeyes):
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

    # Here we do the same operation, but this time with practice images

praccxts = ['21', '223', '31', '224', '37', '203', '78', '214','106', '226', '154', '209']
praceyes=  ['154', '209', '106', '226', '214', '224', '37' ,'203' ,'31','163', '21','78'] 

pracnow=[]
for eyes,cxts in zip(range(1,len(praceyes)+1,2), range(0,len(praccxts)+1,2)):
    for cxtind in range(2):
        for eyeind in range(0,-2,-1):
            pracnow.append(praccxts[cxts+cxtind]+'-'+praceyes[eyes+eyeind]+'.png')
    for eyeind in range(0,-2,-1): # adding iso eyes
            pracnow.append(praceyes[eyes+eyeind]+'_eyes.png')
 

    
# %% Trial order
# Creating the trials with balanced number of conditions, orientations, image occurrences using the order above

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

# creating blocks with equal numbers of trials and corresponding staircases
# for each condition

blocks=[]
tempblock=[]
n_blocks=16 
block_length=48 # Should be multipliers of 12
repetition=block_length/len(combos_new.keys()) # Should be a
ctr=0

for blockno in range(n_blocks):
    for rep in range(int(repetition)):
        for cond in combos_new.keys():
            if rep < repetition/2:
                combos_new[f"{cond}"][int(ctr)+rep]['staircase']=1
            else:
                combos_new[f"{cond}"][int(ctr)+rep]['staircase']=2
            tempblock.append(combos_new[f"{cond}"][int(ctr)+rep])
    ctr=ctr+repetition    
    rnd.shuffle(tempblock)
    blocks.append(tempblock)
    tempblock=[]
    
# This is to write them in a csv file for checking the balances in rstudio later
# fieldnames=list(blocks[0][0].keys())
# with open('firstcheck2.csv', 'w',newline='') as csvfile:
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#     writer.writeheader()
#     for i in range(len(blocks)):
#         for j in range(len(blocks[0])):
#             writer.writerow(blocks[i][j])

    
# %% Trial Order - Practice

pracs_new={'ssup': [] , 'ssinv': [],'sdup': [], 'sdinv': [],
    'dsup': [], 'dsinv': [],'ddup': [], 'ddinv': [],
    'isosup': [], 'isosinv': [],'isodup': [], 'isodinv': []}

for ori in ['up', 'inv']:
        for imgroup in range(3,len(pracnow),6):
            for im1 in range(4):
                for im2 in range(4):
                    condition=''
                    orientation = ori
                    for cxteye in range(2):
                        if pracnow[imgroup-im1].split('-')[cxteye] == pracnow[imgroup-im2].split('-')[cxteye]:
                            condition+='s'
                        else:
                            condition+='d'           
                    pracs_new[condition+ori].append({'im1name':pracnow[imgroup-im1],'im2name':pracnow[imgroup-im2],'cond':condition,'ori':orientation, 'mask':pracnow[imgroup-im1].split('.')[0].split('-')[0]+'_mask.png', 'rt':0, 'acc':0, 'contrast':0, 'trialno':0})
        for i in range(2):
            for imgroup in range(5, len(pracnow), 6):
                for im1 in range(2):
                    for im2 in range(2):
                        orientation = ori
                        if pracnow[imgroup-im1] == pracnow[imgroup-im2]:
                            condition='isos'
                        else:
                            condition='isod'
                        pracs_new[condition+ori].append({'im1name':pracnow[imgroup-im1],'im2name':pracnow[imgroup-im2],'cond':condition,'ori':orientation, 'mask':pracnow[imgroup-im1].split('.')[0].split('_')[0]+'_mask.png', 'rt':0, 'acc':0, 'contrast':0, 'trialno':0}) 

for cond in pracs_new.keys():
    rnd.shuffle(pracs_new[f"{cond}"])

            
pracblocks=[]
tempblock=[]
n_blocks=6 
block_length=48 # Should be multipliers of 12
repetition=block_length/len(pracs_new.keys()) # Should be a
ctr=0

for blockno in range(n_blocks):
    for rep in range(int(repetition)):
        for cond in pracs_new.keys():
            if rep < repetition/2:
                pracs_new[f"{cond}"][int(ctr)+rep]['staircase']=1
            else:
                pracs_new[f"{cond}"][int(ctr)+rep]['staircase']=2
            tempblock.append(pracs_new[f"{cond}"][int(ctr)+rep])
    ctr=ctr+repetition    
    rnd.shuffle(tempblock)
    pracblocks.append(tempblock)
    tempblock=[]
    
fieldnames=list(pracblocks[0][0].keys())
with open('pracs.csv', 'w',newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(len(pracblocks)):
        for j in range(len(blocks[0])):
            writer.writerow(pracblocks[i][j])




# %% Function to make Psi Staircases
def makePsi(nTrials=32):
# Image visibility ranges between 2 and 40, logarithmically, 40 possibilities.
    staircase = PsiMarginal.Psi(stimRange=np.geomspace(2,40,40,endpoint=True),
            Pfunction='Weibull', nTrials=nTrials,
            threshold=np.geomspace(2,25,40, endpoint=True), thresholdPrior=('gamma',3,35),
            slope=5, slopePrior=('gamma',4,4), # with these values, the contrast starts at ~15 and can end up at ~2 in 32 trials.
            guessRate=0.5, 
            lapseRate=0.05, lapsePrior=('beta',0.05,0.1), marginalize=False)
    return staircase
# nTrials is trials PER staircase sigma is slope

# congup=makePsi()
# print(congup.xCurrent)
# for i in range(32):
#       congup.addData(1)
#       if i % 8 == 0:
#           core.wait(1)
#           print(congup.xCurrent)
        

congup=makePsi()
incup=makePsi()
isoup=makePsi()
conginv=makePsi()
incinv=makePsi()
isoinv=makePsi()

congup2=makePsi()
incup2=makePsi()
isoup2=makePsi()
conginv2=makePsi()
incinv2=makePsi()
isoinv2=makePsi()


# %% Occlude function
def occlude(image, percentage, thickness=10):
    # we take the contrast and luminance of the eye region, excluding the background
    #eyecontrast = np.std(image[60:540,140:300], ddof=1)
    eyeluminance=np.average(image[60:540, 157:337])
    # we create an Alpha channel array for the image, fill it with 255s
    srcImg=image
    srcHeight, srcWidth = srcImg.shape[:]
    srcA = np.full([srcHeight,srcWidth], 255)
    # we initiate the occluder, as an image with same size as the source image,
    # fill it with zeros
    # and make an alpha channel for it.
    occImg = np.zeros([srcHeight, srcWidth])
    occA = np.full([srcHeight, srcWidth], 255)
    # alpha at its highest is 255, so we initiate another variable for that 
    # for easier operations later.
    fullAlpha=255
    # we reduce the Alpha transparency of the range of pixels that occluder 
    # will overlap
    srcA[157:337, :] = fullAlpha -((100-percentage)/100*fullAlpha)
    # we equalize occluder luminance to the eye luminance
    occImg[157:337, :] = eyeluminance
    # adjusting occluder alpha
    occA[157:337, :]=(100-percentage)/100*fullAlpha
    #we blend them, merge into a single image
    blend=(srcImg*(srcA/255))+(occImg*(occA/255))
    occ_color=142
    blend[157:157+thickness,:]=occ_color
    blend[337:337+thickness,:]=occ_color
    blend[157:337+thickness,0:thickness]=occ_color
    blend[157:337+thickness,600-thickness:600]=occ_color
    return blend


# %% Final arrangements before showing things
# drawing bitmaps for image 1, image 2, and mask
bitmap1 = visual.ImageStim(win, size=[7.05,8.38], interpolate=True) 
bitmap2 = visual.ImageStim(win, size=[7.05,8.38], interpolate=True) 
bitmap_mask = visual.ImageStim(win, size=[7.05,8.38], interpolate=True)
# setting clocks for reaction time collection
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

# for practice
if not os.path.isdir(dataPath):
    os.makedirs(dataPath)
pracfieldnames=list(pracblocks[0][0].keys())
prac_fname = 'prac_' +  exp_info['participant'] + '_' + exp_info['age'] + '_' + exp_info['gender'][0] + '_' + exp_info['date'] + '.csv'
prac_fname = os.path.join(dataPath, prac_fname)
f2 = open(prac_fname,'w',encoding='UTF8', newline='')
pracwriter=csv.DictWriter(f2, fieldnames=pracfieldnames)
pracwriter.writeheader()


# function that draws a break between blocks, shows which block they are at,
# and takes as arguments block no, the break time between each block, and a
# long break at every 6th block.
# %% Block break
def block_break(block_no, totalblocks, mod, timershort, timerlong):
    timer=timershort
    # timer=1
    blocktext = visual.TextStim(
                    win=win,
                    height=.65,
                    font="Palatino Linotype",
                    alignHoriz='center',
                    color = [color_text,color_text,color_text]
                    )   
    timertext = visual.TextStim(win=win,
            height=.65, 
            pos=[0,-5],
            font="Palatino Linotype",
            alignHoriz = 'center',
            color = [color_text,color_text,color_text])
    if block_no % mod == 0:
        timer=timerlong
        # timer=0
    blocktext.text= instruction_dictionary['blocktext1.text'] + str(timer) + instruction_dictionary['blocktext2.text'] + str(block_no) + """/""" + str(totalblocks)
    for time in range(timer):
        timer-=1
        blocktext.draw()
        timertext.text=""":""" + str(timer)
        timertext.draw()
        core.wait(1)
        win.flip()
        if timer == 0:
            timertext.text= instruction_dictionary['timertext.text']
            blocktext.draw()
            timertext.draw()
            win.flip()
    keys = event.waitKeys(keyList=['space','escape'])
    if 'escape' in keys:
        win.close()
        f.close()
    win.flip()
    core.wait(2)
    

# %% Instruction Screens

# First instruction screen
color_text = float(exp_info['color_text'])
instructions = visual.TextStim(win=win,
    pos=[0,0],
    wrapWidth=60, height=.65, font="Palatino Linotype", alignHoriz='center', color = [color_text,color_text,color_text])

instructions.text = instruction_dictionary['instructions1.text']
instructions.draw()
win.flip() 

keys = event.waitKeys(keyList=['space','escape'])
win.flip() 
# Second instruction screen ==================================================================================

instructions.text = instruction_dictionary['instructions2.text']
instructions.draw()

win.flip()

keys = event.waitKeys(keyList=['space','escape'])
win.flip()
 
# Third instruction screen =================================================================================
instructions.text= instruction_dictionary['instructions3.text']
instructions.pos=[0,0]
instructions.draw()


fixation.draw()
win.flip()
keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
win.flip()

# Fourth instruction screen

instructions.text= instruction_dictionary['instructions4.text']
instructions.pos=[0,0]
instructions.draw()  
fixation.draw()
win.flip()
keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
win.flip()

instructions.text= instruction_dictionary['instructions5.text']
instructions.pos=[0,0]
instructions.draw()  
fixation.draw()
win.flip()
keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
win.flip()



# %% Trial Sequence
#here we define a function for the trialsequence. manipulating this will
# change things in both practice and experiment the same way.


# the aperture for the isolated condition, so the mask only covers that area


aperture = visual.Aperture(
     win=win, name='aperture',
     units='deg', size=(7,2.25), pos=(0,0),
     shape='square')

def trialsequence(path, maskpath, im1name,im2name, maskname, visibility, ori, reduce):
    # we load the array reduce the brightness by a given value in "reduce" as input
    im1=np.array(Image.open(os.path.join(path,im1name)))
    im2=np.array(Image.open(os.path.join(path,im2name)))
    im1= im1.astype(np.int16)-reduce
    im2= im2.astype(np.int16)-reduce
    
    mask=(np.array(Image.open(os.path.join(maskpath,maskname))))/256
    mask=mask.astype(np.int16)-reduce
    
    im1us=occlude(im1,visibility)
    im1=(im1us-127.5)/127.5
    im2us=occlude(im2,visibility)
    im2=(im2us-127.5)/127.5
    mask_occluded=occlude(mask, visibility)
    maskfinal=(mask_occluded-127.5)/127.5

    bitmap1.setOri(ori)
    bitmap2.setOri(ori)
    bitmap_mask.setOri(ori)

    if ori == 180:
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
    if 'eyes' in im1name:
        aperture.enable()
        bitmap_mask.setImage(maskfinal)
    else:
        aperture.disable()
        bitmap_mask.setImage(maskfinal)
    # image[60:540, 157:337]
    for nFrames in range(FixFrame): # 500 ms.
        fixation.draw()
        win.flip()
            
    for nFrames in range(IntFrame):  # 500 ms
        win.flip()
    
    for nFrames in range(ImFrame): # 500 ms
        bitmap1.draw()
        win.flip()
                
    for nFrames in range(MaskFrame): # 200 ms
        bitmap_mask.draw() 
        win.flip()
           
           
    bitmap2.draw()
    win.flip()
    aperture.disable()
    change_clock.reset()
    rt_clock.reset()
    keys = event.waitKeys(keyList=['s','l','escape','p'])     
    
    if keys:
        rt = rt_clock.getTime()
        # fixation.clearTextures()
        
    bitmap1.clearTextures()
    bitmap2.clearTextures()
    win.flip()

    if not keys:
        keys = event.waitKeys(keyList=['s','l','escape','p'])
        rt = rt_clock.getTime()
     
    return keys, rt
# %% Practice

acc_perc=0
tot_prac_blocks=int(exp_info['prac_length'])
#tot_prac_blocks=1
i=0
block_no=-1
pracDone=0
totAcc=0

practice=pracblocks[0:tot_prac_blocks]
for pracblock in practice:
    block_no +=1
    if block_no >0:
        if block_no == int(tot_prac_blocks/2): 
            instructions.text= 'Your accuracy from this block is : '+ str(round(acc_perc*100,2)) + '%' 
            instructions.pos = [0,5]
            instructions.draw()
            instructions.text= instruction_dictionary['prac1.text']
            instructions.pos=[0,-3]
            instructions.draw()
            fixcross.draw()
            win.flip()
            keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
            block_break(block_no,tot_prac_blocks,int(tot_prac_blocks/2), 7,20)
        elif block_no == tot_prac_blocks:
            block_break(block_no,tot_prac_blocks,int(tot_prac_blocks/2), 7,20)
            instructions.text= 'Your total accuracy is : '+ str(round(acc_perc*100,2)) + '%' 
            instructions.pos = [0,7]
            instructions.draw()
            instructions.text= instruction_dictionary['prac2.text']
            instructions.pos=[0,0]
            instructions.draw()
            fixcross.draw()
            win.flip()
            keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
            pracDone=1
            break
        else:
            block_break(block_no,tot_prac_blocks,int(tot_prac_blocks/2),7,20)


    for practrial in pracblock:
        if practrial['ori']=='up':
            ori=180
        else:
            ori=0

        visibility = 24
        # the first half is easy, second is harder
        if block_no > 3:
            visibility= 12
        
        keys, rt = trialsequence(pracPath,pracmaskPath, practrial['im1name'], practrial['im2name'], practrial['mask'], visibility, ori, reduce)
                          
        acc = 0
        
        if keys:
            if 'escape' in keys:
                f2.close()
                win.close()
                win.mouseVisible=True
                break
            elif 's' in keys and (practrial['cond'] == 'ss' or
                    practrial['cond'] == 'ds' or practrial['cond'] == 'isos'): # is same
                acc = 1
            elif 'l' in keys and (practrial['cond'] == 'sd' or
                    practrial['cond'] == 'dd' or practrial['cond'] == 'isod'): # is different
                acc = 1         
            elif 'p' in keys:
                pracDone=1
                f2.close()
                win.flip()
                break
        # if 'p' key is pressed, it skips the practice round
            
        i+=1
        totAcc+=acc
        practrial['acc']=acc
        practrial['contrast']=visibility
        practrial['rt']=rt
        acc_perc=(totAcc+acc)/i
        pracwriter.writerow(practrial)
    if pracDone==1:
        f2.close()
        break
f2.close()

instructions.text = instruction_dictionary['pracfinal.text']
instructions.pos=[0,0]
instructions.draw()
win.flip()
keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
win.flip()

# %% Trial loop
i=0
block_no = -1
ctr_congup1, ctr_congup2, ctr_conginv1, ctr_conginv2, ctr_incup1, ctr_incup2, ctr_incinv1, ctr_incinv2, ctr_isoup1, ctr_isoup2, ctr_isoinv1, ctr_isoinv2 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

for block in blocks:
    block_no += 1
    block_break(block_no,len(blocks),4,7,20)
    for trial in block:
        if trial['ori']=='up':
            ori=180
            if trial['cond'][0] == 'ss' or trial['cond'][0] == 'dd':
                while congup.xCurrent == None or congup2.xCurrent == None:
                    pass # hang in this loop until the psi calculation has finished
                if trial['staircase']==1:
                    ctr_congup1+=1
                    visibility = congup.xCurrent
                    if ctr_congup1 % 8 == 0:
                        visibility = visibility+10
                else:
                    ctr_congup2+=1
                    visibility = congup2.xCurrent
                    if ctr_congup2 % 8 == 0:
                        visibility = visibility+10
            elif trial['cond'][0] == 'ds' or trial['cond'][0] == 'sd':
                while incup.xCurrent == None or incup2.xCurrent == None:
                    pass
                if trial['staircase']==1:
                    ctr_incup1+=1
                    visibility = incup.xCurrent
                    if ctr_incup1 % 8 == 0:
                        visibility = visibility+10
                else:
                    ctr_incup2+=1
                    visibility = incup2.xCurrent
                    if ctr_incup2 % 8 == 0:
                        visibility = visibility+10
            elif trial['cond'][0] == 'i':
                while isoup.xCurrent == None or isoup2.xCurrent == None:
                    pass
                if trial['staircase']==1:
                    ctr_isoup1+=1
                    visibility = isoup.xCurrent
                    if ctr_isoup1 % 8 == 0:
                        visibility = visibility+10
                else:
                    ctr_isoup2+=1
                    visibility = isoup2.xCurrent
                    if ctr_isoup2 % 8 == 0:
                        visibility = visibility+10
        else:
            ori=0
            if trial['cond'][0] == 'ss' or trial['cond'][0] == 'dd':
                while conginv.xCurrent == None or conginv2.xCurrent == None:
                    pass # hang in this loop until the psi calculation has finished
                if trial['staircase']==1:
                    ctr_conginv1+=1
                    visibility = conginv.xCurrent
                    if ctr_conginv1 % 8 == 0:
                        visibility = visibility+10
                else:
                    ctr_conginv2+=1
                    visibility = conginv2.xCurrent
                    if ctr_conginv2 % 8 == 0:
                        visibility = visibility+10
            elif trial['cond'][0] == 'ds' or trial['cond'][0] == 'sd':
                while incinv.xCurrent == None or incinv2.xCurrent == None:
                    pass
                if trial['staircase']==1:
                    ctr_incinv1+=1
                    visibility = incinv.xCurrent
                    if ctr_incinv1 % 8 == 0:
                        visibility = visibility+10
                else:
                    ctr_incinv2+=1
                    visibility = incinv2.xCurrent
                    if ctr_incinv2 % 8 == 0:
                        visibility = visibility+10
            elif trial['cond'][0] == 'i':
                while isoinv.xCurrent == None or isoinv2.xCurrent == None:
                    pass
                if trial['staircase']==1:
                    ctr_isoinv1+=1
                    visibility = isoinv.xCurrent
                    if ctr_isoinv1 % 8 == 0:
                        visibility = visibility+10
                else:
                    ctr_isoinv2+=1
                    visibility = isoinv2.xCurrent
                    if ctr_isoinv2 % 8 == 0:
                        visibility = visibility+10
            

        keys, rt = trialsequence(stimPath,maskPath, trial['im1name'], trial['im2name'], trial['mask'], visibility, ori, reduce)
        acc = 0
        if keys:
            if 'escape' in keys:
                f.close()
                win.close()
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
        i+=1


        if ori==180:
            if trial['cond'][0] == 'ss' or trial['cond'][0] == 'dd':
                if trial['staircase'] == 1:
                    if ctr_congup1 % 8 != 0:
                        congup.addData(acc)
                else:
                    if ctr_congup2 % 8 != 0:
                        congup2.addData(acc)
            elif trial['cond'][0] == 'ds' or trial['cond'][0] == 'sd':
                if trial['staircase'] == 1:
                    if ctr_incup1 % 8 != 0:
                        incup.addData(acc)
                else:
                    if ctr_incup2 % 8 != 0:
                        incup2.addData(acc)
            elif trial['cond'][0] == 'i':
                if trial['staircase'] ==1:
                    if ctr_isoup1 % 8 != 0:
                        isoup.addData(acc)
                else:
                    if ctr_isoup2 % 8 != 0:
                        isoup2.addData(acc)
        else:
            if trial['cond'][0] == 'ss' or trial['cond'][0] == 'dd':
                if trial['staircase']==1:
                    if ctr_conginv1 % 8 != 0:
                        conginv.addData(acc)
                else:
                    if ctr_conginv2 % 8 != 0:
                        conginv2.addData(acc)
            elif trial['cond'][0] == 'ds' or trial['cond'][0] == 'sd':
                if trial['staircase']==1:
                    if ctr_incinv1 % 8 != 0:
                        incinv.addData(acc)
                else:
                    if ctr_incinv2 % 8 != 0:
                        incinv2.addData(acc)
            elif trial['cond'][0] == 'i':
                if trial['staircase']==1:
                    if ctr_isoinv1 % 8 != 0:
                        isoinv.addData(acc)
                else:
                    if ctr_isoinv2 % 8 !=0:
                        isoinv2.addData(acc)

        writer.writerow(trial)
        # shuffle inter-trial intervals and choose one at random to wait.
        rnd.shuffle(ITI)
        #core.wait(ITI[1])
        
f2.close()
f.close()
win.close()
win.mouseVisible=True


