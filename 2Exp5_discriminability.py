# Cognitive Arhaeology Study
# Experiment 5
# August-2020s

# Import modules
from psychopy import visual, core, event, gui, data
import pandas as pd
import numpy as np
import glob, os, random 
from itertools import combinations

### create dialogue box for time entry
myDlg = gui.Dlg(title="CogAch discriminability test") 
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

# make panda for words and responses 
columns = ['Participant', 'Age', 'Gender', 'Trial', 'Stimulus1', 'Stimulus2', 'Target', 'Ori', 'Response', 'Correct','Reaction_time', 'Generation_target', 'Generation_distractor', 'Same_generation']
index = np.arange(0) # array of numbers for the number of samples
DATA = pd.DataFrame(columns=columns, index = index)

# timestamp
date = data.getDateStr() 

# define clock object
stopwatch = core.Clock()

# logfile directory
if not os.path.exists('logfiles'):
    os.makedirs('logfiles')

# define directories
STIMULUS_DIR = 'stimuli/'
LOGFILE_DIR = 'logfiles/'

# logfile name
logfile_name = "logfiles/logfile_{}_{}.csv".format(ID, date)

# define win object
win = visual.Window(fullscr=True, color = 'white', units = 'pix', allowStencil=True) 

# target orientations
ORIS = [0, 45, 135] 

# position list for the elements during the experiments
stim_pos = [(-250,170), (250,170)]

# randomize the positions in the list above
random.shuffle(stim_pos)

# position of target
target_pos = (0, -150)

## define functions
# function that makes a trial list as a dictionary with all combinations of distractors, targets and orientations
def make_trial_list(stimuli):
    trial_list = []
    for pair in stimuli:
        for target in [0, 1]:
            for ori in ORIS:
                trial_list += [{
                    'distractors': pair, 
                    'target': pair[target],
                    'ori': ori}] 
    random.shuffle(trial_list)
    return trial_list

# function to show instruction texts etc
def msg(txt):
    instructions = visual.TextStim(win, text=txt, color = 'black', height = 20) # create an instruction text
    instructions.draw() # draw the text stimulus in a "hidden screen" so that it is ready to be presented 
    win.flip() # flip the screen to reveal the stimulus
    event.waitKeys(keyList = ['space', 'escape']) # wait for any key press

def fixation(time): 
    grey = visual.TextStim(win, text= '+', color = 'black')
    grey.draw()
    win.flip()
    core.wait(time)

def practice_rounds(practice):
    #instruction
    msg(Practice[practice])
    # pick random target
    t = random.choice([0,1])
    # show fixation cross
    fixation(0.5)
    # prepare stimuli
    p_stim1 = visual.ImageStim(win, practice_stim[practice][0], pos = stim_pos[0])
    p_stim2 = visual.ImageStim(win, practice_stim[practice][1], pos = stim_pos[1])
    t_stim = visual.ImageStim(win, practice_stim[practice][t], ori = ORIS[practice], pos = target_pos)
    # draw stimuli
    p_stim1.draw()
    p_stim2.draw()
    t_stim.draw()
    # flip window
    win.flip() 
    # wait for key press
    event.waitKeys(keyList = ['left', 'right']) 

############## PREPARE STIMULI #####################
# import file with partipant and chains matched 
df = pd.read_csv('chain_participant.csv', sep =';')
id = int(ID)

# get stimulus images
correct_path1 = glob.glob(STIMULUS_DIR + '*c{}**{}*.png'.format(df.iat[id - 1, 1],'g[148]'))
correct_path1 = random.sample(correct_path1, k = 6)
correct_path2 = glob.glob(STIMULUS_DIR + '*c{}**{}*.png'.format(df.iat[id - 1, 2],'g[148]'))
correct_path2 = random.sample(correct_path2, k = 6)
STIMULI = correct_path1 + correct_path2
print(len(STIMULI))

# creates combos of stimuli: 2-2, no repetitions, no single elements
STIMULI_COMBI = list(combinations(STIMULI, 2))
print(len(STIMULI_COMBI))

# run function to create randimized trial list with all combinations of stimuli and rotations
trial_list = make_trial_list(STIMULI_COMBI)
print(len(trial_list))

