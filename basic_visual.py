#import pip
#pip.main(['install', 'python-pygaze'])
from psychopy import visual, core, event
from pygaze import libscreen
from pygaze import libtime
from pygaze import liblog
from pygaze import libinput
from pygaze.eyetracker import EyeTracker
from pygaze import settings
import constants
from pygaze.display import Display
import pygaze
import math
import time
import csv

class Experiment():
    def __init__(self, canvas, tracker, subject_nr):
        self.canvas = canvas
        self.tracker = tracker
        self.staircase= 0.2
        

    def wait_for_gaze(self):
        start= core.getTime()
        while True:
            gx, gy = self.tracker.sample()
            if gx<1152 and gx > 768:
                end = core.getTime()
                break
            gx = math.floor(gx - 960)
            gy = math.floor(gy - 540)   
            self.canvas.clear()
            self.canvas.circle(pos=[-384, 0], radius=71)
            self.canvas.circle(pos=[384, 0], radius=71)
            self.canvas.circle(pos=[gx, -gy], radius=71)
            self.canvas.show()

    def pre_stimulus(self, duration):
        start= core.getTime()
        while True:
            gx, gy = self.tracker.sample()
            if gx>1152 or gx < 768:
                end = core.getTime()
                preempt = True
                break
            gx = math.floor(gx - 960)
            gy = math.floor(gy - 540)   
            self.canvas.clear()
            self.canvas.line(start=[-15, 0], end=[15, 0], lineWidth=5)
            self.canvas.line(start=[0, -15], end=[0, 15], lineWidth=5)
            self.canvas.circle(pos=[-384, 0], radius=71)
            self.canvas.circle(pos=[384, 0], radius=71)
            self.canvas.circle(pos=[gx, -gy], radius=71)
            self.canvas.show()
            elapsed = core.getTime() - start
            if elapsed > duration:
                break


    def core_trial(self, trialtype, stop):
        start= core.getTime()
        while True:
            gx, gy = self.tracker.sample()
            if gx>1152 or gx < 768:
                end = core.getTime()
                if (gx<768):
                     choice = "left"
                if (gx>1154):
                     choice = "right"  
                break
            elapsed = core.getTime() - start
            gx = math.floor(gx - 960)
            gy = math.floor(gy - 540)   
            self.canvas.clear()
            self.canvas.line(start=[-15, 0], end=[15, 0], lineWidth=5)
            self.canvas.line(start=[0, -15], end=[0, 15], lineWidth=5)
            if (trialtype=="left"):
                self.canvas.circle(pos=[-20, 20], radius=15)
            if (trialtype=="right"):
                self.canvas.circle(pos=[20, 20], radius=15)  
            if (stop and elapsed > self.staircase):
                if (trialtype=="left"):
                    self.canvas.circle(pos=[-20, -20], radius=15)
                if(trialtype=="right"):
                    self.canvas.circle(pos=[20, -20], radius=15)    
            self.canvas.circle(pos=[-384, 0], radius=71)
            self.canvas.circle(pos=[384, 0], radius=71)
            self.canvas.circle(pos=[gx, -gy], radius=71)
            self.canvas.show()
            if (elapsed>2):
                end= core.getTime()
                choice = "None"
                break
        RT = end - start
        self.canvas.clear()
        self.canvas.text(str(RT))
        self.canvas.show()
        core.wait(2)
        return RT, choice
        
    def trial(self, blankduration, trialtype, stop):
        self.wait_for_gaze()
        self.pre_stimulus(blankduration)
        return self.core_trial(trialtype, stop)

    def block(self, trials, stops):
        RTs = []
        choices = []
        ntrials=len(trials)
        for i in range(0,ntrials):
            RT, choice = self.trial(1, trials[i], stops[i])
            RTs.append(RT)
            choices.append(choice)
            print(choice)
            if (stops[i]==1):
                if(choice=="None"):
                    self.staircase = self.staircase + .020
                else:
                    self.staircase = self.staircase - .020
            core.wait(1)
            if event.getKeys(['escape']):
                self.canvas.win.close()
                core.quit()
        return (RTs, choices)


class Design():
    def __init__(self, trials_file, subject_nr):
        self.trials_file = trials_file
        self.stop_trials = self.get_trials()
        self.dot = subject_nr % 2
        
    def get_trials(self):
        with open(self.trials_file, 'rb') as f:
            reader = csv.reader(f)
            headers = reader.next()
            column = {h:[] for h in headers}
            for row in reader:
             for h, v in zip(headers, row):
                column[h].append(v) 
        column['stop'] = map(int, column['stop'])
        return column

   


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

    def shapestim(self, vertices, fix_coor=True, close=False, fill= True):

        if fill:
            fill_color = self.win.color
        stim = visual.ShapeStim(self.win,
                                vertices=vertices,
                                lineColor=self.win.color, closeShape=close,
                                fillColor=fill_color, interpolate=False)
        self.stim_list.append(stim)

    def rect(self, x, y, w, h):
        self.shapestim([[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
                           close=True)
        pos = [x,y]
        stim = visual.GratingStim(win=self.win, pos=pos,
                                  size=[w, h], color=self.win.color, tex=None,
                                  interpolate=False)
        self.stim_list.append(stim)

    def circle(self, radius, pos):
        stim= visual.Circle(self.win, radius=radius, edges=32, pos=pos)
        self.stim_list.append(stim)

    def line(self, start, end, lineWidth):
        stim = visual.Line(self.win, start=start, end=end, lineWidth=lineWidth)
        self.stim_list.append(stim)

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




