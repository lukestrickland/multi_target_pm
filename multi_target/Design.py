import numpy as np
import pandas as pd
import csv
import random

# cheeky function to insert row into pandas data frame


def insert_row(idx, df, df_insert):
    return df.iloc[:idx, ].append(df_insert).append(df.iloc[idx:, ]).reset_index(drop=True)


'''Design object to create stimulus lists for each participant. On day 1,
 the during __init__ the Experiment object will run the design functions to 
 create the stimuli and save data files as csv. On day 2, the Experiment 
 object will run the read_data function to re-create the design as created on day 1.
'''


class Design():
    def __init__(self, stim_file, blocks, days):
        # Read in source stimuli
        self.stim = pd.read_csv(stim_file)[0:1352]
        # Create pandas dataframes so later words, non-words, PM can be inserted in
        # by index
        self.words = pd.DataFrame()
        self.nonwords = pd.DataFrame()
        self.pmtargets = pd.DataFrame()
        # Experiment design: how many days, how many blocks?
        self.days = days
        self.blocks = blocks
        # Create a data dictionary with the sames of each day and block
        self.data = {}
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
                # Define ranges to insert PM items into
                self.data["day_" + str(i) + "_block_" + str(j)] = 0

    # Shuffle each word and non-word stimuli separately
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

    # Will be called by the experiment object where participants are
    # assigned a response key for each resp. Creates a data frame of practice
    # stimuli that have a correct column (C) which contains the correct response
    def practice_stim(self, Wkey, Nkey, pid):
        pracstim = pd.read_csv("items/practice_stim.csv")
        pracwords = pracstim.loc[:, "Words"].to_frame()
        pracwords.rename(columns={'Words': 'stim'}, inplace=True)
        pracwords['S'] = "W"
        pracwords['C'] = Wkey
        pracnonwords = pracstim.loc[:, "Nonwords"].to_frame()
        pracnonwords.rename(columns={'Nonwords': 'stim'}, inplace=True)
        pracnonwords['S'] = "N"
        pracnonwords['C'] = Nkey
        pracstim = pracwords.append(pracnonwords)
        pracstim.to_csv("tmp/p" + str(pid) + "_practice" + ".csv", index=False)

    # shuffles word and non-word stimuli, collects PM words for both the single and multi target condition.
    # counterbalance is an array of the condition orders for day 1 and 2, e.g., np.array([["single", "multi"], ["multi", "single"]])
    def set_stim(self, counterbalance):
        self.initial_shuffle()
        # pull out PM items
        self.single_cond_words = self.shuffledstim.loc[0:1, "Words"]
        self.multi_cond_words = self.shuffledstim.loc[2:17, "Words"]
        # pull out nonPM items
        ongoing_task_items = self.shuffledstim.loc[18:1278]
        ongoing_task_items = ongoing_task_items.reset_index()
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
                # block_num is the block number counted from the start of the experiment day 1
                # through til the end of testing. E.g, if days have 2 blocks,
                # block 1 on day 2 would have a blocknum of 3
                block_num = (i-1) * self.blocks + j
                # grab the next 273 words
                words = ongoing_task_items.loc[block_num*273 -
                                               273:block_num*273 - 1, "Words"].values
                # grab the next 315 nonwords
                nonwords = ongoing_task_items.loc[block_num*315 -
                                                  315:block_num*315 - 1, "Nonwords"].values
                # either grab 48 single word targets
                if counterbalance[i-1, j-1] == "single":
                    pmtargets = [self.single_cond_words.values[i-1]] * 48
                else:
                    # or 6 * the 8 multi word targets 
                    pmtargets = []
                    for numreps in range(0,6):
                        pmtargets = pmtargets + random.sample(
                        self.multi_cond_words.values[(i-1)*8:(i*8)].tolist(), 8)
                pmtargets = np.array(pmtargets)
                # save all for each day and block
                self.pmtargets["day_" +
                               str(i) + "_block_" + str(j)] = pmtargets
                self.words["day_" + str(i) + "_block_" + str(j)] = words
                self.nonwords["day_" + str(i) + "_block_" + str(j)] = nonwords

    # The pm items need to be interspersed amongst the rest according to quite strict
    # criteria. Here I am putting them in every 13 trials starting from trial 4.
    # there is a break in the middle for participants to rest, so they also
    # don't get pm items for 3 trials after the break (which is why start = 321 when blocklength is 318)

    def set_pm_positions(self, minsep):
        tmp = pd.DataFrame()
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
                # Define ranges to insert PM items into
                starts = np.concatenate(
                    [np.linspace(start=3, stop=302, num=24),
                     np.linspace(start=321, stop=620, num=24)])

                stops = np.concatenate(
                    [np.linspace(start=15, stop=314, num=24),
                     np.linspace(start=333, stop=632, num=24)])
        #################

                pm_positions = []
                for k in range(0, len(starts)):
                    start = starts[k]
                    stop = stops[k]

                    if(k == 0):
                        last = -minsep
                    else:
                        last = pm_positions[k-1]
                    # if statement to make sure people dont get two
                    # pms within 5 trials of each other
                    if (last >= start-minsep):
                        start = last + (minsep+1)
                    position = np.random.random_integers(start, stop)
                    pm_positions.append(position)

                tmp["day_" + str(i) + "_block_" + str(j)] = pm_positions

        self.pm_positions = tmp
    #get the word and nonword stimuli for each block, shuffle them
    #together, assign to data
    def create_blocks(self, keybalance):
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
                word_df = pd.DataFrame(
                    self.words["day_" + str(i) + "_block_" + str(j)])
                word_df['S'] = "W"
                word_df['C'] = keybalance["word"]
                nonword_df = pd.DataFrame(
                    self.nonwords["day_" + str(i) + "_block_" + str(j)])
                nonword_df['S'] = "N"
                nonword_df['C'] = keybalance["nonword"]
                tmp = word_df.append(nonword_df)
                tmp.columns = ["stim", "S", "C"]
                self.data["day_" + str(i) + "_block_" + str(j)
                          ] = tmp.sample(frac=1).reset_index(drop=True)
    #insert PM items into data
    def insert_pm(self, counterbalance, keybalance):
        for i in range(1, self.days+1):
            for j in range(1, self.blocks+1):
                # Define ranges to insert PM items into
                target_list = self.pmtargets.loc[:,
                                                 "day_" + str(i) + "_block_" + str(j)].values
                pm_target = {"stim": self.single_cond_words[0], "S": [
                    "P"], "C": keybalance["pm"]}
                if counterbalance[i-1, j-1] == 'multi':
                    pm_target['stim'] = 'multi'
                pm_target = pd.DataFrame(pm_target)[["stim", "S", "C"]]
                pm_positions = self.pm_positions.loc[:,
                                                     "day_" + str(i) + "_block_" + str(j)].values
                thisblock_stim = self.data["day_" +
                                           str(i) + "_block_" + str(j)]
                thisblock_stim.columns = ["stim", "S", "C"]
                #almost sure there's a one liner way to do the below
                l = 0
                for position in pm_positions:
                    pm_target.values[0, 0] = target_list[l]
                    thisblock_stim = insert_row(
                        position, thisblock_stim, pm_target)
                    l += 1

                self.data["day_" + str(i) + "_block_" +
                          str(j)] = thisblock_stim
    #write a bunch of data files containing all the 
    #stimulus information etc (day 1)
    def setup_data(self, pid, counterbalance):
        for i in range(1, self.days+1):
            day_dats = pd.DataFrame()
            for j in range(1, self.blocks+1):
                data = self.data["day_" + str(i) + "_block_" + str(j)].copy()
                data['RT'] = -1
                data['R'] = -1
                data['prestim_R'] = -1
                data['block'] = j
                data['day'] = i
                data['cond'] = counterbalance[i-1, j-1]
                if j == 1:
                    day_dats = data
                else:
                    day_dats = day_dats.append(data, ignore_index=True)
            day_dats.to_csv("data/p" + str(pid) + "_day_" + str(i) + ".csv")
            self.single_cond_words.to_csv(
                "tmp/p" + str(pid) + "_single" + ".csv")
            self.multi_cond_words.to_csv(
                "tmp/p" + str(pid) + "_multi" + ".csv")
    #read the data backup (day 2)
    def read_data(self, pid):
        self.single_cond_words = pd.read_csv(
            "tmp/p" + str(pid) + "_single" + ".csv", header=None).iloc[:, 1]
        self.multi_cond_words = pd.read_csv(
            "tmp/p" + str(pid) + "_multi" + ".csv", header=None).iloc[:, 1]
        for i in range(1, self.days+1):
            data = pd.read_csv("data/p" + str(pid) + "_day_" + str(i) + ".csv")
            for j in range(1, self.blocks+1):
                blockdat = data[data['block'] == j]
                blockdat = blockdat.reset_index(drop=True)
                self.data["day_" + str(i) + "_block_" +
                          str(j)] = blockdat[["stim", "S", "C"]]
