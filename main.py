from psychopy import visual, core
from multi_target.Canvas import Canvas
from multi_target.Design import Design
from multi_target.Experiment import Experiment
from multi_target.launch_experiment import launch


participantid, day = launch()

# Initialise a new Display instance, experiment, design
disp = visual.Window(color=(-1, -1, -1), fullscr=False)
canvas = Canvas(disp)
experiment = Experiment(canvas, Design(
    "items/stimuli.csv", 2, 2), day, participantid)

#Run experiment
experiment.practice_block()
experiment.run_both_blocks()
experiment.save_data()
experiment.print_instructions(("Thank you for completing the session. " 
                                "Please tell the experimenter you are finished."),
                                0, waitkey='space')
experiment.canvas.close_display()
core.quit()