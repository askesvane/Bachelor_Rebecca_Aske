# Cognitive Arhaeology Study
# Experiment 2
# August-2020s

# Import packages
from psychopy import visual, core, event, gui, data
import pandas as pd
import numpy as np
from numpy.random import random, randint, normal, shuffle 
import ast, csv, glob, random, os
from itertools import combinations

date = data.getDateStr()

# gui requesting participant info
myDlg = gui.Dlg(title="CogAch Intentionality Experiment") 
myDlg.addText('Subject Info')
myDlg.addField('Participant ID:')
myDlg.addField('Age:')
myDlg.addField('Gender:', choices=['female', 'male', 'other'])
myDlg.show()

## popup box ##
#saves data from dialogue box into variables
if myDlg.OK:
    ID = myDlg.data[0]
    age = myDlg.data[1]
    gender = myDlg.data[2]
else:
    core.quit()

# define panda DF for logging
columns = ['ID', 'age', 'gender', 'left', 'right', 'responseL', 'responseR', 'generationL', 'generationR','chainL', 'chainR', 'chainPair','reaction_time']
index = np.arange(0)
DATA = pd.DataFrame(columns=columns, index = index)

# logfile directory
if not os.path.exists('logfiles'):
    os.makedirs('logfiles')
logfile_path = 'logfiles/'

# define window
win = visual.Window(fullscr=True, color = 'White', units = 'height') 

# define stopwatch
stopwatch = core.Clock()

#makes mouse invisible
mouse = event.Mouse()
win.mouseVisible = False

##define functions ##
# Fixation cross
def fixation(t):
    fixation = visual.TextStim(win, text = '+', color = 'black', height = 0.06)
    fixation.draw()
    win.flip()
    core.wait(t)

# Flip-text function
def msg(txt):
    instructions = visual.TextStim(win, text=txt, height = 0.025, color = 'black')
    instructions.draw()
    win.flip()
    event.waitKeys(keyList = ['space', 'escape'])

def practice(txt):
    stim1 = visual.ImageStim(win, image = 'stimuli/Original stimuli/Old_2_a.png', pos = [-0.3, 0.1]) 
    stim2 = visual.ImageStim(win, image = 'stimuli/Original stimuli/Recent_4_a.png', pos = [0.3, 0.1]) 
    txt = visual.TextStim(win, text = txt, pos = [0,-0.2], color = 'black', height = 0.025)
    stim1.draw()
    stim2.draw()
    txt.draw()
    win.flip()
    event.waitKeys(keyList = ['left', 'right', 'escape'])

## prepare stimuli ##
# GET STIMULI IMAGES
# set path
path = '/Users/rebeccakjeldsen/Dropbox/Bachelor - Aske og Rebecca/Study material/experiment2/'
# import file with partipant and chains matched 
df = pd.read_csv('chain_participant.csv', sep =';')

# making a path glob glob can read to import correct stimuli: 
#Based on ID .iat extracts the right chain. Glob glob extracts generation 1, 4 and 8
id = int(ID)
correct_path1 = 'stimuli/*c{}*{}*.png'.format(df.iat[id - 1, 1], 'g[148]') 
correct_path2 = 'stimuli/*c{}*{}*.png'.format(df.iat[id - 1, 2], 'g[148]') 
stimuli1 = glob.glob(correct_path1) 
stimuli2 = glob.glob(correct_path2) 
stimuli = stimuli1 + stimuli2

# combine and randomize
STIM_COMBI = list(combinations(stimuli, 2))
random.shuffle(STIM_COMBI)

# Extract information
trial_list = []
for stimulus in STIM_COMBI:
    trial_list += [{
        'right': stimulus[0], # whats on the left
        'left': stimulus[1], #whats on the right
        'generationR': stimulus[0][17:18],
        'generationL': stimulus[1][17:18],
        'chainR': stimulus[0][13:15],
        'chainL': stimulus[1][13:15]
        }]


## text ##
welcome = '''
Welcome to the experiment!
Press SPACE to continue.
'''

intro = '''
This experiment will address the apparent intentionality of different engravings.
In each trial, you will be presented with two images of engravings. You must evaluate which one of those two you find more likely to be purposely made by a human.
If you think the image to the LEFT is more likely to have been purposefully made by a human, you must press the LEFT key.
If you think the image to the RIGHT is more likely to have been purposefully made by a human, you must press the RIGHT key.

Press SPACE to continue.
'''

prac = '''
Before we start the experiment, you will be presented to a test trial. 
Press SPACE when you are ready!
'''

duringprac = ''' 
Select the image you find most likely
   to be purposely made by a human.
Use either LEFT or RIGHT key to respond.
'''

afterprac = '''
Well done. Now you will continue with the real experiment. 
Press SPACE when you are ready!
'''

pause = '''
Time for a break. Press SPACE when you are ready to proceed. 
'''

outro = '''
The experiment is now over. Thank you for participating!
'''

## run experiment ##
# trial counter
count = 1

# the experiment
msg(welcome)
msg(intro)
msg(prac)
practice(duringprac)
msg(afterprac)

for trial in trial_list:
    if count in [70, 140, 210]:
        msg(pause)
    stopwatch.reset()
    
    stim1 =visual.ImageStim(win, image = trial ['right'], pos = [0.3, 0])
    stim2 =visual.ImageStim(win, image = trial ['left'], pos = [-0.3, 0])
    
    stim1.draw()
    stim2.draw()
    win.flip()
    
    key = event.waitKeys(keyList = ['right', 'left', 'escape'])
    if key[0] == 'left':
        reaction_time = stopwatch.getTime()
        responseL = 1
        responseR = 0
    elif key[0] == 'right':
        reaction_time = stopwatch.getTime()
        responseL = 0
        responseR = 1
    elif key[0] == 'escape':
        logfilename = 'logfiles/logfile_{}_{}.csv'.format(ID,date)
        DATA.to_csv(logfilename)
        core.quit()
        
    #append trial data to pandas
    DATA = DATA.append({
        'ID': ID,
        'age': age,
        'gender': gender,
        'left': trial['left'][8:-4],
        'right': trial['right'][8:-4],
        'responseL': responseL,
        'responseR': responseR,
        'generationR': trial['generationR'],
        'generationL': trial['generationL'],
        'chainR': trial['chainR'],
        'chainL': trial['chainL'],
        'chainPair': df.iat[id - 1, 3],
        'reaction_time': reaction_time}, ignore_index=True)
    count +=1
    fixation(0.3)

#save to csv file - put this in the end of the script 
logfilename = 'logfiles/logfile_{}_{}.csv'.format(ID,date)
DATA.to_csv(logfilename)

msg(outro)
