# Cognitive Arhaeology Study
# Experiment 1
# August-2020s

# Import packages
from psychopy import visual, core, event, gui, data
import pandas as pd
import numpy as np
from numpy.random import random, randint, normal, shuffle
import ast, copy, glob, random, re
import matplotlib.pyplot as plt
from pandas.tools.plotting import table

# gui requesting participant info
myDlg = gui.Dlg(title="CogAch salience Experiment") 
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

# define pandas with information - put this early in the script
columnss = ['Participant', 'Age', 'Gender', 'Block', 'Drawing', 'Chain', 'Generation', 'Reaction_time', 'Response', 'Correct_response', 'Correctness']
DATA = pd.DataFrame(columns=columnss) 

#data from practice trials
columns = ['flicking_side','correct response', 'reaction_time', 'response', 'correctness']
DATA_practice = pd.DataFrame(columns=columns) 

#data for deciding side
columns = ['flicking_side', 'reaction_time', 'valid_ones', 'correctness']
clean_data = pd.DataFrame(columns=columns) 

# logfile name + date
date = data.getDateStr()
logfilename = 'logfiles/logfile_{}_{}.csv'.format(ID, date)

# define clock
stopwatch = core.Clock()
globalClock = core.Clock()

# define window
win = visual.Window(size=[1440,900],units = 'pix', monitor = 'P4N', allowStencil = True, color='white', fullscr=True)

#makes mouse invisible
mouse = event.Mouse()
win.mouseVisible = False



### Prepare stim #####
#test stimuli
test_image = visual.ImageStim(win, image='test_image.gif', size = 50, name = 'test_image')

# define directories
STIMULUS_DIR = 'stimuli/'
STIMULUS_idx = len(STIMULUS_DIR)

# import file with partipant and chains matched 
df = pd.read_csv('chain_participant.csv', sep =';')
id = int(ID)

# get stimulus images
correct_path1 = glob.glob(STIMULUS_DIR + '*c{}**{}*.png'.format(df.iat[id - 1, 1],'g[148]'))
correct_path2 = glob.glob(STIMULUS_DIR + '*c{}**{}*.png'.format(df.iat[id - 1, 2],'g[148]'))

Picture = correct_path1 + correct_path1 + correct_path2 + correct_path2


#turn names in the csv file into images
STIMULI = []
for y in range(48):
    stim = visual.ImageStim(win, image=Picture[y], size = 50)
    img = Picture[y][STIMULUS_idx:-4]
    STIMULI += [{
        'stimulus': stim, 
        'chain': re.search('c\d+', img)[0], 
        'generation': re.search('g.', img)[0],
        'image': img}]

#random periods for intervals, so that all stimuli do not show up at the same time
RAN = [0, 0.1, 0.2, 0.3, 0.4] 
count_r = 0
count_l = 0



#### Prepare calibration #####
#base positions on which to base the calibration. They both correspond to the middle of each "half screen"
XL = -360
XR = 360
height = 0

#Create frames
fixationl = visual.TextStim(win, pos=[XL,height],text='+',color='black',units='pixels', height=30)
fixationr = visual.TextStim(win, pos=[XR,0],text='+',color='black',units='pixels', height=30)
bordersl = visual.Rect(win, width=212, height=168, pos=(XL, height), fillColor='white', lineColor='black', lineWidth=20)
bordersr = visual.Rect(win, width=212, height=168, pos=(XR, 0), fillColor='white', lineColor='black', lineWidth=10)
framel = visual.ImageStim(win=win, pos=(XL,height), size=(252,202), color='dimgrey')
framer = visual.ImageStim(win=win, pos=(XR,0), size=(252,202), color='dimgrey')
circlel = visual.Circle(win, radius=20, edges=40, lineWidth= 12, lineColor='black', pos=(XL,height))
circler = visual.Circle(win, radius=20, edges=40, lineWidth= 12, lineColor='black', pos=(XR,0))

#opacity start level
opas=0.0

