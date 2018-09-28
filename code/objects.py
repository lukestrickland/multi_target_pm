from psychopy import visual, core, event
import numpy as np
import pandas as pd
import csv

ldt_instructions = "In the next block of trials, you will again perform \n\n"

#cheeky function to insert row into pandas data frame
def insert_row(idx, df, df_insert):
    return df.iloc[:idx, ].append(df_insert).append(df.iloc[idx:, ]).reset_index(drop = True)

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
    def __init__(self, stim_file, blocks, days):
        # 1338 stimuli - 1:14 PM ratio gives 88 PM trials
        self.stim = pd.read_csv(stim_file)[0:1352]
        self.words = pd.DataFrame()
        self.nonwords = pd.DataFrame()
        self.pmtargets = pd.DataFrame()
        self.days = days
        self.blocks = blocks
        self.data = {}
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


    def set_stim(self, counterbalance):
        self.initial_shuffle()
        self.single_cond_words= self.shuffledstim.loc[0:1, "Words"]
        self.multi_cond_words= self.shuffledstim.loc[2:17, "Words"]
        #setup pandas df of single target PM words for days 1 and day 2 and multi target 

        ongoing_task_items = self.shuffledstim.loc[18:1278]  
        ongoing_task_items= ongoing_task_items.reset_index()
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):

                block_num = (i-1)* self.blocks + j 

                words = ongoing_task_items.loc[block_num*273 - 
                273:block_num*273 -1, "Words"].values

                nonwords = ongoing_task_items.loc[block_num*315 - 
                315:block_num*315 -1, "Nonwords"].values

                if counterbalance[i-1,j-1]=="single":
                    pmtargets = [self.single_cond_words.values[i-1]] * 48
                else:
                    pmtargets = np.ndarray.tolist(self.multi_cond_words.values[(i-1)*8:(i*8)]) * 6
                np.random.shuffle(pmtargets)
                pmtargets = np.array(pmtargets)

                self.pmtargets["day_" + str(i) + "_block_" + str(j)] = pmtargets
                self.words["day_" + str(i) + "_block_" + str(j)] = words
                self.nonwords["day_" + str(i) + "_block_" + str(j)] = nonwords

    def set_pm_positions(self):
        tmp = pd.DataFrame()
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
        ###Define ranges to insert PM items into       
                starts = np.concatenate(
                    [np.linspace(start=3, stop=302, num=24),
                    np.linspace(start=318, stop=617, num=24)])

                stops = np.concatenate(
                    [np.linspace(start=16, stop=315, num=24),
                    np.linspace(start=331, stop=630, num=24)])
        #################

                pm_positions=[]
                for k in range(0, len(starts)):
                    start = starts[k]
                    stop = stops[k]
                    
                    if(k==0):
                        last=0
                    else:
                        last = pm_positions[k-1]

                    if (last>=start-5):
                        start = last + 6
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

    def insert_pm(self, counterbalance):
        newstim = pd.DataFrame()
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
        ###Define ranges to insert PM items into 
                target_list = self.pmtargets.loc[:,"day_" + str(i) + "_block_" + str(j)].values
                pm_target ={"stim":self.single_cond_words[0], "S":[ "P"]}
                if counterbalance[i-1,j-1]=='multi':
                    pm_target['stim']='multi'
                pm_target = pd.DataFrame(pm_target)[["stim", "S"]]
                pm_positions = self.pm_positions.loc[:,"day_" + str(i) + "_block_" + str(j)].values
                thisblock_stim = self.data["day_" + str(i) + "_block_" + str(j)]
                thisblock_stim.columns=["stim", "S"]
                l = 0
                for position in pm_positions:
                    pm_target.values[0,0] = target_list[l]
                    thisblock_stim = insert_row(position, thisblock_stim, pm_target)
                    l+=1

                self.data["day_" + str(i) + "_block_" + str(j)] = thisblock_stim
      
    def setup_data(self, pid, counterbalance):
        for i in range(1, self.days+1):
            day_dats = pd.DataFrame()
            for j in range(1, self.blocks+1):
                data = self.data["day_" + str(i) + "_block_" + str(j)].copy()
                data['R'] = -1
                data['RT'] = -1
                data['block'] = j
                data['day'] = i
                data['cond'] = counterbalance[i-1,j-1]
                if j==1:
                    day_dats= data
                else:
                    day_dats = day_dats.append(data, ignore_index=True)
            day_dats.to_csv("data/p" +str(pid)+ "_day_" + str(i)+ ".csv")
            self.single_cond_words.to_csv("tmp/p" +str(pid)+ "_single" + ".csv")
            self.multi_cond_words.to_csv("tmp/p" +str(pid)+ "_multi" + ".csv")

    def read_data(self, pid):
        self.single_cond_words = pd.read_csv("tmp/p" +str(pid)+ "_single" + ".csv", header=None).iloc[:,1]
        self.multi_cond_words = pd.read_csv("tmp/p" +str(pid)+ "_multi" + ".csv", header=None).iloc[:,1]
        for i in range(1, self.days+1):
            data = pd.read_csv("data/p" +str(pid)+ "_subj_" + "_sess_"  + "_" +
            "day_" + str(i)+ ".csv")
            for j in range(1, self.blocks+1):
                blockdat = data[data['block']==j]
                blockdat=blockdat.reset_index(drop=True)
                self.data["day_" + str(i) + "_block_" + str(j)] = blockdat[["stim", "S"]]
                