from psychopy import core, event
import numpy as np
import pandas as pd

ldt_instructions = "In the next block of trials, you will again perform \n\n"

class Experiment():
    def __init__(self, canvas, design, day, participantid):
        self.participantid=participantid
        self.perf_data = {}
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

    def recmem_leadup(self):
        self.canvas.clear()
        self.canvas.text('RECMEM'+ ' '.join(self.design.multi_cond_words))
        self.canvas.show()
        core.wait(0.25)
        resp = event.waitKeys(timeStamped=True)
    
    def single_leadup(self):
        self.canvas.clear()
        self.canvas.text(ldt_instructions+ ' '.join(self.design.single_cond_words))
        self.canvas.show()
        core.wait(0.25)
        resp = event.waitKeys(timeStamped=True)        

    def run_block(self, btype):
        if (btype=='multi'):
            self.multi_leadup()
        else:
            self.single_leadup()
        choices, RTs = self.block(self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)].loc[:,'stim'])
        perf = pd.DataFrame({'RT': RTs, 'R':choices})
        perf['block'] = self.blocknum
        perf['day'] = self.day
        perf['cond'] = btype
        self.perf_data['day_' + str(self.day) + '_block_' + str(self.blocknum)] =   pd.concat([
            self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)], 
        perf], axis=1, sort=False)     
        self.blocknum += 1
        

    def run_both_blocks(self):
        for block in range(0,2):
            self.run_block(self.counterbalance[self.day-1, block])

    def block(self, trials):
        RTs = []
        choices = []
        #len(trials)
        ntrials=2
        for i in range(0,ntrials):           
            choice, RT = self.trial(trials[i])
            RTs.append(RT)
            choices.append(choice)
            core.wait(0.5)
            if event.getKeys(['escape']):
                self.canvas.close_display()
                core.quit()
        return choices, RTs

    def recmem_block(self, btype):
        self.recmem_leadup()
        lures = pd.read_csv('recmem_words.csv', header=None)
        lures = lures[0:8]
        stim = pd.concat([lures, self.design.multi_cond_words])
        choices, RTs = self.block(stim.iloc[:,0])
        perf = pd.DataFrame({'RT': RTs, 'R':choices})
        perf['block'] = self.blocknum
        perf['day'] = self.day
        perf['cond'] = btype
        self.perf_data['RM' + 'day_' + str(self.day) + '_block_' + str(self.blocknum)] =   pd.concat([
            self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)], 
        perf], axis=1, sort=False)     

    def save_data(self):
        for j in range(1, self.design.blocks+1):
            data = self.perf_data["day_" + str(self.day) + "_block_" + str(j)].copy()
            if j==1:
                day_dats= data
            else:
                day_dats = day_dats.append(data, ignore_index=True)
        day_dats.to_csv("data/p" +str(self.participantid)+ "_day_" + str(self.day)+ ".csv")
