import unittest
import math
import pandas as pd
import itertools
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
    # todo: test whether PM items turn up where expected

    def test_pm_positions(self):
        old = []
        for i in range(1, 100):
            test_design.set_pm_positions(5)
            all_positions = [test_design.pm_positions.iloc[:,
                                                           j].values.flatten() for j in range(0, 4)]
            all_flattened = [
                item for sublist in all_positions for item in sublist]
            old = old + all_flattened
        plt.hist(old, bins=1000)

    def test_pm_insert(self):
        for i in experiment.design.data:
            self.assertEqual(experiment.design.pm_positions[i].tolist(),
                             experiment.design.data[i].index[experiment.design.data[i]['S'] == 'P'].tolist())
# simulate participants and check that all combinations of response key list
# and condition orders are equal

    def test_sim_design(self):
        response_keys = []
        counterbalance = []
        for i in range(0, 32):
            experiment = Experiment(canvas, Design(
                "items/stimuli.csv", 2, 2), 1, i)
            response_keys.append(experiment.responsekeys)
            counterbalance.append(experiment.counterbalance)
        cb = zip(response_keys, counterbalance)
        cb_dict = Counter(str(e) for e in cb)
        counts = [cb_dict[c] for c in cb_dict]
        self.assertEqual(len(set(counts)), 1)

    def test_data_days_consistent(self):
        # read in experiment one data
        matches = []
        for i in range(0, 32):
            experiment1 = Experiment(canvas, Design(
                "items/stimuli.csv", 2, 2), 1, i)
            data_1 = experiment1.design.data.copy()
            del experiment1
            experiment2 = Experiment(canvas, Design(
                "items/stimuli.csv", 2, 2), 2, i)
            data_2 = experiment2.design.data
            match = [pd.DataFrame.equals(data_1[dat1], data_2[dat2]) for
                     dat1, dat2 in zip(data_1, data_2)]
            matches = matches + match
        self.assertTrue(all(matches))

    def test_data_blocks_not_duplicate(self):
        matches = []
        for i in range(0, 32):
            experiment1 = Experiment(canvas, Design(
                "items/stimuli.csv", 2, 2), 1, i)
            data_1 = experiment1.design.data.copy()
            match = [pd.DataFrame.equals(data_1[dat1], data_1[dat2]) for
                     dat1, dat2 in itertools.combinations(data_1, 2)]
            matches = matches + match
        self.assertFalse(any(matches))

    def test_stimuli_duplicates(self):
        all_stim_matching = []
        for i in range(0,32):
            experiment_new = Experiment(canvas, Design(
    "items/stimuli.csv", 2, 2), 1, i)
            data_1 = experiment_new.design.data.copy()
            stacked = pd.concat(data_1)
            counts = Counter(str(e) for e in stacked['stim'])
            # get entire list of PM targets
            ongoing = stacked.loc[stacked["S"] !=
                                'P', "stim"].values.flatten().tolist()
            multis = experiment_new.design.multi_cond_words.values.flatten().tolist()
            singles = experiment_new.design.single_cond_words.values.flatten().tolist()
            pms = multis+singles
            counts_ongoing = {key: counts[key] for key in ongoing}
            counts_singles = {key: counts[key] for key in singles}
            counts_multi = {key: counts[key] for key in multis}
            n_multis = len(experiment_new.design.pm_positions['day_1_block_1'])/8
            n_singles = len(experiment_new.design.pm_positions['day_1_block_1'])
            all_matching = [counts_multi[count] 
                == n_multis for count in counts_multi] + [counts_singles[count]
                                                        == n_singles for count in counts_singles] + [counts_ongoing[count]
                                                                                                    == 1 for count in counts_ongoing]
            all_stim_matching = all_stim_matching + [all(all_matching)]
        self.assertTrue(all(all_stim_matching))
        # check if all ongoing equal to

        # Check stimuli - no repeating ongoing task stimuli
# repeating PM stimuli, correct number of times?


class Test_Experiment(unittest.TestCase):
    # todo: test whether PM items turn up where expected
    def test_RM_newstim(self):
        experiment = Experiment(canvas, Design(
            "items/stimuli.csv", 2, 2), 1, 2)
        initial_len = len(
            pd.read_csv("tmp/p" + str(experiment.participantid) +
                        "recmem_nontargets" + ".csv")) * len(experiment.todays_multi)
        all_nontargets = []
        for i in range(0, initial_len):
            if (i == 0):
                newstim = experiment.recmem_newstim('multi')
            else:
                newstim = newstim.append(experiment.recmem_newstim('multi'))
        self.assertFalse(any(pd.isnull(newstim["Words"])))

    def test_RM_newstim_samenum(self):
        experiment = Experiment(canvas, Design(
            "items/stimuli.csv", 2, 2), 1, 2)
        initial_len = len(
            pd.read_csv("tmp/p" + str(experiment.participantid) +
                        "recmem_nontargets" + ".csv")) * len(experiment.todays_multi)
        all_nontargets = []
        for i in range(0, initial_len):
            newstim = experiment.recmem_newstim('multi')
            nontargets = newstim.loc[newstim['corr'] ==
                                     'n', "Words"].values.flatten().tolist()
            all_nontargets = all_nontargets + nontargets
        stim_dict = Counter(str(e) for e in all_nontargets)
        counts = [stim_dict[c] for c in stim_dict]
        self.assertEqual(len(set(counts)), 1)


# check block run order
