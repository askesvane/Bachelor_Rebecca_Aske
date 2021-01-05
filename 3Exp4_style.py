# style try

# Import modules
from psychopy import visual, core, event, gui, data
import pandas as pd
import numpy as np
import glob, os, random 
from itertools import combinations
import itertools

### create dialogue box for time entry
myDlg = gui.Dlg(title="CogAch Cultural Traditions Experiment") 
myDlg.addText('Subject Info')
myDlg.addField('Participant ID:')
myDlg.addField('Age:')
myDlg.addField('Gender:', choices=['female', 'male', 'other'])
myDlg.show()
if myDlg.OK:
    ID = myDlg.data[0]
    age = myDlg.data[1]
    gender = myDlg.data[2]
else:
    core.quit()

# define win object
win = visual.Window(fullscr=True, color = 'white', units = 'height')#, units = 'pix', allowStencil=True) # defines a window

# define timestamp object
date = data.getDateStr()  

# define clock object
stopwatch = core.Clock()

mouse = event.Mouse()
win.mouseVisible = False

# define pandas data frame for logging 
columns = ['ID', 'age', 'gender', 'trial', 'generation', 'target', 'competitor1', 'competitor2', 'response','correct','reaction_time']
DATA = pd.DataFrame(columns=columns)
# changed period to be generation (1,4,8)

# logfile directory
if not os.path.exists('logfiles'):
    os.makedirs('logfiles')
logfile_path = 'logfiles/'

# logfile name
logfile_name = "logfiles/logfile_{}_{}.csv".format(ID, date)

############ DEFINE FUNCTIONS ###################
# import file with partipant and chains matched 
df = pd.read_csv('chain_participant.csv', sep =';')
id = int(ID)

# save the variables to use in prepare stim function
chainA = df.iat[id - 1, 1]
chainB = df.iat[id - 1, 2]


def prepare_stim(stimuli, path_idx):
    STIMULI = []
    for stimulus in stimuli: 
        period = stimulus[17:18] # point to the generation 
        chain = int(stimulus[12:15])
        if int(chainA) == chain:
            site = 'blombos' # chainA
        elif int(chainB) == chain:
            site = 'diepkloof' # chain B
        STIMULI += [{
            'file': stimulus,
            'stimulus': stimulus[path_idx:-4], 
            'period': period, # generation
            'site': site}] # = chain
    return STIMULI

def prepare_trials(blombos, diepkloof):
    period_list = []
    for i in range(len(blombos)):
        B = np.delete(blombos,i)
        random.shuffle(diepkloof)
        for j in B:
            for k in diepkloof[0:-1]: # so target and competitor wont be identical
                period_list +=[{
                'target': blombos[i], 
                'competitor1': j,
                'competitor2': k
                }]
    random.shuffle(period_list)
    return period_list

def prepare_trial_list(STIMULI): 
    PERIOD = ['1', '4', '8']
    trial_list = []
    for period in PERIOD:
        blombos = list(item for item in STIMULI if item['period'] == period and item['site'] == 'blombos')
        diepkloof = list(item for item in STIMULI if item['period'] == period and item['site'] == 'diepkloof')
        trials = prepare_trials(blombos, diepkloof)
        trial_list += trials
        trials = prepare_trials(diepkloof, blombos)
        trial_list += trials
    random.shuffle(trial_list)
    return trial_list

def msg(txt):
    instructions = visual.TextStim(win, text=txt, color = 'black', height = 0.02)
    instructions.draw() 
    win.flip()
    event.waitKeys(keyList = ['space', 'escape'])

def fixation(t):
    fixation = visual.TextStim(win, text = '+', color = 'black', height = 0.07)
    fixation.draw()
    win.flip()
    core.wait(t)

def show_trial(trial):
    if random.sample([True, False],1)[0]:
        left = trial['competitor1']
        right = trial['competitor2']
    else:
        right = trial['competitor1']
        left = trial['competitor2']
    stim1 = visual.ImageStim(win, image = left['file'], pos = [-0.3, 0.15]) 
    stim2 = visual.ImageStim(win, image = right['file'], pos = [0.3, 0.15]) 
    stim3 = visual.ImageStim(win, image = trial['target']['file'], pos = [0, -0.15]) 
    stim1.draw()
    stim2.draw()
    stim3.draw()
    win.flip()
    return left, right

