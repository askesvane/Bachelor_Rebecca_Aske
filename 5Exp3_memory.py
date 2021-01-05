# Cognitive Arhaeology Study
# Experiment 3
# August-2020s

# Import packages
from psychopy import visual, core, event, gui, data
import pandas as pd
import numpy as np
import random # from numpy.random
import math, os, glob
from PIL import Image

# gui requesting participant info
myDlg = gui.Dlg(title="CogAch Cultural Traditions Experiment") 
myDlg.addText('Subject Info')
myDlg.addField('Subject number:')
myDlg.addField('Age:')
myDlg.addField('Gender:', choices=['female', 'male', 'other'])
myDlg.show()

## popup box
#saves data from dialogue box into variables
if myDlg.OK:
    ID = myDlg.data[0]
    age = myDlg.data[1]
    gender = myDlg.data[2]

# define panda DF for logging
columns = ['ID', 'age', 'chain', 'gender', 'drawing', 'generation', 'line', 'x_pos', 'y_pos', 'orientation', 'reaction_time']
index = np.arange(0)
DATA = pd.DataFrame(columns=columns, index = index) 

# logfile and screenshot directories
if not os.path.exists('logfiles'):
    os.makedirs('logfiles')
logfile_path = 'logfiles/'

if not os.path.exists('screenshots'):
    os.makedirs('screenshots')
screenshot_path = 'screenshots/'

# define timestamp object
date = data.getDateStr()  

# logfile name
logfile_name = "logfiles/logfile_{}_{}.csv".format(ID, date)


##define functions ##
# define stopwatch
stopwatch = core.Clock()

# define window
win = visual.Window(fullscr=True, color='LightGrey', colorSpace='rgb', allowStencil=True, units = 'pix')

# define white drawing space and wait text
drawing_space = visual.Rect(win, pos=(0,0),width=280, height=280, fillColor='white', units = 'pix')
wait_text = visual.TextStim(win, color = "black", text ='Wait', height = 30)

# define pi from radians/degress
if math.sin(90) == 1:
    pi = 180
    pi2 = 360
else:
    pi = math.pi
    pi2 = pi*2

# Flip-text function
def msg(txt):
    instructions = visual.TextStim(win, text=txt, height = 20, color = 'black')
    instructions.draw()
    win.flip()
    event.waitKeys(keyList = ['space', 'escape'])

def blank(time):
    grey = visual.TextStim(win, text='', color = 'black')
    grey.draw()
    win.flip()
    core.wait(time)

def show_stim(stimulus):
    drawing_space.draw()
    image = visual.ImageStim(win, stimulus)
    image.draw() #do the drawing
    win.flip()
    core.wait(3) #show for three seconds

    wait_text.draw()
    win.flip()
    core.wait(2) #wait for 2 seconds

def draw_all():
    drawing_space.draw()
    fixSpot.draw()
    for line in LINES:
        line.draw()
    win.flip()

def trial_function(stimulus, save):
    global LINES
    global DATA
    # draw lines
    for i in range(len(LINES)):
        
        
        while True: 
            #handle key presses each frame
            for key in event.getKeys():
                if key in ['escape']:
                    DATA.to_csv(logfile_name)
                    core.quit()
                    
            #get line positions as the mouse positions
            mouse_dX, mouse_dY = mouse.getRel()
            fixSpot.setPos(mouse.getPos())
            
            #set line orientation to be the same as the mouse wheel
            wheel_dX, wheel_dY = mouse.getWheelRel()
            fixSpot.ori += wheel_dY * 4
        
            #do the drawing
            draw_all()
                        
            if mouse.getPressed()[0]:  # if button is pressed, line is put where the mouse is with the same orientation
                mouse.clickReset()
                #x, y = mouse.getPos()
                LINES[i].image = "line1.png"
                LINES[i].pos = fixSpot.pos # [x,y]
                LINES[i].ori = fixSpot.ori
                
                key = event.waitKeys(keyList=['space','z'])[0]
                
                if key == 'space':
                    # give the orientation give us a number between 0-pi (aka 0 and 180 degrees)
                    r = int(fixSpot.ori/pi2)
                    R = fixSpot.ori - (r*pi2)
                    R = abs(R)
                    if R > pi:
                        R = R - pi2
                    R = abs(R)
                    
                    # get time
                    reaction_time = stopwatch.getTime()
                    # gets the watch from 0 again
                    stopwatch.reset()
                    #divide the positions into x coordinates and y coordinates
                    x_pos = LINES[i].pos[0]
                    y_pos = LINES[i].pos[1]
                    # get generation
                    generation = stimulus[17:18]
                    chain = stimulus[13:15]
                    line = 'line{}'.format(i+1)
                    
                    nameForScreenshot = stimulus[8:-4]
                    #print(nameForScreenshot)
                    
                    #append real data to pandas 
                    if save == 1:
                        DATA = DATA.append({
                        'ID': ID,
                        'age': age,
                        'chain': chain,
                        'gender': gender,
                        'drawing': stimulus[8:-4],
                        'generation': generation,
                        'line': line,
                        'x_pos': x_pos,
                        'y_pos': y_pos,
                        'orientation': R,
                        'reaction_time': reaction_time}, ignore_index=True)
                    fixSpot.ori = 0 
                    
                    break
                # make it possible to regret the placement of a line by pressing 'z' 
                elif key == 'z':
                    LINES[i].image = None
                    fixSpot.setPos(mouse.getPos())
                
    #take a screenshot of the result and save it
    if save == 1:
        screenshot_name = screenshot_path + "screenshot_id{}_{}_{}.png".format(ID,nameForScreenshot,date)
        win.getMovieFrame(buffer='front')
        win.saveMovieFrames(screenshot_name)
        # open and crop image 
        win.flip()
        core.wait(1)
        im = Image.open(screenshot_name)
        x = im.size[0]
        y = im.size[1]
        right = (x/2)-280 
        top = (y/2)-280
        left = (x/2)+280
        bottom = (y/2)+280
        im2 = im.crop((right,top,left,bottom))
        gray = im2.convert('L')
        bw = gray.point(lambda x: 0 if x<217 else 255, '1')
        bw.save(screenshot_name)
    
    for j in LINES:
        j.image = None
        j.pos = [900,900]
    
    blank(1)


