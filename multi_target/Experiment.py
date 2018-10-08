from psychopy import core, event
import numpy as np
import pandas as pd

instruct_delay = 0
puzzle_time = 5

first_trials=0
second_trials = 1

class Experiment():
    def __init__(self, canvas, design, day, participantid):
        self.participantid=participantid
        self.perf_data = {}
        self.canvas = canvas
        self.design = design
        self.rm_count = 1
        #read in response key counterbalance from csv
        keybalance = pd.read_csv("items/keybalance.csv").iloc[:,0] - 1

        responsekey_list = ({"word": 'd', "nonword" : 's', "pm" : 'j'},
                            {"word": 's', "nonword" : 'd', "pm" : 'j'},
                            {"word": 'j', "nonword" : 'k', "pm" : 'd'},
                            {"word": 'k', "nonword" : 'j', "pm" : 'd'})

        self.responsekeys = responsekey_list[self.participantid % 4]
        self.OThand = 'LEFT'
        if self.responsekeys["word"] == 'j' or self.responsekeys["word"] == 'k':
            self.OThand = 'RIGHT'
        self.design = design
        self.bal = participantid % 2 
        self.counterbalance = [np.array([["single", "multi"], ["multi", "single"]]),
        np.array([["multi", "single"], ["single", "multi"]])][self.bal]
        self.day = day
        self.blocknum = 1
        if day ==1:
            self.design.practice_stim(self.responsekeys["word"], self.responsekeys["nonword"], self.participantid)
            self.design.set_stim(self.counterbalance)
            self.design.set_pm_positions()
            self.design.create_blocks(self.responsekeys)
            self.design.insert_pm(self.counterbalance, self.responsekeys)
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

    def trial(self, stim, corr):
        self.canvas.fixcross()
        core.wait(0.5)
        self.canvas.clear()
        self.canvas.show()
        core.wait(0.25)
        pre_stim_resps = event.getKeys()
        self.canvas.text(stim)
        t0 = self.canvas.show()
        resp = event.waitKeys(timeStamped=True)
        #Not statement to deal with correct ldt responses on PM trials
        if resp[0][0]!=corr and not (corr=='p' and resp[0][0]=='w'):
            self.canvas.clear()    
            self.canvas.text("INCORRECT") 
            self.canvas.show()
            core.wait(1)
        self.canvas.clear()    
        self.canvas.show()
        return resp[0][0], resp[0][1] - t0, pre_stim_resps

    def create_instructions(self, btype):
        keyhands = (".\n\nPlease place the middle finger of your LEFT hand on the 's' key and the index finger of your LEFT hand on the 'd' key."+
        " Please make your lexical decision responses from this position.\n\n" + "Please locate the 'j' key now. During the next block of trials," +
        " please rest the index finger of your RIGHT hand here, ")
        if self.OThand=="RIGHT":
            keyhands = (".\n\nPlease place the middle finger of your RIGHT hand on the 'k' key and the index finger of your RIGHT hand on the 'j' key." +
            " Please make your lexical decision responses from this position.\n\n" +
            "Please locate the 'd' key now. During the next block of trials, please rest the index finger of your LEFT hand here, ")

        if(btype=='multi'):
            instruction1 = ("We have an interest in your ability to remember to perform actions in the future. \n\n" +
            "During the next block of lexical decision trials, we would like you to make an alternative response to certain target words.\n\n" + 
            " We will now present you the target words to memorize.")

            instruction2 = ("Please memorize the following target words \n\n"+
             ' '.join(self.todays_multi.values.flatten()) +
            "\n\n Once you have tried to memorize them, we will test you." +
            " You will be presented words one by one. Press the 'y' key if the word is on this list, otherwise press the 'n' key. \n\n"+
            "Press space to begin.")

            instruction3 = ("Here are the target words that you just memorized: \n\n"+
             ' '.join(self.todays_multi.values.flatten()) +
            " \n\n When you are presented any of these words during the the next block of lexical decision trials, we would like you to press "+
            self.responsekeys['pm']+" INSTEAD of "+ self.responsekeys['word'] +
            keyhands + "and use it to make your response if you see an item from your target list.\n\n " +
            "Please speak with the experimenter about your instructions.")

        elif(btype=='single'):
            instruction1 = ("We have an interest in your ability to remember to perform actions in the future. \n\n" +
            "During the next block of lexical decision trials, we would like you to make an alternative response to a target word.\n\n" + 
            " We will now present you the target word to memorize.")

            instruction2 = ("Please memorize the following target word \n\n"+
             ' '.join(self.todays_single.values.flatten()) +
            "\n\n Once you have memorized the word, we will test you." +
            " You will be presented words one by one. Press the 'y' key if the word is your target word, otherwise press the 'n' key. \n\n"+
            "Press space to begin.")

            instruction3 = ("Here is the target word that you just memorized: \n\n"+
             ' '.join(self.todays_single.values.flatten()) +
            " \n\n When you are presented this word during the the next block of lexical decision trials, we would like you to press "+
            self.responsekeys['pm']+" INSTEAD of "+ self.responsekeys['word'] +
            keyhands + "and use it to make your response if you see your target word.\n\n " +
            "Please speak with the experimenter about your instructions.")

        return instruction1, instruction2, instruction3
 
    def print_instructions(self, instructions, delay, waitkey= None, size=None,
    height=None, wrapWidth = None):
        self.canvas.clear()
        self.canvas.text(instructions, height=height, wrapWidth=wrapWidth)
        self.canvas.show()
        core.wait(delay)
        if event.getKeys(['escape']):
            self.canvas.close_display()
            core.quit()      
        if (waitkey is not None):
            resp = event.waitKeys(keyList= [waitkey, 'escape'], timeStamped=True)
            if (resp[0][0]=='escape'):
                self.canvas.close_display()
                core.quit()    

    def block_leadup(self, btype):
        block_instructions, recmem_instructions, response_instructions = self.create_instructions(btype)
        self.print_instructions(block_instructions, instruct_delay, 'space', height = 0.085, wrapWidth= 1.65)
        self.print_instructions(recmem_instructions, instruct_delay, 'space', height = 0.085, wrapWidth= 1.65)
        self.recmem_block(btype)
        self.canvas.clear()
        self.print_instructions(response_instructions, instruct_delay, 'n', height = 0.085, wrapWidth= 1.65)
        self.puzzle()

 #here add a mid block break      
    def run_block(self, btype):
        self.block_leadup(btype)
        choices1, RTs1, pre_stim_resps1 = self.block(self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)].loc[0:first_trials,'stim'],
            self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)].loc[0:first_trials:,'C'])
        self.print_instructions("Please take a break for one minute.", 5)  
        self.print_instructions("Press space to begin the task again.", 0, waitkey = "space")   
 #insert block break here  
 # #add tolist to reset index  
        choices2, RTs2, pre_stim_resps2 = self.block(self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)].loc[(first_trials+1 ):second_trials,'stim'].tolist(),
            self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)].loc[(first_trials+1 ):second_trials:,'C'].tolist())
        choices = choices1 + choices2
        RTs = RTs1 + RTs2     
        pre_stim_resps = pre_stim_resps1 + pre_stim_resps2
        perf = pd.DataFrame({'RT': RTs, 'R':choices, 'prestim_R':pre_stim_resps, 
                             'block':self.blocknum, 'day':self.day, 'cond':btype})
        self.perf_data['day_' + str(self.day) + '_block_' + str(self.blocknum)] =   pd.concat([
            self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)], 
        perf], axis=1, sort=False)     
        self.blocknum += 1

    def practice_block(self):
        stim = pd.read_csv("tmp/p"+str(self.participantid)+"_practice.csv")
        stim = stim.sample(frac=1).reset_index()
        keyhands = "\n\nPlease place the middle finger of your LEFT hand on the 's' key and the index finger of your LEFT hand on the 'd' key. Please make your lexical decision responses from this position."
        if self.OThand=="RIGHT":
            keyhands = "Please place the middle finger of your RIGHT hand on the 'k' key and the index finger of your RIGHT hand on the 'j' key. Please make your lexical decision responses from this position."

        instructions = ("Welcome to the experiment. You will perform a lexical decision task, in which you must decide whether strings of letters are" +
            " words or non-words.\n\n Each trial begins with a fixation cross which appears on the screen for a short time, followed by a string of lower case letters." +
            " Once each item is presented you must indicate with a keypress whether or not the string of letters forms an English word.  Please answer as ACCURATELY,  but as QUICKLY as you can.\n\n" +
            "Locate the '" + self.responsekeys['word'] +"' key.  When the string appears press the '" + self.responsekeys['word'] +"' key if the string is an English word.\n\n" +
            "Locate the '" + self.responsekeys['nonword'] +"' key.  When the string appears press the '" + self.responsekeys['nonword'] +"' key if the string is NOT an English word."+
            keyhands +
            "\n\n You will now perform some practice trials. Press space to begin."
            )
        self.print_instructions(instructions, instruct_delay, 'space', height = 0.075, wrapWidth= 1.65)
        choices, RTs, pre_stim_resps = self.block(stim["stim"], stim["C"])
        perf = pd.DataFrame({'RT': RTs, 'R':choices, 
                        'day':self.day, 'cond':'practice', 'stim' : stim.loc[range(0, len(RTs)), "stim"],
                        'C' : stim.loc[range(0, len(RTs)), "C"], 'prestim_R':pre_stim_resps})
        perf.to_csv("data/practice_p" +str(self.participantid)+ "_day_" + str(self.day)+ ".csv")

    def run_both_blocks(self):
        for block in range(0,2):
            self.run_block(self.counterbalance[self.day-1, block])

    def block(self, trials, corrs):
        RTs = []
        choices = []
        pre_stim = []
        #len(trials)
        ntrials=1
        for i in range(0,ntrials):           
            choice, RT, pre_stim_resps = self.trial(trials[i], corrs[i])
            RTs.append(RT)
            choices.append(choice)
            pre_stim.append (pre_stim_resps)
            core.wait(0.5)
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
        #add in a check that there are enough recmem targets in the .csv
        # If <8 targets, create a new file    
            stim = self.recmem_newstim(btype)
            choices, RTs, pre_stim_resps = self.block(stim.iloc[:,0], stim.iloc[:,1])
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
                self.print_instructions('100% accuracy, great job!', 3, 'space')  
                break
            else:
                 self.print_instructions('You were not 100% accurate, please try again.', 3, 'space') 
     
    def puzzle(self):
        self.print_instructions('Before you complete the lexical decision trials we would like you to complete a sudoku puzzle.\n\n' +
        'Please find the puzzle on your desk. You have three minutes. Do not worry if there is not time to finish the puzzle.', 
        puzzle_time)
        self.print_instructions(("It is now time to begin the lexical decision trials. \n\n" +
        "Please rest your fingers on the response keys."+
        " Press space when you are ready to begin."), 1, 'space')

    def save_data(self):
        for j in range(1, self.design.blocks+1):
            data = self.perf_data["day_" + str(self.day) + "_block_" + str(j)].copy()
            if j==1:
                day_dats= data
            else:
                day_dats = day_dats.append(data, ignore_index=True)
        day_dats.to_csv("data/p" +str(self.participantid)+ "_day_" + str(self.day)+ ".csv")