#creating flicking for L
def flicking(win, position, square_size, columns, rows, flick):
    global flash
    global flash1 # The flash stimulus (an array of flashing squares)
    red = [1, -1, -1]
    green = [-1, 1, -1]
    blue = [-1, -1, 1]
    yellow = [1, 0.97, -0.55]
    black = [-1, -1, -1]
    color_set = [red, green, blue, yellow, black]
    cell_number = columns * rows
    by_color = int(np.floor(float(cell_number)/len(color_set)))
    # fill an array with colors. Each color should appear approximatively the same number of times.
    f_colors = []
    for c in color_set:
        for i in range(by_color):
            f_colors.append(c)
    shuffle(color_set)
    i = cell_number - len(f_colors)
    while i > 0:
        f_colors.append(color_set[i])
        i -= 1
    # randomize color order.
    shuffle(f_colors)
    # fill an array with coordinate for each color square. First square should be at the upper left
    # and next should follow from left to right and up to down.
    xys = []
    x_left = (1 - columns) * square_size / 2
    y_top = (1 - rows) * square_size / 2
    for l in range(rows):
        for c in range(columns):
            xys.append((x_left + c * square_size, y_top + l * square_size))
    if flick == 1:
        flash = visual.ElementArrayStim(win=win,
                        fieldPos=position,
                        fieldShape='sqr',
                        nElements=cell_number,
                        sizes=square_size,
                        xys=xys,
                        colors=f_colors,
                        elementTex=None,
                        elementMask=None,
                        name='flash',
                        autoLog=False)
    elif flick == 2: 
        flash1 = visual.ElementArrayStim(win=win,
                        fieldPos=position,
                        fieldShape='sqr',
                        nElements=cell_number,
                        sizes=square_size,
                        xys=xys,
                        colors=f_colors,
                        elementTex=None,
                        elementMask=None,
                        name='flash1',
                        autoLog=False)

#define the code to calibrate the squares
def calibration(x,y,h):
    cali = True
    while cali == True:
        
        #sets random lists of positions for alt that will be later used for the flickering images and the stimuli
        base_positionsl = [[x-53,h], [x+53,h],[x-53,h], [x+53,h],[x-53,h], [x+53,h],[x-53,h], [x+53,h],[x-53,h], [x+53,h]]
        base_positionsl = np.random.permutation(base_positionsl)
        base_positionsr = [[y-53,0], [y+53,0],[y-53,0], [y+53,0],[y-53,0], [y+53,0],[y-53,0], [y+53,0],[y-53,0], [y+53,0]]
        base_positionsr = np.random.permutation(base_positionsr)
        flickering_positions = [[x-53,h], [y+53,0],[x-53,h], [y+53,0],[x-53,h], [y+53,0],[x-53,h], [y+53,0],[x-53,h], [y+53,0],
        [x-53,h], [y+53,0],[x-53,h], [y+53,0],[x-53,h], [y+53,0],[x-53,h], [y+53,0],[x-53,h], [y+53,0]]
        flickering_positions = np.random.permutation(flickering_positions)
        
        #sets positions for all elements that are shown during the calibration, which are afterward drawn
        bordersl.pos = [x,h]
        bordersr.pos = [y,0]
        fixationl.pos = [x,h]
        fixationr.pos = [y,0]
        framel.pos = [x,h]
        framer.pos = [y,0]
        circlel.pos = [x,h]
        circler.pos = [y,0]
        framel.draw(); framer.draw(); bordersl.draw(); bordersr.draw(); circlel.draw(); circler.draw(); fixationl.draw();fixationr.draw()
        win.flip()
        
        #make the arrow responses move the frames up/down/sides
        response = event.waitKeys(keyList = 'left, right, space, up, down')
        if response[0] == 'left':
            x += 5; y -= 5
        elif response[0] == 'right':
            x -= 5; y += 5
        elif response[0] == 'up':
            h += 5
        elif response[0] == 'down':
            h -= 5
        elif response[0] == 'space':
            cali = False
    return(x,y,h,base_positionsl,base_positionsr,flickering_positions)

# flash stimulus change
def flash_change():
    global flash
    global flash1
    shuffle(flash.colors)
    flash.setColors(flash.colors)
    shuffle(flash1.colors)
    flash1.setColors(flash1 .colors)