####### Prepare stimuli #########
# basic stimulus where we define THE LINE
fixSpot = visual.ImageStim(win, image="line1.png")
mouse = event.Mouse()
x, y = [None, None]

# The 6 LINES to be drawn
line1 = visual.ImageStim(win, pos = [900,900])
line2 = visual.ImageStim(win, pos = [900,900])
line3 = visual.ImageStim(win, pos = [900,900])
line4 = visual.ImageStim(win, pos = [900,900])
line5 = visual.ImageStim(win, pos = [900,900])
line6 = visual.ImageStim(win, pos = [900,900])
LINES = [line1, line2, line3, line4, line5, line6]

# GET STIMULI IMAGES
# set path
# import file with partipant and chains matched 
df = pd.read_csv('chain_participant.csv', sep =';')

# making a path glob glob can read to import correct stimuli: 
#Based on ID .iat extracts the right chain. Glob glob extracts generation 1, 4 and 8
id = int(ID)
path = 'stimuli/'
correct_path1 = glob.glob(path + '*c{}**{}*.png'.format(df.iat[id - 1, 1],'g[148]'))
correct_path2 = glob.glob(path + '*c{}**{}*.png'.format(df.iat[id - 1, 2],'g[148]'))
stimuli = correct_path1 + correct_path2



random.shuffle(stimuli)


# image for practice round
practice = 'practice_trial.png'


########## INSTRUCTIONS ###############
instruction1 = '''
THANK YOU FOR PARTICIPATING IN OUR EXPERIMENT!\n\nIn this experiment,\
you are going to be presented with different line patterns made up of six lines. Your task \
is to try to copy them with the mouse as well as you can. Each image will be presented to you for three seconds, after which there will be a two seconds pause. \
Afterwards, you have to copy it from your memory by placing lines one-by-one using the mouse.\n\n\n Press SPACE to continue.'''

instruction2 = '''You can \
move the lines in the following way:\n\nBy moving the mouse across the screen, you can choose the location of each line. \
\n\nBy scrolling the mouse, you can rotate the line to the orientation you want.\n\nOnce you have the location and angle you want, \
click the mouse and the line will be placed. Afterwards, \
press SPACE and a new line will come. Then, the same procedure repeats until you placed all six lines.\n\n\n Press SPACE to continue.'''

instruction3 = '''Be aware: You can regret the placement of the last line by pressing the 'z' key. That will allow you move it to a new position. \
But once you have pressed 'space' and the next line appears, you cannot change the previous one anymore.\n\n\n Press SPACE to continue.
'''
practice_text = '''\n\nYou \
will first have a practice trial. Afterwards, the experiment will begin.\n\nPress SPACE to start with the practice trial'''

experiment_start = '''\n\nNow the experiment will start. Press SPACE to begin!'''

goodbye ='''The experiment is now over.\n\nThank you for your participation.'''


########### RUN EXPERIMENT ##############

# intro info
msg(instruction1)
msg(instruction2)
msg(instruction3)
msg(practice_text)

# trial round
show_stim(path + practice)
trial_function(practice, 0)

# Real experiment
msg(experiment_start)

for stimulus in stimuli:
    show_stim(stimulus)
    trial_function(stimulus, 1)

DATA.to_csv(logfile_name)

msg(goodbye)




