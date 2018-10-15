from psychopy import core, event

# generates some of the lengthier task instructions.


class Instructions():
    def __init__(self, responsekey_list, todays_multi, todays_single):
        # needs the responsekey_list like experiment, and also
        # the names of the PM targets
        self.responsekeys = responsekey_list
        self.OThand = 'LEFT'
        if self.responsekeys["word"] == 'j' or self.responsekeys["word"] == 'k':
            self.OThand = 'RIGHT'
        self.todays_multi = todays_multi
        self.todays_single = todays_single

    def block_instructions(self, btype):
        keyhands = (".\n\nPlease place the middle finger of your LEFT hand on the 's' key and the index finger of your LEFT hand on the 'd' key." +
                    " Please make your lexical decision responses from this position.\n\n" + "Please locate the 'j' key now. During the next block of trials," +
                    " please rest the index finger of your RIGHT hand here, ")
        if self.OThand == "RIGHT":
            keyhands = (".\n\nPlease place the middle finger of your RIGHT hand on the 'k' key and the index finger of your RIGHT hand on the 'j' key." +
                        " Please make your lexical decision responses from this position.\n\n" +
                        "Please locate the 'd' key now. During the next block of trials, please rest the index finger of your LEFT hand here, ")

        if(btype == 'multi'):
            instruction1 = ("We have an interest in your ability to remember to perform actions in the future. \n\n" +
                            "During the next block of lexical decision trials, we would like you to make an alternative response to certain target words.\n\n" +
                            " We will now present you the target words to memorize.")

            instruction2 = ("You have two minutes to memorize the following target words: \n\n" +
                            ' '.join(self.todays_multi.values.flatten()) +
                            "\n\n Once you have tried to memorize the target words, we will test you.")

            instruction3 = ("We will now test your memory. \n\n" +
                            " You will be presented words one by one. Press the 'y' key if the word is on this list, otherwise press the 'n' key. \n\n" +
                            " We wish to train you to 100% accuracy. Thus, you will continue to be tested until you can perfectly recognise the target words. \n\n" +
                            "Press space to begin.")

            instruction4 = ("Here are the target words that you just memorized: \n\n" +
                            ' '.join(self.todays_multi.values.flatten()) +
                            " \n\n When you are presented any of these words during the the next block of lexical decision trials, we would like you to press '" +
                            self.responsekeys['pm']+"' INSTEAD of '" + self.responsekeys['word'] + "'"+
                            keyhands + "and use it to make your response if you see an item from your target list.\n\n " +
                            "Please speak with the experimenter about your instructions.")

        elif(btype == 'single'):
            instruction1 = ("We have an interest in your ability to remember to perform actions in the future. \n\n" +
                            "During the next block of lexical decision trials, we would like you to make an alternative response to a target word.\n\n" +
                            " We will now present you the target word to memorize.")

            instruction2 = ("You have two minutes to memorize the following target word: \n\n" +
                            ' '.join(self.todays_single.values.flatten()) +
                            "\n\n Once you have tried to memorize the target word, we will test you.")

            instruction3 = ("We will now test your memory. \n\n" +
                            " You will be presented words one by one. Press the 'y' key for your target word, otherwise press the 'n' key. \n\n" +
                            " We wish to train you to 100% accuracy. Thus, you will continue to be tested until you can perfectly recognise the target words \n\n" +
                            "Press space to begin.")

            instruction4 = ("Here is the target word that you just memorized: \n\n" +
                            ' '.join(self.todays_single.values.flatten()) +
                            " \n\n When you are presented this word during the the next block of lexical decision trials, we would like you to press '" +
                            self.responsekeys['pm']+"' INSTEAD of '" + self.responsekeys['word'] + "'"+
                            keyhands + "and use it to make your response if you see your target word.\n\n " +
                            "Please speak with the experimenter about your instructions.")

        return instruction1, instruction2, instruction3, instruction4

    def practice_instructions(self):
        keyhands = "\n\nPlease place the middle finger of your LEFT hand on the 's' key and the index finger of your LEFT hand on the 'd' key. Please make your lexical decision responses from this position."
        if self.OThand == "RIGHT":
            keyhands = "\n\nPlease place the middle finger of your RIGHT hand on the 'k' key and the index finger of your RIGHT hand on the 'j' key. Please make your lexical decision responses from this position."

        instructions = ("Welcome to the experiment. You will perform a lexical decision task, in which you must decide whether strings of letters are" +
                        " words or non-words.\n\n Each trial begins with a fixation cross which appears on the screen for a short time, followed by a string of lower case letters." +
                        " Once each item is presented you must indicate with a keypress whether or not the string of letters forms an English word.  Please answer as ACCURATELY,  but as QUICKLY as you can.\n\n" +
                        "Locate the '" + self.responsekeys['word'] + "' key.  When the string appears press the '" + self.responsekeys['word'] + "' key if the string is an English word.\n\n" +
                        "Locate the '" + self.responsekeys['nonword'] + "' key.  When the string appears press the '" + self.responsekeys['nonword'] + "' key if the string is NOT an English word." +
                        keyhands +
                        "\n\n You will now perform some practice trials. Press space to begin."
                        )
        return instructions