# draw data for both calibration and real experiment
def drawData(Pos1, Pos2, session):
    framel.draw(); framer.draw(); bordersl.draw(); bordersr.draw();
    flicking(win, position = Pos1, square_size=10, columns=8, rows=15, flick = 1);
    flicking(win, position = Pos2, square_size=10, columns=8, rows=15, flick = 2);
    flash_change();
    flash.draw();
    flash1.draw();
    fixationl.draw(); fixationr.draw()
    if session == 1:
        test_image.draw()
    elif session == 2:
        STIMULI[t]['stimulus'].draw()
    win.flip()

# show data in the right position after calibration
def basePos(Y,P, X, L):
    base_positions_image = [
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y],
    [X-53,Y], [X+53,Y],[X-53,Y], [X+53,Y]]
    F1XPOS = (L+53,P)
    F2XPOS = (L-53,P)
    return (base_positions_image, F1XPOS, F2XPOS)


##### instructions #########
instructions_general = '''THANKS FOR PARTICIPATING IN OUR EXPERIMENT!\n\nIn this experiment, \
you are going to be presented to different images on top of a flickering colorful background. Your task is to say in which side of the \
screen the image appears on as fast as you can.\n\nIf the image appears on top of the LEFT flickering image, you have to press the \
LEFT arrow on the keyboard.\n\nIf the image appears on top of the RIGHT flickering image, you have to press the RIGHT arrow on the \
keyboard.\n\nYou will first have 20 practice trials. Afterwards, the experiment will begin.\n\nIf, during the experiment, you \
find the stimulus unpleasant, say so: the experiment will be stopped immediately and you will receive full compensation.\n\nPlease press\
 SPACE to continue with the instructions'''

instructions_calibration = '''For the experiment, you are going to use the mirror stereoscope \
in front of you.\n\nIn order to be used correctly, it needs to be calibrated properly. Therefore, you need to follow the following \
instructions once you go to the next screen:\n\n1. Put the stereoscope in front of you as if it were a pair of binoculars.\n\n2.\
Two sets of frames will appear on the screen. You have to move them till they "merge" and you only see one set of \
squares:\nIf you press the RIGHT arrow, the frames move further away from each other.\nIf you press the LEFT arrow, \
the frames will get closer to each other.\nIf you press the UP and DOWN arrows, the frame to the left will move \
accordingly.\n\n3. If you cannot get the two sets of frames to merge, let the experimenter \
know.\n\nPlease press SPACE on the left keyboard when you are ready to start with the calibration.'''

wait = '''Wait for instructions'''

forBreak = '''Break. 
Press SPACE  
to continue'''

end = '''This experiment is now over.\n\nThank you again for participating.\n\n'''

def msg(txt):
    t = visual.TextStim(win, color = "black", text = txt)
    t.draw()
    win.flip()
    event.waitKeys(keyList = 'space')

def waitScreen(txt = 'Wait for instructions'):
    framel.draw(); framer.draw(); bordersl.draw(); bordersr.draw()
    wait_for_instructionsr = visual.TextStim(win, color = "black", pos = (XR,0),text = txt)
    wait_for_instructionsr.draw()
    win.flip()
    event.waitKeys(keyList = 'space')

def blank(time):
    grey = visual.TextStim(win, text='', color = 'black')
    grey.draw()
    win.flip()
    core.wait(time)


##### Start experiment #######
msg(instructions_general)
msg(instructions_calibration)

# start calibration
XL, XR, height, base_positionsl, base_positionsr, flickering_positions = calibration(XL, XR, height) 
framel.draw(); framer.draw(); bordersl.draw(); bordersr.draw()

waitScreen()

