import os.path
import pandas as pd

def launch():
    while True:
        participantid = int(raw_input("Please enter participant id: "))
        day = int(raw_input("Please enter session number: "))
        already_file = os.path.isfile(("data/p" + str(participantid) + "_day_" + str(1) + ".csv")) 
        if(already_file and day ==1):
            confirm_overwrite = raw_input(("Warning! You already initialised this participant (ran day 1)."
            " If you proceed, previous data will be overwritten. Enter 'y' to continue, or 'n' to change details: "))
            print(confirm_overwrite)
            if confirm_overwrite=='y\r' or confirm_overwrite=='y':
                break
        elif(already_file and day ==2):
            day_2 = pd.read_csv("data/p" + str(participantid) + "_day_" + str(2) + ".csv")
            no_data = day_2.loc[0,"RT"]==-1
            if(no_data):
                break
            confirm_overwrite = raw_input(("Warning! There is already data saved for day 2 for this participant. "
            "If you proceed, previous data will be overwritten. Enter 'y' to continue, or 'n' to change details: "))
            if confirm_overwrite=='y\r' or confirm_overwrite=='y':
                break        
        else: 
            break
    return participantid, day