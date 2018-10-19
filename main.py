from psychopy import visual
from multi_target.Canvas import Canvas
from multi_target.Design import Design
from multi_target.Experiment import Experiment
from multi_target.launch_experiment import launch


participantid, day = launch()
break_delay=5

# Initialise a new Display instance, experiment, design
disp = visual.Window(color=(-1, -1, -1), fullscr=False)
canvas = Canvas(disp)
experiment = Experiment(canvas, Design(
    "items/stimuli.csv", 2, 2), day, participantid)

#Run experiment
#experiment.print_instructions("Please take a break for one minute.", break_delay)
#experiment.print_instructions(
#            "Press space to begin the task again.", 0, waitkey="space")
#experiment.practice_block()
experiment.run_both_blocks()
experiment.save_data()
experiment.print_instructions(("Thank you for completing the experiment. " 
                                "Please tell the experimenter you are finished."),
                                0, waitkey='space')
experiment.canvas.close_display
