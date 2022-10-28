# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 14:41:32 2022

@author: canoluk
"""


# %% Package imports
import os
import numpy as np
import numpy.random as rnd
from psychopy import visual, event, core, gui, data, monitors
from PIL import Image
import PsiMarginal
import csv
import translators as ts


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
        'screenwidth(cm)': '49',
        'screenresolutionhori(pixels)': '1920',
        'screenresolutionvert(pixels)': '1200',
        'refreshrate(hz)': '120'}

dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)
    

# If 'Cancel' is pressed, quit
if dlg.OK == False:
    core.quit()
        
# Get date and time
exp_info['date'] = data.getDateStr()
exp_info['exp_name'] = exp_name
  
#%% Creation of a dictonary with all the instruction
instruction_dictionary = {'instructions.text' : "Dans cette étude, vous allez voir deux visages (ou paire d'yeux) présentés l'un à la suite de l'autre. \n\nVotre tâche est d'indiquer si la région oculaire (yeux et sourcils) des visages présentés est identique ou différente.",
                          'instructions2a.text': "Si la région oculaire est IDENTIQUE,\n appuyez sur 'S'.",
                          'instructions2b.text': "Si la région oculaire est DIFFÉRENTE,\n appuyez sur 'L'.", 
                          'instructions2c.text': "Appuyez sur la barre 'ESPACE' pour continuer",
                          'instructions3.text': "Bravo!\nVous avez terminé l'entrainement.\nVous allez maintenant commencer l'étude.\n\nAppuyez sur la barre 'ESPACE' pour commencer l'étude",
                          'instructions4.text': "Vous pouvez maintenant placer vos mains sur les touches 'S' et 'L' du clavier.",
                          'instructions5.text': "Veuillez garder votre regard fixé au centre durant toute l'expérience.",
                          'instructions6.text': "Appuyez sur la barre 'ESPACE' pour commencer l'entraînement.",
                          'instructions7a.text': "Il sera difficile de remarquer des changements au niveau de la région oculaire indépendament du reste du visage. \n\nPar conséquent, nous vous demandons de concentrer votre attention uniquement au niveau de la région oculaire (yeux et sourcils).",
                          'instructions7b.text': "Si vous avez des questions par rapport aux consignes, sentez-vous libre de les poser.",
                          'timertext.text':"Prêt",
                          'blocktext1.text': "Veuillez faire une courte pause avant le prochain bloc. \nVous pouvez appuyer sur la barre 'ESPACE' pour continuer après ",
                          'blocktext2.text':" secondes lorsque vous serez prêt. \n Bloc:"}

#%% Creation of a function to translate the instructions
def intoenglish(input_dictionary,language): 
    instruction_dictionary_english={} 
    for k,phrase in input_dictionary.items():
       translater = ts.google(phrase, from_language='fr', to_language=language)
       instruction_dictionary_english[k] = translater
    return instruction_dictionary_english

#Now we translate the instruction if required
if exp_info['language']!='fr':
    language = exp_info['language']
    instruction_dictionary=intoenglish(instruction_dictionary, language) 
# %% Monitor setup 
mon = monitors.Monitor('Vpixx040821') #Pulls out photometer calibration settings by name.  
mon.setWidth(float(exp_info['screenwidth(cm)'])) # Cm width
mon.setDistance(57)
horipix = exp_info['screenresolutionhori(pixels)']
vertpix = exp_info['screenresolutionvert(pixels)']
framerate = exp_info['refreshrate(hz)']
scrsize = (float(horipix),float(vertpix))
framelength = 1000/(float(framerate))
mon.setSizePix(scrsize)

# how many rgb values do we lower the brightness
reduce=50

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
# Fixation, Interval, Target, Mask times in terms of # of frames
FixFrame, IntFrame, ImFrame, MaskFrame = int(FixT/framelength), int(IntT/framelength), int(TargetT/framelength), int(MaskT/framelength)


# %% Fixation
fixation = visual.TextStim(
    win=win,
    pos=[0,.75],
    wrapWidth=None,
    height=1,
    font="Palatino Linotype",
    alignHoriz='center',
    alignVert='center',
    color= "black",
    bold=True
    )
fixation.text = """
+"""

# visual.ShapeStim(win, 
#     vertices=((0, -0.3), (0, 0.3), (0,0), (-0.3,0), (0.3, 0)),
#     lineWidth=3,
#     closeShape=False,
#     lineColor="black"
#     )


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
# [same up * 8, diff up*8, iso up * 8, same inv * 8, diff inv * 8, iso inv * 8]
# and we need to make big blocks (a block made of 6 miniblocks) with each 
# condition once in it.



blocks2=[]
bigblock=[]
for bigs in range(n_bigblocks):
    for block in range(0,len(blocks),n_bigblocks):
        bigblock.append(blocks[block+bigs])
    rnd.shuffle(bigblock)
    blocks2.append(bigblock)
    bigblock=[]
    

final_blocks=[]
for i in range(len(blocks2)):
    for j in range(len(blocks2[i])):
        final_blocks.append(blocks2[i][j])

sc=[np.zeros(8),np.ones(8)]
sc2=[]
for i in sc:
    for j in i:
        if j == 0:
            j=2
        sc2.append(int(j))

# adding staircases to each block, 8 trials use staircase 1, the rest 8 use 2
for i in final_blocks:
    rnd.shuffle(sc2)
    for j,t in zip(i,sc2):
        j['staircase']=t



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


miniblock_length=12
pracblocks=[]
asd=[]
tempblock=[]
for ori in ['up','inv']:
    for cond in ['s','d','iso']:
        for ctr in range(0,len(pracs_new['ssup']),int(miniblock_length/2)):
            for i in range(int(miniblock_length/2)):
                tempblock.append(pracs_new[f"{cond}s{ori}"][ctr+i])
                tempblock.append(pracs_new[f"{cond}d{ori}"][ctr+i])
            rnd.shuffle(tempblock)
            pracblocks.append(tempblock)
            tempblock=[]
# pracblocks has 24 blocks, first 12 up, second 12 inv
# out of the 12, first 4 "same", next 4 "diff", next 4 "iso" 


# here we create 4 big prac blocks. we'll only use 2 of those to keep it short
pracblocks2=[]
n_bigblocks=int(len(pracblocks)/6) # 6 is the # of conditions(same-up, diff-inv,etc.)
bigblock=[]
for bigs in range(n_bigblocks):
    for block in range(0,len(pracblocks),4):
        bigblock.append(pracblocks[block+bigs])
    rnd.shuffle(bigblock)
    pracblocks2.append(bigblock)
    bigblock=[]
    

# here we 'unfold' the big blocks so it's easier to index. 
final_prac_blocks=[]
for i in range(len(pracblocks2)):
    for j in range(len(pracblocks2[i])):
        final_prac_blocks.append(pracblocks2[i][j])



# With the practice, we don't bother too much with the equalization of
# everything. This is where practice trials are ready already.
# also, we don't use a staircase for practice, their visibility is pre-defined.






# %% Shortcut to make Psi Staircases
def makePsi(nTrials=64, start_thresh=1.5):
# Image visibility ranges between 2 and 40, logarithmically, 40 possibilities.
    staircase = PsiMarginal.Psi(stimRange=np.geomspace(start_thresh,40,40,endpoint=True),
            Pfunction='Weibull', nTrials=nTrials,
            threshold=np.geomspace(start_thresh,40,40, endpoint=True), 
            thresholdPrior=('normal',5,5), slope=np.geomspace(0.5, 20, 50, endpoint=True),
            guessRate=0.5, slopePrior=('gamma',3,6),lapseRate=0.05, lapsePrior=('beta',2,20), marginalize=True)
    return staircase
# nTrials is trials PER staircase sigma is slope


sameup=makePsi()
diffup=makePsi()
isoup=makePsi()
sameinv=makePsi()
diffinv=makePsi()
isoinv=makePsi()

sameup2=makePsi()
diffup2=makePsi()
isoup2=makePsi()
sameinv2=makePsi()
diffinv2=makePsi()
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
    blend[157:157+thickness,:]=90
    blend[337:337+thickness,:]=90
    blend[157:337+thickness,0:thickness]=90
    blend[157:337+thickness,600-thickness:600]=90
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

# function that draws a break between blocks, shows which block they are at,
# and takes as arguments block no, the break time between each block, and a
# long break at every 6th block.

def block_break(block_no, totalblocks, timershort, timerlong):
    timer=timershort
    # timer=1
    blocktext = visual.TextStim(
                    win=win,
                    height=.65,
                    font="Palatino Linotype",
                    alignHoriz='center',
                    color = [-.9,-.9, -.9]
                    )   
    timertext = visual.TextStim(win=win,
            height=.65, 
            pos=[0,-5],
            font="Palatino Linotype",
            alignHoriz = 'center',
            color = [-.9,-.9, -.9])
    if block_no % 6 == 0:
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
    

#%% We draw the text explaining what we will show
instructions = visual.TextStim(win=win,
    pos=[0,7],
    wrapWidth=None, height=.65, font="Palatino Linotype", alignHoriz='center', color = [-.9,-.9,-.9])

instructions.text = instruction_dictionary['instructions.text']
instructions.draw()


instructions.text = instruction_dictionary['instructions7a.text']
instructions.pos = [0,-2]
instructions.draw()



instructions=instructions
instructions.pos=[0,-11]

instructions.text = instruction_dictionary['instructions2c.text']
instructions.draw()


win.flip() 

keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)

# We add another instruction screen ==================================================================================

## We add some examples ======================================================================================= 
# We begin by creating the bitmaps to modify the frame
bitmap_im1 = np.array(Image.open(os.path.join('exp_imgs','2-8.png')))
bitmap_im1 = bitmap_im1.astype(np.int16)-reduce
bitmap_im1 = occlude(bitmap_im1, 50)
bitmap_im1 = (bitmap_im1-127.5)/127.5

bitmap_im2 = np.array(Image.open(os.path.join('exp_imgs','2-93.png')))
bitmap_im2 = bitmap_im2.astype(np.int16)-reduce
bitmap_im2 = occlude(bitmap_im2, 50)
bitmap_im2 = (bitmap_im2-127.5)/127.5

bitmap_im3 = np.array(Image.open(os.path.join('exp_imgs','46-8.png')))
bitmap_im3 = bitmap_im3.astype(np.int16)-reduce
bitmap_im3 = occlude(bitmap_im3, 50)
bitmap_im3 = (bitmap_im3-127.5)/127.5

bitmap_eye1 = np.array(Image.open(os.path.join('exp_imgs','8_eyes.png')))
bitmap_eye1 = bitmap_eye1.astype(np.int16)-reduce
bitmap_eye1 = occlude(bitmap_eye1, 50)
bitmap_eye1 = (bitmap_eye1-127.5)/127.5

bitmap_eye2 = np.array(Image.open(os.path.join('exp_imgs','93_eyes.png')))
bitmap_eye2 = bitmap_eye2.astype(np.int16)-reduce
bitmap_eye2 = occlude(bitmap_eye2, 50)
bitmap_eye2 = (bitmap_eye2-127.5)/127.5

# Now we create pictures to put the bitmaps on
# Same condition
image_stim1 = visual.ImageStim(win, image = bitmap_im1, pos = [-11, 1.5], size = 4)
image_stim1.setOri(180)
image_stim1.draw()
image_stim2 = visual.ImageStim(win, image = bitmap_im1, pos = [-7, 1.5], size = 4)
image_stim2.setOri(180)
image_stim2.draw()
image_stim3 = visual.ImageStim(win, image = bitmap_im2, pos = [11, 1.5], size = 4)
image_stim3.setOri(180)
image_stim3.draw()
image_stim4 = visual.ImageStim(win, image = bitmap_im1, pos = [7, 1.5], size = 4)
image_stim4.setOri(180)
image_stim4.draw()

# Different context condition
image_stim1 = visual.ImageStim(win, image = bitmap_im1, pos = [-11, -2.5], size = 4)
image_stim1.setOri(180)
image_stim1.draw()
image_stim2 = visual.ImageStim(win, image = bitmap_im3, pos = [-7, -2.5], size = 4)
image_stim2.setOri(180)
image_stim2.draw()
image_stim2 = visual.ImageStim(win, image = bitmap_im3, pos = [7, -2.5], size = 4)
image_stim2.setOri(180)
image_stim2.draw()
image_stim3 = visual.ImageStim(win, image = bitmap_im2, pos = [11, -2.5], size = 4)
image_stim3.setOri(180)
image_stim3.draw()

# Isolated condition
image_eye1 = visual.ImageStim(win, image = bitmap_eye1, pos = [-11, -6.5], size = 4)
image_eye1.setOri(180)
image_eye1.draw()
image_eye1 = visual.ImageStim(win, image = bitmap_eye1, pos = [-7, -6.5], size = 4)
image_eye1.setOri(180)
image_eye1.draw()
image_eye1 = visual.ImageStim(win, image = bitmap_eye1, pos = [7, -6.5], size = 4)
image_eye1.setOri(180)
image_eye1.draw()
image_eye2 = visual.ImageStim(win, image = bitmap_eye2, pos = [11, -6.5], size = 4)
image_eye2.setOri(180)
image_eye2.draw()

instructions2 = visual.TextStim(win=win,
    pos=[-9,5], 
    wrapWidth=None, height=.65, font="Palatino Linotype", alignHoriz='center', color = [-.9,-.9,-.9])
instructions2.text = instruction_dictionary['instructions2a.text']
instructions2.draw()

instructions2 = visual.TextStim(win=win,
    pos=[9,5], 
    wrapWidth=None, height=.65, font="Palatino Linotype", alignHoriz='center', color = [-.9,-.9,-.9])
instructions2.text = instruction_dictionary['instructions2b.text']
instructions2.draw()

instructions.text = instruction_dictionary['instructions7b.text']
instructions.pos = [0,-9]
instructions.draw()

instructions2.text = instruction_dictionary['instructions2c.text']
instructions2.pos = [0,-11]
instructions2.draw()



win.flip()

keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
 
# We add the last instruction screen =================================================================================
instructions2.text= instruction_dictionary['instructions4.text']
instructions2.pos=[0,-5]
instructions2.draw()


instructions2.text= instruction_dictionary['instructions5.text']
instructions2.pos=[0,5]
instructions2.draw()  


instructions2.text= instruction_dictionary['instructions6.text']
instructions2.pos=[0,-11]
instructions2.draw()

fixcross = visual.TextStim(win=win,
    pos=[0,.75], wrapWidth=None, height=1, font="Palatino Linotype", alignHoriz='center', alignVert='center',
    color= "black",bold=True)

fixcross.text = """
+"""
fixcross.draw()

win.flip()
keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)

#%% here we define a function for the trialsequence. manipulating this will
# change things in both practice and experiment the same way.

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
    bitmap_mask.setImage(maskfinal)

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

#%%
# we start with the practice



acc_perc=0
tot_mini_blocks=12
i=0
block_no=0
pracDone=0
totAcc=0
for pracblock in final_prac_blocks:
    block_no +=1
    if block_no >1:
        if block_no == 6 or block_no == 12:
            instructions.text= 'Votre précision est:'+ str(round(acc_perc*100,2)) + '%' 
            instructions.draw()
            win.flip()
            keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
            block_break(block_no,tot_mini_blocks,7,20)
        else:
            block_break(block_no,tot_mini_blocks,7,20)
    if block_no == 12:
        break

    for practrial in pracblock:
        if practrial['ori']=='up':
            ori=180
        else:
            ori=0

        visibility = 15
        # the first big block is easy, second is harder
        if block_no > 5:
            visibility= 6
        
        keys, rt = trialsequence(pracPath,pracmaskPath, practrial['im1name'], practrial['im2name'], practrial['mask'], visibility, ori, reduce)
                          
        acc = 0
        if keys:
            if 'escape' in keys:
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
                break
        #        block_no=5
            
        i+=1
        totAcc+=acc
        acc_perc=(totAcc+acc)/i
            
        # if 'p' key is pressed, it skips the practice round
    if pracDone==1:
        break

instructions2.text = instruction_dictionary['instructions3.text']


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
        block_break(block_no,len(final_blocks),7,20)
    for trial in block:
        if trial['ori']=='up':
            ori=180
            if trial['cond'][0] == 's' :
                while sameup.xCurrent == None or sameup2.xCurrent == None:
                    pass # hang in this loop until the psi calculation has finished
                if trial['staircase']==1:
                    visibility = sameup.xCurrent
                else:
                    visibility = sameup2.xCurrent
            elif trial['cond'][0] == 'd':
                while diffup.xCurrent == None or diffup2.xCurrent == None:
                    pass
                if trial['staircase']==1:
                    visibility = diffup.xCurrent
                else:
                    visibility = diffup2.xCurrent
            elif trial['cond'][0] == 'i':
                while isoup.xCurrent == None or isoup2.xCurrent == None:
                    pass
                if trial['staircase']==1:
                    visibility = isoup.xCurrent
                else:
                    visibility = isoup2.xCurrent
        else:
            ori=0
            if trial['cond'][0] == 's':
                while sameinv.xCurrent == None or sameinv2.xCurrent == None:
                    pass # hang in this loop until the psi calculation has finished
                if trial['staircase']==1:
                    visibility = sameinv.xCurrent
                else:
                    visibility = sameinv2.xCurrent
            elif trial['cond'][0] == 'd':
                while diffinv.xCurrent == None or diffinv2.xCurrent == None:
                    pass
                if trial['staircase']==1:
                    visibility = diffinv.xCurrent
                else:
                    visibility = diffinv2.xCurrent
            elif trial['cond'][0] == 'i':
                while isoinv.xCurrent == None or isoinv2.xCurrent == None:
                    pass
                if trial['staircase']==1:
                    visibility = isoinv.xCurrent
                else:
                    visibility = isoinv2.xCurrent
            

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
            if trial['cond'][0] == 's' :
                if trial['staircase'] == 1:
                    sameup.addData(acc)
                else:
                    sameup2.addData(acc)
            elif trial['cond'][0] == 'd':
                if trial['staircase'] == 1:
                    diffup.addData(acc)
                else:
                    diffup2.addData(acc)
            elif trial['cond'][0] == 'i':
                if trial['staircase'] ==1:
                    isoup.addData(acc)
                else:
                    isoup2.addData(acc)
        else:
            if trial['cond'][0] == 's':
                if trial['staircase']==1:
                    sameinv.addData(acc)
                else:
                    sameinv2.addData(acc)
            elif trial['cond'][0] == 'd':
                if trial['staircase']==1:
                    diffinv.addData(acc)
                else:
                    diffinv2.addData(acc)
            elif trial['cond'][0] == 'i':
                if trial['staircase']==1:
                    isoinv.addData(acc)
                else:
                    isoinv2.addData(acc)

        writer.writerow(trial)
        # shuffle inter-trial intervals and choose one at random to wait.
        rnd.shuffle(ITI)
        core.wait(ITI[1])
        

f.close()
win.close()
win.mouseVisible=True

