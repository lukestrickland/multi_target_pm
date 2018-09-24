from psychopy import visual, core, event
import math
import time
from objects import Canvas, Experiment, Design
import pandas as pd
import numpy as np

# Initialise a new Display instance
disp = visual.Window(color=(-1,-1,-1))
# Initialise a new EyeTracker instancep
# Get the handle to the active Window
canvas = Canvas(disp)
experiment = Experiment(canvas, "a")


design=Design("stimuli.csv", 1, 1, 2,2)
design.set_ldt()
print(design.data)
design.set_pm()
print(design.newdata)
print(len(design.pm_positions))

#print(stim["Words"])
#print(stim.values)

canvas.close_display
