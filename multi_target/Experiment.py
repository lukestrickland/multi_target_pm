from psychopy import core, event
from Instructions import Instructions
import numpy as np
import pandas as pd
from parameters import *


'''Experiment object which is meant to do
things like run the trials, blocks, etc.'''


class Experiment():
    def __init__(self, canvas, design, day, participantid):
        self.participantid = participantid
        self.perf_data = {}
        self.canvas = canvas
        self.design = design
        self.rm_count = 1
        # read in response key counterbalance from csv
        keybalance = pd.read_csv(
            "items/keybalance.csv", header=None).iloc[self.participantid, 0] - 1

        responsekey_list = ({"word": 'd', "nonword": 's', "pm": 'j'},
                            {"word": 's', "nonword": 'd', "pm": 'j'},
                            {"word": 'j', "nonword": 'k', "pm": 'd'},
                            {"word": 'k', "nonword": 'j', "pm": 'd'})

        self.responsekeys = responsekey_list[keybalance]
        # Will need to associate keybalance with hand for instructions
        self.OThand = 'LEFT'
        if self.responsekeys["word"] == 'j' or self.responsekeys["word"] == 'k':
            self.OThand = 'RIGHT'
        self.bal = participantid % 2
        self.counterbalance = [np.array([["single", "multi"], ["multi", "single"]]),
                               np.array([["multi", "single"], ["single", "multi"]])][self.bal]
        self.day = day
        # blocknum will increment as the experiment runs
        self.blocknum = 1
        if day == 1:
         # create stimuli
            self.design.practice_stim(
                self.responsekeys["word"], self.responsekeys["nonword"], self.participantid)
            self.design.set_stim(self.counterbalance)
            self.design.set_pm_positions(5)
            self.design.create_blocks(self.responsekeys)
            self.design.insert_pm(self.counterbalance, self.responsekeys)
            self.design.setup_data(self.participantid, self.counterbalance)
            self.design.gen_recmem_nontargets(self.participantid)
        else:
            self.design.read_data(participantid)
        # read in PM stimuli as need to display them in instructions
        self.todays_multi = self.design.multi_cond_words.to_frame().copy().iloc[
            range((self.day-1)*8, (self.day-1)*8+8), :]
        self.todays_single = self.design.single_cond_words.to_frame().copy().iloc[[
            self.day-1]]
        self.todays_single = self.todays_single.rename(columns={1: 'Words'})
        self.todays_multi = self.todays_multi.rename(columns={1: 'Words'})
        self.instructions = Instructions(
            self.responsekeys, self.todays_multi, self.todays_single)

    def trial(self, stim, corr=None):
        self.canvas.fixcross()
        core.wait(0.5)
        self.canvas.clear()
        self.canvas.show()
        core.wait(0.25)
        pre_stim_resps = event.getKeys()
        self.canvas.text(stim)
        #New way to get accurate ms timing
        trial_clock = core.Clock()
        self.canvas.win.callOnFlip(trial_clock.reset)
        self.canvas.show()
        resp = event.waitKeys(timeStamped=trial_clock)
        #If statement to deal with case when participants are getting RM tested-
        #no feedback except telling them not to press random keys
        if corr is None:
            if (resp[0][0] != 'y' and resp[0][0] != 'n'): 
                self.canvas.clear()
                self.canvas.text("INVALID RESPONSE KEY")
                self.canvas.show()
                core.wait(2)
        elif resp[0][0] != corr and not (corr == self.responsekeys["pm"] and resp[0][0] == self.responsekeys["word"]):
            self.canvas.clear()
            self.canvas.text("INCORRECT")
            self.canvas.show()
            core.wait(1)
        self.canvas.clear()
        self.canvas.show()
        # return response, RT, list of pre stimulus responses
        return resp[0][0], resp[0][1], pre_stim_resps

    def print_instructions(self, instructions, delay, waitkey=None, size=None,
                           height=None, wrapWidth=None):
        self.canvas.clear()
        self.canvas.text(instructions, height=height, wrapWidth=wrapWidth)
        self.canvas.show()
        core.wait(delay)
        if event.getKeys(['escape']):
            self.canvas.close_display()
            core.quit()
        if (waitkey is not None):
            resp = event.waitKeys(
                keyList=[waitkey, 'escape'], timeStamped=True)
            if (resp[0][0] == 'escape'):
                self.canvas.close_display()
                core.quit()

    def block_leadup(self, btype):
        block_instructions, recmem_instructions1, recmem_instructions2, response_instructions = self.instructions.block_instructions(
            btype)

        self.print_instructions(
            block_instructions, instruct_delay, 'space', height=0.085, wrapWidth=1.65)
        self.print_instructions(
            recmem_instructions1, memorize_delay, height=0.085, wrapWidth=1.65)
        self.print_instructions(
            recmem_instructions2, instruct_delay, 'space', height=0.085, wrapWidth=1.65)
        self.recmem_practice(btype)
        self.canvas.clear()
        self.print_instructions(
            response_instructions, instruct_delay, 'n', height=0.085, wrapWidth=1.65)
        self.puzzle()

    def block_main(self, btype):
        choices1, RTs1, pre_stim_resps1 = self.block(self.design.data['day_' + str(self.day) + '_block_' + str(
        self.blocknum)].loc[0:first_trials, 'stim'],
        self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)].loc[0:first_trials:, 'C'])
        self.print_instructions(
        "Please take a break for one minute.", break_delay)
        self.print_instructions(
        "Press space to begin the task again.", 0, waitkey='space')
    # Mid block break
        choices2, RTs2, pre_stim_resps2 = self.block(self.design.data['day_' + str(self.day) + '_block_' + str(
            self.blocknum)].loc[(first_trials+1):second_trials, 'stim'].tolist(),
            self.design.data['day_' + str(self.day) + '_block_' + str(
                self.blocknum)].loc[(first_trials+1):second_trials:, 'C'].tolist())
    # Combine data from the halves and save
        choices = choices1 + choices2
        RTs = RTs1 + RTs2
        pre_stim_resps = pre_stim_resps1 + pre_stim_resps2
        perf = pd.DataFrame({'RT': RTs, 'R': choices, 'prestim_R': pre_stim_resps,
                                'block': self.blocknum, 'day': self.day, 'cond': btype})
        self.perf_data['day_' + str(self.day) + '_block_' + str(self.blocknum)] = pd.concat([
            self.design.data['day_' + str(self.day) + '_block_' + str(
                self.blocknum)],
            perf], axis=1, sort=False)       

    def block_ending(self, btype):
        self.recmem_test(btype)
        if (btype == 'multi'):
            self.print_instructions(
                ("Thank you. You no longer need to remember your target words."
                 " In fact, you will not be presented those words again in this"
                 " experiment. Press space to continue."), 0, waitkey="space")
        else:
            self.print_instructions(
                ("Thank you. You no longer need to remember your target word."
                 " In fact, you will not be presented that word again in this"
                 " experiment. Press space to continue."), 0, waitkey="space")

        if self.blocknum == 1:
            self.print_instructions(
                "Please have a break for two minutes.", break_time)

        self.blocknum += 1

    def run_block(self, btype):
        self.block_leadup(btype)
        self.block_main(btype)
        self.block_ending(btype)

    # loads up practice stimuli, runs practice block
    def practice_block(self):
        stim = pd.read_csv("tmp/p"+str(self.participantid)+"_practice.csv")
        stim = stim.sample(frac=1).reset_index()
        self.print_instructions(self.instructions.practice_instructions(
        ), instruct_delay, 'space', height=0.075, wrapWidth=1.65)
        choices, RTs, pre_stim_resps = self.block(stim["stim"], stim["C"])
        perf = pd.DataFrame({'stim': stim.loc[range(0, len(RTs)), "stim"],
                             'S': stim.loc[range(0, len(RTs)), "S"],
                             'C': stim.loc[range(0, len(RTs)), "C"],
                             'RT': RTs, 'R': choices, 'prestim_R': pre_stim_resps,
                             'day': self.day, 'cond': 'practice'})
        perf.to_csv("data/practice_p" + str(self.participantid) +
                    "_day_" + str(self.day) + ".csv")

    def run_both_blocks(self):
        for block in range(0, 2):
            self.run_block(self.counterbalance[self.day-1, block])

    def block(self, trials, corrs=None):
        RTs = []
        choices = []
        pre_stim = []
        ntrials = len(trials)
        if pilot:
            ntrials = 1
        for i in range(0, ntrials):
            if (corrs is None):
                choice, RT, pre_stim_resps = self.trial(trials[i])
            else:
                choice, RT, pre_stim_resps = self.trial(trials[i], corrs[i])
            RTs.append(RT)
            choices.append(choice)
            pre_stim.append(pre_stim_resps)
            core.wait(0.5)
            if event.getKeys(['escape']):
                self.canvas.close_display()
                core.quit()
        return choices, RTs, pre_stim

    '''fairly cooked. Before each block,
    participants do a recognition memory task to make sure they
    perfectly recall the items. The recognition memory task involves
    50% non-targets and 50% target items. I have stored a list of 
    non-targets in a separate csv, which are shuffled when the experiment
    is initialised. However, I was concerned that this list might run out 
    if people kept getting the RM task wrong. Thus there is a check at 
    the start to make sure there are enough targets, and if not then shuffle
    a new RM target list from scratch.'''

    def recmem_newstim(self, btype, n_copies, n_nontargets):
        # Shuffle in new rec-mem non-targets each loop from a csv
        full_nontargets = pd.read_csv("tmp/p" + str(self.participantid) +
                                      "recmem_nontargets" + ".csv")
        full_nontargets.dropna(how="all", inplace=True)
        # if there's not enough targets, re-generate them from scratch
        if (len(full_nontargets) < n_nontargets):
            self.design.gen_recmem_nontargets(self.participantid)
            full_nontargets = full_nontargets.append(pd.read_csv("tmp/p" + str(self.participantid) +
                                                                 "recmem_nontargets" + ".csv"))
            full_nontargets.reset_index(inplace=True, drop=True)

        nontargets = full_nontargets.copy().iloc[0:n_nontargets, 1].to_frame()
        next_nontargets = full_nontargets.copy(
        ).loc[range(n_nontargets, len(full_nontargets)), :]

        next_nontargets.reset_index(inplace=True, drop=True)
        next_nontargets.to_csv("tmp/p" + str(self.participantid) +
                               "recmem_nontargets" + ".csv", index=False)
        if (btype == 'multi'):
            targets = self.todays_multi.copy()
        else:
            targets = pd.concat([self.todays_single.copy()]
                                * 8, ignore_index=True)

        nontargets['corr'] = "n"
        nontargets = nontargets.rename(columns={'0': 'Words'})
        targets['corr'] = "y"

        stim = pd.concat([nontargets, targets])
        stim = stim.sample(frac=1)
        stim.reset_index(inplace=True, drop=True)