# prepare pratice stim
practice_stim = [
    ['stimuli/Practice_1a.png', 'stimuli/Practice_1b.png'],
    ['stimuli/Practice_2a.png', 'stimuli/Practice_2b.png'],
    ['stimuli/Practice_3a.png', 'stimuli/Practice_3b.png']]


################ INSTRUCTIONS #########################
Instructions = '''
Welcome to this experiment that investigates how correct and fast you are able to make visual decisions.\n\n
In each trial you will be presented with two different figures side-by-side on the screen.\n
You will also see a target figure underneath the two figures.\n\n
If the target is identical to the LEFT figure, press the LEFT arrow key as fast as possible.\n
If the target is identical to the RIGHT figure, press the RIGHT arrow key as fast as possible.\n\n
Notice that some times the target will be rotated either 45 or 135 degrees relative to the matching figure.\n\n
First you will be presented with three practice trials, just to familiarize you with the task.\n\n\n
Press SPACE when you are ready to start the practice trials. 
'''

Practice = [
    'Example of trial without rotation of target\n\nPress SPACE to continue.',
    'Example of trial with 45 degree rotation of target\n\nPress SPACE to continue.', 
    'Example of trial with 135 degree rotation of target\n\nPress SPACE to continue.']

Start_exp = '''
Now we continue to the actual experiment.\n\n
Please remember to answer as FAST as you can, while answering correctly.\n\n
Press SPACE when you are ready.
'''

pause = '''
Time for a break. Press SPACE when you are ready to proceed.
'''

Goodbye = '''
The experiment is done.\n\n
Thank you very much for your participation.
'''

### Run experiment ###
msg(Instructions)

# practice rounds
for i in range(3):
    practice_rounds(i)

msg(Start_exp)

# Actual experiment #
count = 1 
for trial in trial_list:
    if count in [100, 200, 300]:
        msg(pause)
    
    # show fixation for 1 sec
    fixation(0.5)
    
    # target
    target = trial['target']
    ori = trial['ori']
    targ = visual.ImageStim(win, target, pos = target_pos, ori = ori)
    
    # prepare visual display
    stimulus1 = trial['distractors'][0]
    stimulus2 = trial['distractors'][1]
    stim1 = visual.ImageStim(win, stimulus1, pos = stim_pos[0])
    stim2 = visual.ImageStim(win, stimulus2, pos = stim_pos[1])
    
    # draw stimuli
    targ.draw(); stim1.draw(); stim2.draw() 
    win.flip()
    
    # reset stopwatch 
    stopwatch.reset()
    
    # record response
    key = event.waitKeys(keyList = ['escape', 'left', 'right'])
    
    # record reaction time
    reaction_time = stopwatch.getTime()
    
    # if participants answer faster than 150 miliseconds record response as NaN
    if reaction_time > 0.15:
        #code to log the period of the target image
        generationT = target[17:18]
        
        # code to log the period of the distractor. Since the target is chosen randomly among the stimuli, then we select the distractor
        # as being the one that is not the same as the target.
        if target == stimulus1:
            generationD = stimulus2[17:18]
        elif target == stimulus2:
            generationD = stimulus1[17:18]
        
        #log whether the pair of pictures and the distractores are from the same period
        if generationT == generationD:
                same = 1
        elif generationT != generationD:
                same = 0
        
        # decide if response is correct
        if key[0] == 'left':
            response = 'left'
            if target == stimulus1:
                correct = 1
            else:
                correct = 0
            
        elif key[0] == 'right':
            response = 'right'
            if target == stimulus2:
                correct = 1
            else:
                correct = 0
                
        elif key[0] == 'escape':
            DATA.to_csv(logfile_name)
            core.quit()
    else:
        response = 'NaN'
        correct = 'NaN'

    # write data to logfile
    DATA = DATA.append({
        'Participant': ID, 
        'Age': age, 
        'Gender': gender, 
        'Trial': count, 
        'Stimulus1': stimulus1[8:22], 
        'Stimulus2': stimulus2[8:22], 
        'Target': target[8:22], 
        'Ori': ori,
        'Response': response, 
        'Correct': correct, 
        'Reaction_time': reaction_time,
        'Generation_target': generationT,
        'Generation_distractor':generationD,
        'Same_generation': same
        }, ignore_index=True)
    # set trial number for next trial 
    count += 1

# write logfile with date/time in it
DATA.to_csv(logfile_name, index=False)

msg(Goodbye)