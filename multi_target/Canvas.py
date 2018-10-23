''' Defining a canvas object which uses psychopy give me some basic visual stimulus functions to work with.
functions to load stimuli up and a function to show and record RT
'''
from psychopy import visual, core


class Canvas():

    def __init__(self, win):
        self.win = win
        self.stim_list = []
        self.clear()

    def text(self, text, height=None, wrapWidth=None):
        stim = visual.TextStim(win=self.win, text=text,
                               font="Arial", height=height, wrapWidth=wrapWidth)
        self.stim_list.append(stim)

    def rect(self, x, y, w, h):
        self.shapestim([[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
                       close=True)
        pos = [x, y]
        stim = visual.GratingStim(win=self.win, pos=pos,
                                  size=[w, h], color=self.win.color, tex=None,
                                  interpolate=False)
        self.stim_list.append(stim)

    def shapestim(self, vertices, fix_coor=True, close=False, fill=True):

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
        self.line(start=[-18, 0], end=[18, 0], lineWidth=7)
        self.line(start=[0, -18], end=[0, 18], lineWidth=7)
        self.show()

    def show(self):
        for stim in self.stim_list:
            stim.draw()
        self.win.flip(clearBuffer=True)
 #       return core.getTime()

    def clear(self):

        self.stim_list = []
        x, y = -self.win.size[0]/2, -self.win.size[1]/2
        self.rect(x, y, self.win.size[0], self.win.size[1])

    def close_display(self):
        self.win.close()
