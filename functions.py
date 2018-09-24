from glob import glob
from sets import Set
    
def finish():
    import pygame, sys
    pygame.quit()
    sys.exit()
    
def get_filename(subject,session):
    return 'subj.'+str(subject)+'-sess.'+str(session)+'.dat'
    
def suggest_subject():
    ''' Suggests a subject number based on existing data files
        If no data files are found, suggets 1
        If data files are found, suggests the lowest value that is not already used
    '''
    x = glob("data/subj*.dat")
    subjects = Set()    
    for s in x:    
        subjects.add(int(s.split('subj.')[1][0]))    
    if (len(subjects)==0):
        return 1
    for i in range(1,max(subjects)):
        if i not in subjects:
            return i
    return max(subjects)+1

def get_subject_list():
    ''' returns set of subject numbers based on existing data files '''
    data_files = glob("data/subj*.dat")
    res = Set()    
    for s in data_files:    
        res.add(int(s.split('subj.')[1][0]))
    return res

def subject_exists(n):
    ''' checks to see if subject number is already used in data files'''
    subjects = get_subject_list()
    return (n in subjects)
    
def get_number(msg):    
    while True:
        n = raw_input(msg + "> ")
        if n.isdigit():
            return int(n)
        else:
            print "Not a valid number."

def get_subject():
    res = get_number("Enter Subject Number ("+str(suggest_subject())+")")
    return res

def get_session():
    res = get_number("Enter Session Number")
    return res

# def show_instructions(cond):
#     if (cond=='SESS'):
#         print "SESSION INSTRUCTIONS"
#     if (cond=='PRAC'):
#         print "PRACTICE INSTRUCTIONS"
#     elif (cond=='LF'):
#         print "LF INSTRUCTIONS"
#     elif (cond=='HF'):
#         print "HF INSTRUCTIONS"
#     elif (cond=='CON'):
#         print "CON INSTRUCTIONS"
#     elif (cond=='DIS'):
#         print"DISTRACTOR INSTRUCTIONS"

def end_of_data(indx,ln):                
    return indx >= (ln-1)  
    
def current_block(indx,data):
    return data[indx].split('\t')[1]   

def current_trial(indx,data):
    return data[indx].split('\t')

def next_trial(indx):
    return indx + 1
    
def end_of_block(indx,data):
    if end_of_data(indx,len(data)) or (data[indx].split('\t')[0] != data[indx+1].split('\t')[0]):
        return True
    else:
        return False
    
def end_of_condition(indx,data):
    if end_of_data(indx,len(data)) or (data[indx].split('\t')[1] != data[indx+1].split('\t')[1]):
        return True
    else:
        return False

def load_data(subject,session):
    fn = get_filename(subject, session)    
    fp = open('data/'+fn,"r").read().split('\n')
    data = list(filter(None, fp))
    header = '\n'.join(data[:6])
    del data[:6]    
    return header,data

def save_data(subject,session,header,data):
    fn = get_filename(subject,session)
    fp = open('data/'+fn,'w')
    fp.write(header+'\n')
    for dat in data:
        fp.write(dat+'\n')
    fp.close()