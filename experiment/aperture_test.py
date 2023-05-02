# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 16:08:58 2023

@author: canoluk
"""

from psychopy import visual, core, event, monitors

mon = monitors.Monitor('VPixx020523')
win = visual.Window(monitor = mon,
                    size = [600,800],
                    colorSpace = "rgb255",
                    color= [127.5, 127.5, 127.5],
                    units='deg',
                    fullscr=False,
                    allowStencil=True,
                    screen=1)

win.flip()

# break the loop when the user presses a key  
while True:
    if event.getKeys():
        break
win.close()