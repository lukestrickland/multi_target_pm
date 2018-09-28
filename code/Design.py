from psychopy import visual, core, event
import numpy as np
import pandas as pd
import csv

#cheeky function to insert row into pandas data frame
def insert_row(idx, df, df_insert):
    return df.iloc[:idx, ].append(df_insert).append(df.iloc[idx:, ]).reset_index(drop = True)


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
                