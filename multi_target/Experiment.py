from psychopy import core, event
import numpy as np
import pandas as pd

instruct_delay = 0
puzzle_time = 3


class Experiment():
    def __init__(self, canvas, design, day, participantid):
        self.participantid=participantid
        self.perf_data = {}
        self.canvas = canvas
        self.design = design
        self.rm_count = 1
        #read in response key counterbalance from csv
        keybalance = pd.read_csv("items/keybalance.csv").iloc[:,0] - 1

        responsekey_list = ({"word": 'd', "won-word" : 's', "pm" : 'j'},
                            {"word": 's', "won-word" : 'd', "pm" : 'j'},
                            {"word": 'j', "won-word" : 'k', "pm" : 'd'},
                            {"word": 'k', "won-word" : 'j', "pm" : 'd'})

        self.responsekeys = responsekey_list[self.participantid % 4]
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
            recmem_nontargets = pd.read_csv('items/recmem_nontargets.csv', header=None)
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
        return resp[0][0], resp[0][1] - t0, pre_stim_resps

    def create_instructions(self, btype):
        if(btype=='multi'):
            instruction1 = ("We have an interest in your ability to remember to perform actions in the future. " +
            "In the next block of lexical decision trials, for EIGHT target words we would like you to then press " +
            self.responsekeys['pm'] +" INSTEAD of "+ self.responsekeys['word'] +". On the next slide, we will present to you the target words to memorize.")

            instruction2 = ("Please remember the following target words \n\n"+
             ' '.join(self.todays_multi.values.flatten()) +
            "\n\n Once you have tried to memorize them, we want to test you." +
            " You will be presented words one by one. Press the 'y' key if the word is on this list, otherwise press the 'n' key. ")

        elif(btype=='single'):
            instruction1 =("We have an interest in your ability to remember to perform actions in the future."+
            "In the next block of lexical decision trials, for ONE target word we would like you to then press "+
            self.responsekeys['pm'],"INSTEAD of", self.responsekeys['word'],". On the next slide, we will present to you the target word to memorize.")

            instruction2 = ("Please remember the following:"+
            "Once you are finished memorizing, you will be tested on your recognition of the words." +
            "You will be presented words one by one. Press the 'y' key if the word is on this list, otherwise press the 'n' key. "+
            'The target words are:'
             ' '.join(self.todays_single.values.flatten()) +
             "Please press any key to proceed to your memory test.")
        return instruction1, instruction2
 
    def print_instructions(self, instructions, delay, waitkey= None):
        self.canvas.clear()
        self.canvas.text(instructions)
        self.canvas.show()
        core.wait(delay)
        if (waitkey is not None):
            resp = event.waitKeys(keyList= [waitkey], timeStamped=True)       

    def block_leadup(self, btype):
        block_instructions, recmem_instructions = self.create_instructions(btype)
        self.print_instructions(block_instructions, instruct_delay, 'n')
        self.print_instructions(recmem_instructions, instruct_delay, 'n')
        self.recmem_block(btype)
        self.canvas.clear()
        self.puzzle()
       
    def run_block(self, btype):
        self.block_leadup(btype)
        choices, RTs, pre_stim_resps = self.block(self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)].loc[:,'stim'])
        perf = pd.DataFrame({'RT': RTs, 'R':choices, 'prestim_R':pre_stim_resps})
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
        pre_stim = []
        #len(trials)
        ntrials=2
        for i in range(0,ntrials):           
            choice, RT, pre_stim_resps = self.trial(trials[i])
            RTs.append(RT)
            choices.append(choice)
            pre_stim.append (pre_stim_resps)
            core.wait(2)
            if event.getKeys(['escape']):
                self.canvas.close_display()
                core.quit()
        return choices, RTs, pre_stim

    def recmem_newstim(self, btype):
        #Shuffle in new rec-mem non-targets each loop from a csv
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
            return(stim)

    def recmem_block(self, btype):
      #run recmem trials til 100% accuracy  
        while True:
            stim = self.recmem_newstim(btype)
            choices, RTs, pre_stim_resps = self.block(stim.iloc[:,0])
            #Update recmem saved data
            perf = pd.DataFrame({'RT': RTs, 'R':choices, 'block':self.blocknum,
                        'day':self.day, 'cond':btype, 'stim' : stim.loc[range(0, len(RTs)),'Words'],
                        'C' : stim.loc[range(0, len(RTs)),'corr'], 'count': self.rm_count,
                        'prestim_R':pre_stim_resps})
            if (self.rm_count==1):
                perf.to_csv("data/RM_p" +str(self.participantid)+ "_day_" + str(self.day)+ ".csv", index=False)
            elif(self.rm_count>1):
                old_perf = pd.read_csv("data/RM_p" +str(self.participantid)+ "_day_" + str(self.day)+ ".csv")
                new_perf = old_perf.append(perf)
                new_perf.to_csv("data/RM_p" +str(self.participantid)+ "_day_" + str(self.day)+ ".csv", index=False)
            self.rm_count += 1
            #check if all answers correct
            match = [i==j for i, j in zip(choices, stim['corr'].values.tolist())]
            if all(match):
                self.print_instructions('100% accuracy, great job!', 3, 'n')  
                break
            else:
                 self.print_instructions('Oops, you missed 100% accuracy, please try again', 3, 'n') 
     
    def puzzle(self):
        self.print_instructions('Before you complete the experimental trials we would like you to complete a sudoku puzzle.\\n' +
        'Please find the puzzle on your desk. You have three minutes. Do not worry if there is not time to finish the puzzle.', 
        puzzle_time)
        self.print_instructions('It is now time to complete the task. Please rest your fingers on the KEYS and then press space', 1, 'n')

    def save_data(self):
        for j in range(1, self.design.blocks+1):
            data = self.perf_data["day_" + str(self.day) + "_block_" + str(j)].copy()
            if j==1:
                day_dats= data
            else:
                day_dats = day_dats.append(data, ignore_index=True)
        day_dats.to_csv("data/p" +str(self.participantid)+ "_day_" + str(self.day)+ ".csv")