def practice():
    stim1 = visual.ImageStim(win, image = path+ 'i1_c101_g1_.png', pos = [-0.3, 0.25], size = 0.2) 
    stim2 = visual.ImageStim(win, image = path+'i1_c101_g4_id14.png', pos = [0.3, 0.25], size = 0.2) 
    stim3 = visual.ImageStim(win, image = path+'i1_c101_g8_id314.png', pos = [0, -0.05], size = 0.2) 
    txt = visual.TextStim(win, text = instruction2, pos = [0,-0.3], color = 'black', height = 0.02)
    stim1.draw()
    stim2.draw()
    stim3.draw()
    txt.draw()
    win.flip()
    event.waitKeys(keyList = ['left', 'right', 'escape'])

############## PREPARE STIMULI #####################
# stimulus directories
path = 'stimuli/'

# indexing where the stimulus name starts
path_idx = len(path) 

# stimulus directories
path = 'stimuli/'

# indexing where the stimulus name starts
path_idx = len(path) 

# get stimulus images
correct_path1 = glob.glob(path + '*c{}**{}*.png'.format(df.iat[id - 1, 1],'g[148]'))
correct_path2 = glob.glob(path + '*c{}**{}*.png'.format(df.iat[id - 1, 2],'g[148]'))
stimuli = correct_path1 + correct_path2

# prepare stimuli dictionaries
STIMULI = prepare_stim(stimuli, path_idx)

# prepare trial list combining target and competitor foils
trial_list = prepare_trial_list(STIMULI)

################ INSTRUCTIONS #########################

# instruction texts
instruction1 = '''
In a moment, you will see a number of schematic images generated in a cultural transmission experiment. 

Your task is to decide which patterns belong together since they are made by the same participants and therefore resemble each other in terms of their style. 

In each trial, you will be presented with a target pattern in the lower part of the screen (this is the one you should make a decision about), and two "competitor" patterns on the upper part of the screen.

If you think the target is more likely to belong together with the competitor to the LEFT in terms of style, you should press the LEFT arrow key. 
If you think the target is more likely to belong together with the competitor to the RIGHT in terms of style, you should press the RIGHT arrow key.

Press SPACE to start the practice session. 
'''

instruction2 = '''
Here is an example of a trial.

You have to decide if the target pattern in the middle of the lower part of the screen comes from the same transmission chain as one or the other pattern on the upper part of the screen.

If you think the target is more likely to belong together with the competitor to the LEFT in terms of style, you should press the LEFT arrow key. 
If you think the target is more likely to belong together with the competitor to the RIGHT in terms of style, you should press the RIGHT arrow key.
'''

instruction3 = '''
Great. Now we are ready to start the actual experiment.
There will be a couple of breaks along the way.

Press SPACE to start.
'''

pause = '''
Time for a break. Press SPACE when you are ready to proceed.
'''

goodbye = '''
The experiment is done. Thank you so much for your participation!
'''

########### RUN EXPERIMENT ##############
msg(instruction1)
practice()
msg(instruction3)

# trial counter
count = 1

for trial in trial_list:
    if count in [55,110,165]:
        msg(pause)
    
    fixation(0.5)
    left_competitor, right_competitor = show_trial(trial)
    stopwatch.reset()
    key = event.waitKeys(keyList = ['left', 'right', 'escape'])[0]
    reaction_time = stopwatch.getTime()
    
    if key == 'escape':
        DATA.to_csv(logfile_name)
        core.quit()
    elif (key == 'left' and (trial['target']['site'] == left_competitor['site'])) or (key == 'right' and (trial['target']['site'] == right_competitor['site'])):
        correct = 1
    else:
        correct = 0
    
    DATA = DATA.append({
        'ID': ID, 
        'age': age, 
        'gender': gender,
        'trial': count, 
        'generation': trial['target']['period'],
        'target': trial['target']['stimulus'], 
        'competitor1': left_competitor['stimulus'], 
        'competitor2': right_competitor['stimulus'], 
        'response': key,
        'correct': correct,
        'reaction_time': reaction_time
        }, ignore_index=True)
    count += 1

DATA.to_csv(logfile_name)

msg(goodbye)