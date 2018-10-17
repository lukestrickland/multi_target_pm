# This is all to dispatch the experiment.

from psychopy import visual
from multi_target.Canvas import Canvas
from multi_target.Design import Design
from multi_target.Experiment import Experiment

#participantid = int(raw_input("Please enter participant id: "))
#day = int(raw_input("Please enter session number: "))

day=1
participantid=1


# Initialise a new Display instance, experiment, design
disp = visual.Window(color=(-1, -1, -1), fullscr=False)
canvas = Canvas(disp)
experiment = Experiment(canvas, Design(
    "items/stimuli.csv", 2, 2), day, participantid)


experiment.practice_block()
experiment.run_both_blocks()
experiment.save_data()
experiment.canvas.close_display

##random junk syntax I've been using to test
# print(test)
# instruct_delay=0
#block_instructions, recmem_instructions1,recmem_instructions2, response_instructions = experiment.instructions.block_instructions('multi')
#experiment.print_instructions(recmem_instructions1, instruct_delay, 'space', height = 0.085, wrapWidth= 1.65)
#experiment.print_instructions(recmem_instructions2, instruct_delay, 'space', height = 0.085, wrapWidth= 1.65)
# experiment.run_block('multi')


#block_instructions, recmem_instructions, response_instructions = experiment.create_instructions("single")
#experiment.print_instructions(recmem_instructions, 1, 'space', height = 0.085, wrapWidth= 1.65)

#experiment.print_instructions(response_instructions, 1, 'n', height = 0.075, wrapWidth= 1.65)

#
# print(experiment.counterbalance)
# experiment.block(design.data['day_1_block_1'].loc[:,'stim'])

# experiment.practice_block()

# experiment.recmem_block("multi")
#

# print(stim["Words"])
# print(stim.values)

# print(experiment.perf_data)
# experiment.save_data()
