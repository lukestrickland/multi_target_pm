from psychopy import visual, core, event
import numpy as np
import pandas as pd
import csv

#cheeky function to insert row into pandas data frame
def insert_row(idx, df, df_insert):
    return df.iloc[:idx, ].append(df_insert).append(df.iloc[idx:, ]).reset_index(drop = True)

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
        self.stim = pd.read_csv(stim_file)[0:1346]
        self.cb = subject_nr % 4
        self.id = str(subject_nr) + "_" + str(session_nr)
        self.words = pd.DataFrame()
        self.nonwords = pd.DataFrame()
        self.days = days
        self.blocks = blocks
        self.data = {}
        self.design = np.array([["single", "multi"], ["multi", "single"]])
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
        ###Define ranges to insert PM items into 
                self.data["day_" + str(i) + "_block_" + str(j)] = 0


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
        ongoing_task_items = self.shuffledstim.loc[18:1346]  
        ongoing_task_items= ongoing_task_items.reset_index()
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):

                block_num = (i-1)* self.blocks + j 

                words = ongoing_task_items.loc[block_num*290 - 
                290:block_num*290 -1, "Words"].values

                nonwords = ongoing_task_items.loc[block_num*332 - 
                332:block_num*332 -1, "Nonwords"].values

                self.words["day_" + str(i) + "_block_" + str(j)] = words
                self.nonwords["day_" + str(i) + "_block_" + str(j)] = nonwords

    def set_pm_positions(self):
        tmp = pd.DataFrame()
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
        ###Define ranges to insert PM items into       
                starts = np.concatenate(
                    [np.linspace(start=3, stop=318, num=22),
                    np.linspace(start=336, stop=651, num=22)])

                stops = np.concatenate(
                    [np.linspace(start=17, stop=332, num=22),
                    np.linspace(start=350, stop=665, num=22)])
        #################

                pm_positions=[]
                for k in range(0, len(starts)):
                    start = starts[k]
                    stop = stops[k]
                    
                    if(k==0):
                        last=0
                    else:
                        last = pm_positions[k-1]

                    if (last>start-2):
                        start = last + 2
                    position=np.random.random_integers(start,stop)
                    pm_positions.append(position)

                tmp["day_" + str(i) + "_block_" + str(j)] = pm_positions

        self.pm_positions = tmp

    def create_blocks(self):    
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
                word_df= pd.DataFrame(self.words["day_" + str(i) + "_block_" + str(j)])
                word_df['S']="W"
                nonword_df= pd.DataFrame(self.nonwords["day_" + str(i) + "_block_" + str(j)])
                nonword_df['S']="N"
                tmp=word_df.append(nonword_df)
                tmp.columns = ["stim", "S"]
                self.data["day_" + str(i) + "_block_" + str(j)] = tmp.sample(frac=1).reset_index(drop=True)

    def insert_pm(self):
        newstim = pd.DataFrame()
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
        ###Define ranges to insert PM items into 
                pm_target ={"stim":[ "single"], "S":[ "P"]}
                if self.design[i-1,j-1]=='multi':
                    pm_target['stim']='multi'
                pm_target = pd.DataFrame(pm_target)[["stim", "S"]]
                pm_positions = self.pm_positions.loc[:,"day_" + str(i) + "_block_" + str(j)].values
                thisblock_stim = self.data["day_" + str(i) + "_block_" + str(j)]
                thisblock_stim.columns=["stim", "S"]
                for position in pm_positions:
                    thisblock_stim = insert_row(position, thisblock_stim, pm_target)
                self.data["day_" + str(i) + "_block_" + str(j)] = thisblock_stim
      
    def save(self):
        self.shuffledstim.to_csv(self.id + ".csv")

