import unittest
from psychopy import visual
from multi_target.Experiment import Experiment
from multi_target.Instructions import Instructions
from multi_target.Design import Design
from multi_target.Canvas import Canvas

disp = visual.Window(color=(-1, -1, -1), fullscr=False)
canvas = Canvas(disp)

experiment = Experiment(canvas, Design(
    "items/stimuli.csv", 2, 2), 1, 1)

class Test_Instructions(unittest.TestCase):
  
    def test_string(self):
        self.assertTrue(isinstance(
            experiment.instructions.block_instructions('multi')[0],
            basestring
        ))   
#todo: test whether PM items turn up where expected
    def test_pm_insert(self):
        for i in experiment.design.data:
            self.assertEqual(experiment.design.pm_positions[i].tolist(),
            experiment.design.data[i].index[experiment.design.data[i]['S'] == 'P'].tolist())

