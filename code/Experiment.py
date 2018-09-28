from psychopy import visual, core, event
import numpy as np
import pandas as pd
import csv

ldt_instructions = "In the next block of trials, you will again perform \n\n"

class Experiment():
    def __init__(self, canvas, design, day, participantid):

        self.canvas = canvas
        self.design = design
        self.bal = participantid % 2 
        self.counterbalance = [np.array([["single", "multi"], ["multi", "single"]]),
        np.array([["multi", "single"], ["single", "multi"]])][self.bal]
        self.day = day
        self.blocknum = 1
        if day ==1:
            self.design.set_stim(self.counterbalance)
            self.design.set_pm_positions()
            self.design.create_blocks()
            self.design.insert_pm(self.counterbalance)
            self.design.setup_data(participantid, self.counterbalance)
        else:
            self.design.read_data(participantid)

    def trial(self, stim):
        self.canvas.fixcross()
        core.wait(0.5)
        self.canvas.clear()
        self.canvas.show()
        core.wait(0.25)
        pre_stim_resps = event.getKeys()
        self.canvas.text(stim)
        t0 = core.getTime()
        self.canvas.show()
        resp = event.waitKeys(timeStamped=True)
        self.canvas.clear()
        self.canvas.show()
        return resp[0][0], resp[0][1] - t0

    def multi_leadup(self):
        self.canvas.clear()
        self.canvas.text(ldt_instructions+ ' '.join(self.design.multi_cond_words))
        self.canvas.show()
        core.wait(0.25)
        resp = event.waitKeys(timeStamped=True)

    def single_leadup(self):
        self.canvas.clear()
        self.canvas.text(ldt_instructions+ ' '.join(self.design.single_cond_words))
        self.canvas.show()
        core.wait(0.25)
        resp = event.waitKeys(timeStamped=True)        

    def run_block(self, type):
        if (type=='multi'):
            self.multi_leadup()
        else:
            self.single_leadup()
        self.block(self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)].loc[:,'stim'])
        self.blocknum += 1

    def run_both_blocks(self):
        for block in range(0,2):
            self.run_block(self.counterbalance[self.day-1, block])

    def block(self, trials):
        RTs = []
        choices = []
        #len(trials)
        ntrials=5
        for i in range(0,ntrials):           
            RT, choice = self.trial(trials[i])
            RTs.append(RT)
            choices.append(choice)
            core.wait(0.5)
            if event.getKeys(['escape']):
                self.canvas.close_display()
                core.quit()