# TRIAL PERIOD, NO DATA SAVED #
for a in range(20):
    endTRIAL = False
    opas = 0
    ran_time = random.randint(0,4)
    #set random position for the flickering images
    flickinge = flickering_positions[a]
    #set sitmuli to the opposite side of the flickering
    if flickinge[0] > 0:
        flickingr = ((flickinge[0] - (106)),0)
        test_image.pos = base_positionsl[count_l]
        count_l = count_l + 1
    else:
        flickingr = ((flickinge[0] + 106),height)
        test_image.pos = base_positionsr[count_r]
        count_r = count_r + 1

    stopwatch.reset()

    while not endTRIAL:
        if stopwatch.getTime() > RAN[ran_time]:
            #change opacity 0.015 per win-flip
            if opas < 0.99:
                opas += 0.015
            else: 
                opas = 1
        #draw everything
        test_image.setOpacity(opas)
        drawData(flickinge, flickingr, 1)
        #if the participant did not answer after 15 seconds, it is registered as NaN and the code moves on. 
        if stopwatch.getTime() > 15.0:
            endTRIAL = True
            if flickinge[0] > 0:
                flicking_side = 'right'
            elif flickinge[0] < 0:
                flicking_side = 'left'
                
            if test_image.pos[0] > fixationr.pos[0]:
                corrAns = 'right'
            elif test_image.pos[0] < fixationl.pos[0]:
                corrAns = 'left'
            elif test_image.pos[0] > fixationl.pos[0] and test_image.pos[0] < 0:
                corrAns = 'right'
            elif test_image.pos[0] > fixationl.pos[0] and test_image.pos[0] > 0:
                corrAns = 'left'

            #append trial data to pandas
            DATA_practice = DATA_practice.append({
                'flicking_side': flicking_side,
                'correct response': corrAns,
                'reaction_time': 'NaN',
                'response': 'NaN',
                'correctness': 'NaN'}, ignore_index=True)
        #if a key is pressed, get reaction time, where the flicking is and if they were right
        for key in event.getKeys(keyList = ['left', 'right', 'escape']):
            if key in ['escape']:
                core.quit()
            elif key in ['left']:
                reaction_time = stopwatch.getTime() - RAN[ran_time]
                endTRIAL = True
            elif key in ['right']:
                reaction_time = stopwatch.getTime() - RAN[ran_time]
                endTRIAL = True
                
            if flickinge[0] > 0:
                flicking_side = 'right'
            elif flickinge[0] < 0:
                flicking_side = 'left'
                
            if test_image.pos[0] > fixationr.pos[0]:
                corrAns = 'right'
            elif test_image.pos[0] < fixationl.pos[0]:
                corrAns = 'left'
            elif test_image.pos[0] > fixationl.pos[0] and test_image.pos[0] < 0:
                corrAns = 'right'
            elif test_image.pos[0] > fixationl.pos[0] and test_image.pos[0] > 0:
                corrAns = 'left'
            if key == corrAns and reaction_time > 0:
                correctness = 1.0
            else:
                correctness = 0.0

            #append trial data to pandas
            DATA_practice = DATA_practice.append({
                'flicking_side': flicking_side,
                'correct response': corrAns,
                'reaction_time': reaction_time,
                'response': key,
                'correctness': correctness}, ignore_index=True)
            #aggregation process
            #for those trials in which the participant DID RESPONSE (that is, it was not more than 15 sec
            #we measure where the flicking was, the reaction time, the number of responses (valid_ones) and how many correct ones they had
            if reaction_time != 'NaN':
                clean_data = clean_data.append({
                'flicking_side': flicking_side,
                'reaction_time': reaction_time,
                'valid_ones': correctness,
                'correctness':correctness}, ignore_index=True)

DATA_practice.to_csv('data/TTE_practice_{}.csv'.format(ID[0]))


# SEE RESULTS OF CALIBRATION #

#see the median of the reactione time per side, and the count of actual responses. 
aggregations= {'reaction_time':'median', 'valid_ones':'count', 'correctness':'mean'}

# calculate performance for each flickering side
clean_data = clean_data.groupby('flicking_side').agg(aggregations)

# show wait screen + the experimenter presses 'f' to continue 
waitScreen()
event.waitKeys(keyList = 'f')

#make a table with the information of the practice trial to decide to which eye to show the colors. 
ax = plt.subplot(111, frame_on=False) # no visible frame
ax.xaxis.set_visible(False)  # hide the x axis
ax.yaxis.set_visible(False) #hide y
table(ax, clean_data)  # where clean_data is your data frame
plt.savefig('wer.png')
results=visual.ImageStim(win, image='wer.png', pos = (0,200), size = 1000, name = 'wer')

# show table
results.draw()
win.flip()

# We want to make sure to display the target stimuli to the non-dominant eye - i.e. the side with longer reaction times and lower accuracy.
# THat means that we want the flickering presented to the eye with shorter reaction times.
# select L if flickring should be shown to the left, R if it should be shown to the right.
key = event.waitKeys(keyList = 'l, r')[0]

#show wait screen
waitScreen()

#second option to merge if it did not work before
XL, XR, height, base_positionsl,base_positionsr,flickering_positions = calibration(XL, XR, height) 