#Copy/shuffle/append the stimulus list to make as many trials as desired
        for i in range(1, n_copies):
            stim2 = stim.copy()
            stim2 = stim2.sample(frac=1)
            stim2.reset_index(inplace=True, drop=True)  
            stim = stim.append(stim2)
            stim.reset_index(inplace=True, drop=True)     

        return(stim)

    '''runs the recognition memory task until perfect accuracy. In the 
    single target condition, participants are presented one target word
    and one non-target word. 8 of each in the multi target condition'''

    def recmem_practice(self, btype):
      # run recmem trials til 100% accuracy
        while True:
            # add in a check that there are enough recmem targets in the .csv
            # If <8 targets, create a new file
            stim = self.recmem_newstim(btype, n_copies=2, n_nontargets=8)    
            choices, RTs, pre_stim_resps = self.block(
                stim.iloc[:, 0], stim.iloc[:, 1])
            # Update recmem saved data
            perf = pd.DataFrame({'stim': stim.loc[range(0, len(RTs)), 'Words'],
                                 'C': stim.loc[range(0, len(RTs)), 'corr'],
                                 'RT': RTs, 'R': choices, 'prestim_R': pre_stim_resps,
                                 'block': self.blocknum, 'day': self.day, 'cond': btype,
                                 'count': self.rm_count
                                 }
                                )
            if (self.rm_count == 1):
                perf.to_csv("data/RM_p" + str(self.participantid) +
                            "_day_" + str(self.day) + ".csv", index=False)
            elif(self.rm_count > 1):
                old_perf = pd.read_csv(
                    "data/RM_p" + str(self.participantid) + "_day_" + str(self.day) + ".csv")
                new_perf = old_perf.append(perf)
                new_perf.to_csv("data/RM_p" + str(self.participantid) +
                                "_day_" + str(self.day) + ".csv", index=False)
            # rm_count keeps track of how many tries they had at the RM task
            self.rm_count += 1
            # check if all answers correct
            match = [i == j for i, j in zip(
                choices, stim['corr'].values.tolist())]
            if all(match):
                self.print_instructions(
                    ('100% accuracy, great job!'
                     ' Press space to continue'),
                    3, 'space')
                break
            else:
                if (btype == 'single'):
                    self.print_instructions(
                        ('You were not 100% accurate, please study the target word'
                         ' and try again. Press space when ready.'), 3, 'space')
                    self.print_instructions("Here is the target word: \n\n" +
                                            ' '.join(self.todays_single.values.flatten()) +
                                            "\n\n Press space when you are ready for another test.", 3, 'space')
                else:
                    self.print_instructions(
                        ('You were not 100% accurate, please study the target words'
                         ' and try again. Press space when ready.'), 3, 'space')
                    self.print_instructions("Here are the target words: \n\n" +
                                            ' '.join(self.todays_multi.values.flatten()) +
                                            "\n\n Press space when you are ready for another test.", 3, 'space')

