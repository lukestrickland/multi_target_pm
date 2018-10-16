import unittest
from psychopy import visual
from multi_target.Experiment import Experiment
from multi_target.Instructions import Instructions
from multi_target.Design import Design
from multi_target.Canvas import Canvas
from collections import Counter
import matplotlib.pyplot as plt

disp = visual.Window(color=(-1, -1, -1), fullscr=False)
canvas = Canvas(disp)

experiment = Experiment(canvas, Design(
    "items/stimuli.csv", 2, 2), 1, 2)

test_design = Design(
    "items/stimuli.csv", 2, 2)

class Test_Design(unittest.TestCase):
#todo: test whether PM items turn up where expected

    def test_pm_positions(self):
        old= []
        for i in range(1,100):
            test_design.set_pm_positions(5)
            all_positions = [test_design.pm_positions.iloc[:,j].values.flatten() for j in range(0,4)]
            all_flattened = [item for sublist in all_positions for item in sublist]
            old = old + all_flattened
        plt.hist(old, bins=1000)
 
    def test_pm_insert(self):
        for i in experiment.design.data:
            self.assertEqual(experiment.design.pm_positions[i].tolist(),
            experiment.design.data[i].index[experiment.design.data[i]['S'] == 'P'].tolist())
#simulate participants and check that all combinations of response key list 
#and condition orders are equal
    def test_sim_design(self):
        response_keys = []
        counterbalance = []
        for i in range(0,32):
            experiment= Experiment(canvas, Design("items/stimuli.csv", 2, 2), 1, i)
            response_keys.append(experiment.responsekeys)
            counterbalance.append(experiment.counterbalance)
        cb = zip(response_keys, counterbalance)   
        cb_dict = Counter(str(e) for e in cb)
        counts = [cb_dict[c] for c in cb_dict]
        self.assertEqual(len(set(counts)), 1)    



#test that PM positions seem genuinely random - how to test this? maybe just pop up a graph            
#test counterbalance: 


#check block run order

#Check stimuli - no repeating ongoing task stimuli
#repeating PM stimuli, correct number of times?


