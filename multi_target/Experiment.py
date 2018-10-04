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
        self.Word_response = 'd'
        self.PM_response = 'j'
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
            recmem_nontargets = pd.read_csv('recmem_nontargets.csv', header=None)
            recmem_nontargets = recmem_nontargets.sample(frac=1)
            recmem_nontargets.reset_index(inplace=True, drop=True)
            recmem_nontargets.to_csv("tmp/p" +str(self.participantid)+ "recmem_nontargets" + ".csv")
        else:
            self.design.read_data(participantid)

        self.todays_multi = self.design.multi_cond_words.to_frame().copy().iloc[
        range((self.day-1)*8,(self.day-1)*8+8), :]
        self.todays_single = self.design.single_cond_words.to_frame().copy().iloc[[self.day-1]]
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

    def create_instructions(self, blocktype):
        if(blocktype=='multi'):
            instruction1 = ("We have an interest in your ability to remember to perform actions in the future. " +
            "In the next block of lexical decision trials, for EIGHT target words we would like you to then press " +
            self.PM_response +" INSTEAD of "+ self.Word_response +". On the next slide, we will present to you the target words to memorize.")

            instruction2 = ("Please remember the following target words \n\n"+
             ' '.join(self.todays_multi.values.flatten()) +
            "\n\n Once you have tried to memorize them, we want to test you." +
            " You will be presented words one by one. Press the 'y' key if the word is on this list, otherwise press the 'n' key. ")

        elif(blocktype=='single'):
            instruction1 =("We have an interest in your ability to remember to perform actions in the future."+
            "In the next block of lexical decision trials, for ONE target word we would like you to then press "+
            self.PM_response,"INSTEAD of", self.Word_response,". On the next slide, we will present to you the target word to memorize.")

            instruction2 = ("Please remember the following:"+
            "Once you are finished memorizing, you will be tested on your recognition of the words." +
            "You will be presented words one by one. Press the 'y' key if the word is on this list, otherwise press the 'n' key. "+
            'The target words are:'
             ' '.join(self.todays_single.values.flatten()) +
             "Please press any key to proceed to your memory test.")
        return instruction1, instruction2
 
    def print_instructions(self, instructions):
        self.canvas.clear()
        self.canvas.text(instructions)
        self.canvas.show()
        core.wait(0.25)
        resp = event.waitKeys(timeStamped=True)       

    def block_leadup(self, blocktype):
        block_instructions, recmem_instructions = self.create_instructions(blocktype)
        self.print_instructions(block_instructions)
        self.print_instructions(recmem_instructions)
        self.recmem_block(blocktype)
        self.canvas.clear()
        self.puzzle()
       

    def run_block(self, btype):
        self.block_leadup(btype)
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
        while True:
            full_nontargets = pd.read_csv("tmp/p" +str(self.participantid)+ 
            "recmem_nontargets" + ".csv")
            nontargets = full_nontargets.copy().iloc[0:8,1].to_frame()
            next_nontargets = full_nontargets.copy().loc[range(8, len(full_nontargets)), :] 
            next_nontargets.reset_index(inplace=True, drop=True)
            next_nontargets.to_csv("tmp/p" +str(self.participantid)+ 
            "recmem_nontargets" + ".csv", index=False)                    
            if (btype=='multi'):
                targets = self.todays_multi.copy()
            else:
                targets = self.todays_single.copy()

            nontargets['corr'] = "n"
            nontargets = nontargets.rename(columns={'0' : 'Words'})
            targets['corr'] = "y"
            if (btype=='multi'):
                stim = pd.concat([nontargets, targets])
            else:
                stim = pd.concat([nontargets.iloc[[0],:], targets])    
            stim = stim.sample(frac=1)
            stim.reset_index(inplace=True, drop=True)
            choices, RTs = self.block(stim.iloc[:,0])
            match = [i==j for i, j in zip(choices, stim['corr'].values.tolist())]
            if all(match):
                self.canvas.clear()
                self.canvas.text('100% accuracy, great job!')  
                self.canvas.show() 
                core.wait(3)
                break
            else:
                self.canvas.clear()
                self.canvas.text('Oops, you missed 100% accuracy, please try again')  
                self.canvas.show() 
                core.wait(3)


        perf = pd.DataFrame({'RT': RTs, 'R':choices})
        perf['block'] = self.blocknum
        perf['day'] = self.day
        perf['cond'] = btype
        self.perf_data['RM' + 'day_' + str(self.day) + '_block_' + str(self.blocknum)] =   pd.concat([
            self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)], 
        perf], axis=1, sort=False)     

    def puzzle(self):
        self.canvas.text('Before you complete the experimental trials we would like you to complete a sudoku puzzle.\\n' +
        'Please find the puzzle on your desk. You have three minutes. Do not worry if there is not time to finish the puzzle.')
        self.canvas.show()
        core.wait(3)
        self.canvas.clear()
        self.canvas.text('It is now time to complete the task. Please rest your fingers on the KEYS and then press space')
        self.canvas.show()
        event.waitKeys(timeStamped=True)

    def save_data(self):
        for j in range(1, self.design.blocks+1):
            data = self.perf_data["day_" + str(self.day) + "_block_" + str(j)].copy()
            if j==1:
                day_dats= data
            else:
                day_dats = day_dats.append(data, ignore_index=True)
        day_dats.to_csv("data/p" +str(self.participantid)+ "_day_" + str(self.day)+ ".csv")
