from psychopy import visual, core, event
import numpy as np
import pandas as pd
import csv

class Experiment():
    def __init__(self, canvas, design):
        self.canvas = canvas
        self.design = design

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

    def block(self, trials):
        RTs = []
        choices = []
        ntrials=len(trials)
        for i in range(0,ntrials):
            RT, choice = self.trial(trials[i])
            RTs.append(RT)
            choices.append(choice)
        

class Canvas():

    def __init__(self, win):
        self.win = win
        self.stim_list = []
        self.clear()

    def copy(self, canvas):
        self.stim_list = canvas.stim_list + []

    def show(self):

        for stim in self.stim_list:
            stim.draw()
        self.win.flip(clearBuffer=True)
        return self.experiment.clock.time()

    def text(self, text):
        stim = visual.TextStim(win=self.win, text=text)
        self.stim_list.append(stim)

    def rect(self, x, y, w, h):
        self.shapestim([[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
                           close=True)
        pos = [x,y]
        stim = visual.GratingStim(win=self.win, pos=pos,
                                  size=[w, h], color=self.win.color, tex=None,
                                  interpolate=False)
        self.stim_list.append(stim)    

    def shapestim(self, vertices, fix_coor=True, close=False, fill= True):

        if fill:
            fill_color = self.win.color
        stim = visual.ShapeStim(self.win,
                                vertices=vertices,
                                lineColor=self.win.color, closeShape=close,
                                fillColor=fill_color, interpolate=False)
        self.stim_list.append(stim)

    def line(self, start, end, lineWidth):
        stim = visual.Line(self.win, start=start, end=end, lineWidth=lineWidth,
        units='pix')
        self.stim_list.append(stim)

    def fixcross(self):
        self.clear()
        self.line(start=[-15, 0], end=[15, 0], lineWidth=5)
        self.line(start=[0, -15], end=[0, 15], lineWidth=5)
        self.show()      

    def show(self):

        for stim in self.stim_list:
            stim.draw()
        self.win.flip(clearBuffer=True)
        return core.getTime()

    def clear(self):

        self.stim_list = []
        x, y = -self.win.size[0]/2 , -self.win.size[1]/2
        self.rect(x, y, self.win.size[0], self.win.size[1])

    def close_display(self):
        # prevent confusion
        self.win.close()


#def __init__(self, trials_file, subject_nr):
class Design():
    def __init__(self, stim_file, subject_nr, session_nr, blocks, days):
        # 1338 stimuli - 1:14 PM ratio gives 88 PM trials
        self.stim = pd.read_csv(stim_file)[0:1338]
        self.cb = subject_nr % 4
        self.id = str(subject_nr) + "_" + str(session_nr)
        self.data = pd.DataFrame()
        self.days = days
        self.blocks = blocks


    def initial_shuffle(self):
        stim_nwshuffled = self.stim.drop("Words", axis=1)
        stim_nwshuffled = stim_nwshuffled.sample(frac=1)
        stim_nwshuffled.reset_index(inplace=True, drop=True)
        stim_nwshuffled['Words'] = self.stim['Words']
        stim_bothshuffled = stim_nwshuffled.drop("Nonwords", axis=1)
        stim_bothshuffled = stim_bothshuffled.sample(frac=1)
        stim_bothshuffled.reset_index(inplace=True, drop=True)
        stim_bothshuffled['Nonwords'] = stim_nwshuffled['Nonwords']
        self.shuffledstim = stim_bothshuffled
   
    def set_ldt(self):
        self.initial_shuffle()
        self.single_cond_words= self.shuffledstim.loc[0:2, "Words"]
        self.multi_cond_words= self.shuffledstim.loc[2:18, "Words"]
        ongoing_task_items = self.shuffledstim.loc[18:1338]  
        ongoing_task_items= ongoing_task_items.reset_index()
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):

                block_num = (i-1)* self.blocks + j 

                words = ongoing_task_items.loc[block_num*288 - 
                288:block_num*288 -1, "Words"].values

                nonwords = ongoing_task_items.loc[block_num*330 - 
                330:block_num*330 -1, "Nonwords"].values

                self.data["day_" + str(i) + "_block_" + str(j)] = np.concatenate([words, nonwords])

    def set_pm_positions(self):
        tmp = pd.DataFrame()

 ###Define ranges to insert PM items into       
        starts = np.concatenate(
            [np.linspace(start=16, stop=316, num=21),
            np.linspace(start=346, stop=646, num=21)])

        stops = np.concatenate(
            [np.linspace(start=30, stop=330, num=21),
            np.linspace(start=360, stop=660, num=21)])
#################

        pm_positions=[]
        thisblock_stim = self.data.loc[:,"day_1_block_1"].values
        thisblock_pm = self.single_cond_words.values[0]

        for i in range(0, len(starts)):
            start = starts[i]
            stop = stops[i]
            
            if(i==0):
                last=0
            else:
                last = pm_positions[i-1]

            if (last>start-2):
                start = last + 2
            position=np.random.random_integers(start,stop)
            pm_positions.append(position)
            thisblock_stim = np.insert(thisblock_stim, position, thisblock_pm)

        tmp["day_1_block_1"] = thisblock_stim
        self.newdata = tmp
        self.pm_positions = pm_positions

 #       self.test =  self.data.loc[:,"day_1_block_1"].
#        tmp["day_1_block_1"] = np.concatenate([thisblock_stim, thisblock_pm])
        
    def save(self):
        self.shuffledstim.to_csv(self.id + ".csv")

def generate_pm_positions(starts, stops, pm_positions, thisblock_stim):
    for i in range(0, len(starts)):
        start = starts[i]
        stop = stops[i]
        
        if(i==0):
            last=0
        else:
            last = pm_positions[i-1]

        if (last>start-2):
            start = last + 2
        position=np.random.random_integers(start,stop)
        thisblock_stim = np.insert(thisblock_stim, position, thisblock_pm)


    return thisblock_stim