#based on the "poetntially" new positions of the frames and the choice of the dominant eye,
#select positions for both the stimuli and the flickering background. 
#there are 48 for the images, since it has to be an equal number of times that it appears on each side.
#the flickering doesnt move, so it has only one. 
# after calibration - should picture be shown in left or right side

if key[0] == 'l':
    base_positions_image = basePos(0, height, XR, XL)[0]
    F1XPOS = basePos(0, height, XR, XL)[1]
    F2XPOS = basePos(0, height, XR, XL)[2]
    Fixation = fixationr.pos
elif key[0] == 'r':
    base_positions_image = basePos(height, 0, XL, XR)[0]
    F1XPOS = basePos(height, 0, XL, XR)[1]
    F2XPOS = basePos(height, 0, XL, XR)[2]
    Fixation = fixationl.pos

#show wait screen
waitScreen()

#START OF REAL EXPERIMENT WITH 3 BLOCKS#
for k in range(3):
    #randomize the list of images before each of the three blocks
    random.shuffle(STIMULI)
    #randomize the list of positions before each of the three blocks
    random.shuffle(base_positions_image)
    #the next loop follows the same structure as the practice loop
    for t in range(48):
        endTRIAL = False
        opas = 0
        ran_time = random.randint(0,4)
        STIMULI[t]['stimulus'].pos = base_positions_image[t]
        stopwatch.reset()
        
        while not endTRIAL:
            if stopwatch.getTime() > RAN[ran_time]:
                if opas < 0.99:
                    opas += 0.015
                else: 
                    opas = 1
            [o['stimulus'].setOpacity(opas) for o in STIMULI]
            drawData(F1XPOS, F2XPOS, 2)
            
            if stopwatch.getTime() > 15.0:
                endTRIAL = True
                reaction_time = 'NaN'
                key = 'None'
                correctness = 'NaN'
                if STIMULI[t]['stimulus'].pos[0] > Fixation[0]:
                    corrAns = 'right'
                if STIMULI[t]['stimulus'].pos[0] < Fixation[0]:
                    corrAns = 'left'
                    
                DATA = DATA.append({
                    'Participant': ID,
                    'Age': age,
                    'Gender': gender,
                    'Block':k+1,
                    'Drawing': STIMULI[t]['image'],
                    'Chain': STIMULI[t]['chain'],
                    'Generation': STIMULI[t]['generation'],
                    'Reaction_time': reaction_time,
                    'Response': key,
                    'Correct_response': corrAns,
                    'Correctness': correctness}, ignore_index=True)
                
            for key in event.getKeys(keyList = ['left', 'right', 'escape']):
                if key in ['escape']:
                    core.quit()
                elif key in ['left']:
                    reaction_time = stopwatch.getTime() - RAN[ran_time]
                    endTRIAL = True
                elif key in ['right']:
                    reaction_time = stopwatch.getTime() - RAN[ran_time]
                    endTRIAL = True
                if STIMULI[t]['stimulus'].pos[0] > Fixation[0]:
                    corrAns = 'right'
                    
                if STIMULI[t]['stimulus'].pos[0] < Fixation[0]:
                    corrAns = 'left'
                    
                if key == corrAns and reaction_time > 0:
                    correctness = '1'
                else:
                    correctness = '0'
    
                #append trial data to pandas
                DATA = DATA.append({
                    'Participant': ID,
                    'Age': age,
                    'Gender': gender,
                    'Block':k+1,
                    'Drawing': STIMULI[t]['image'],
                    'Chain': STIMULI[t]['chain'],
                    'Generation': STIMULI[t]['generation'],
                    'Reaction_time': reaction_time,
                    'Response': key,
                    'Correct_response': corrAns,
                    'Correctness': correctness}, ignore_index=True)
    #participants get a break after each block. they press space to continue
    if k < 2:
        framel.draw(); framer.draw(); bordersl.draw(); bordersr.draw()
        waitScreen(forBreak)
        blank(1)
    else:
        continue
    #data is saved after each block, to ensure that if the participant cannot continue after each block, we still ahve some data. 
    DATA.to_csv(logfilename)

#save to csv file - put this in the end of the script 
DATA.to_csv(logfilename)

msg(end)