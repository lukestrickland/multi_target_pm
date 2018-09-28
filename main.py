from psychopy import visual
from multi_target.Canvas import Canvas
from multi_target.Design import Design
from multi_target.Experiment import Experiment


#participantid = int(raw_input("Please enter participant id: "))
#day = int(raw_input("Please enter session number: "))

day=1
participantid=1


# Initialise a new Display instance
disp = visual.Window(color=(-1,-1,-1))
canvas = Canvas(disp)
#

experiment = Experiment(canvas, Design("stimuli.csv", 2,2), day, participantid)
print(experiment.counterbalance)
#experiment.block(design.data['day_1_block_1'].loc[:,'stim'])
experiment.recmem_block("multi")
experiment.run_both_blocks()
#print(stim["Words"])
#print(stim.values)

print(experiment.perf_data)
experiment.save_data()
experiment.canvas.close_display