# Runs the RM test once (to get recognition after the block)
    def recmem_test(self, btype):
        if (btype == 'multi'):
            RM1 = "words."
            RM2 = "from your target list"
        else:
            RM1 = "word."
            RM2 = "your target word"
        self.print_instructions(
            ("Great work completing the block!"
             " We now wish to test your memory for your target " +
             RM1 +
             " You will be presented words one by one. Press the 'y' key if the "
             "word is " +
             RM2 +
             ", otherwise press the 'n' key. \n"
             "Note that in this block you will NOT receive"
             " feedback indicating whether your answers are correct. \n"
             "Press space to begin."), 3, 'space')

        stim = self.recmem_newstim(btype, n_copies=1, n_nontargets=24)
        choices, RTs, pre_stim_resps = self.block(
            stim.iloc[:, 0])
        # Update recmem saved data
        perf = pd.DataFrame({'stim': stim.loc[range(0, len(RTs)), 'Words'],
                             'C': stim.loc[range(0, len(RTs)), 'corr'],
                             'RT': RTs, 'R': choices, 'prestim_R': pre_stim_resps,
                             'block': self.blocknum, 'day': self.day, 'cond': btype
                             }
                            )
        perf.to_csv("data/test_RM_p" + str(self.participantid) +
                    "_day_" + str(self.day) + "_" + str(btype) + ".csv", index=False)

# distractor puzzle before they complete the task

    def puzzle(self):
        self.print_instructions(('Before you complete the lexical decision trials we would like you'
                                 ' to complete a sudoku puzzle.\n\n Please find the puzzle on your desk. '
                                 'You have three minutes. Do not worry if there is not time to finish the puzzle.'),
                                puzzle_time)
        self.print_instructions(("It is now time to begin the lexical decision trials. \n\n"
                                 "Please rest your fingers on the response keys."
                                 " Press space when you are ready to begin."), 1, 'space')
# saves of the main data at the end of the experiment.

    def save_data(self):
        for j in range(1, self.design.blocks+1):
            data = self.perf_data["day_" +
                                  str(self.day) + "_block_" + str(j)].copy()
            if j == 1:
                day_dats = data
            else:
                day_dats = day_dats.append(data, ignore_index=True)
        day_dats.to_csv("data/p" + str(self.participantid) +
                        "_day_" + str(self.day) + ".csv")
