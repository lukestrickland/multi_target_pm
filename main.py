from psychopy import visual, core, event
import math
import time
from objects import Canvas, Experiment, Design
import pandas as pd
import numpy as np

#participantid = int(raw_input("Please enter participant id: "))
#day = int(raw_input("Please enter session number: "))

day=2
participantid=1

print(day + 3)

# Initialise a new Display instance
disp = visual.Window(color=(-1,-1,-1))
# Initialise a new EyeTracker instancep
# Get the handle to the active Window
canvas = Canvas(disp)
#

experiment = Experiment(canvas, Design("stimuli.csv", 2,2), day, participantid)
print(experiment.counterbalance)
#experiment.block(design.data['day_1_block_1'].loc[:,'stim'])
experiment.run_both_blocks()
#print(stim["Words"])
#print(stim.values)

canvas.close_display
