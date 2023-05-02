# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 16:08:58 2023

@author: canoluk
"""

from psychopy import visual, core, event

win = visual.Window(size=[1900, 1200], fullscr=False, allowStencil=True)

image = visual.ImageStim(win, image='img.jpg')
aperture = visual.Aperture(
    win=win, name='aperture',
    units='pix', size=(251,61), pos=(0,0), shape='square')
aperture.enable()
image.draw()
win.flip()

# break the loop when the user presses a key
while True:
    if event.getKeys():
        break
win.close()