import random, pygame, sys
from pygame.locals import *

FPS = 30 # frames per second, the general speed of the program
WINDOWWIDTH = 800 # size of window's width in pixels
WINDOWHEIGHT = 500 # size of windows' height in pixels
REVEALSPEED = 8 # speed boxes' sliding reveals and covers
BOXSIZE = 40 # size of box height & width in pixels
GAPSIZE = 10 # size of gap between boxes in pixels
BOARDWIDTH = 8 # number of columns of icons
BOARDHEIGHT = 8 # number of rows of icons
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2) - 100
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)
 
#            R    G    B
BLUE     = (  0,   0, 255)
CYAN     = (  0, 255, 255)
GRAY     = (100, 100, 100)
GREEN    = (  0, 255,   0)
NAVYBLUE = ( 60,  60, 100)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
RED      = (255,   0,   0)
WHITE    = (255, 255, 255)
YELLOW   = (255, 255,   0)

box_colour = (255, 255, 255)

BGCOLOUR = NAVYBLUE
LIGHTBGCOLOUR = GRAY
HIGHLIGHTCOLOUR = BLUE

OVAL = 'oval'
 
ALLCOLORS = (RED, GREEN, BLUE, YELLOW)
ALLSHAPES = (OVAL)
MATCHSCORES = (2, 4, 8, 16, 32, 64, 128)
LEVELSCORES = (0, 20, 40, 160, 640, 2560, 10240)
LOTTO = (0, 0, 0, 0.04, 0.10, 0.18, 0.28)
MAXLEVEL = 7
curr_score = 0
curr_lv = 1
available_flips = 32
#EACH TIME COMPLETE A MATCH, AVAILFLIP += min(2^LV, 15) 
revealed = []
pattern = 2
 
def main():
    global FPSCLOCK, DISPLAYSURF, revealed, curr_score, curr_lv, pattern, box_colour, available_flips
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
 
    mousex = 0 # x coordinate of mouse
    mousey = 0 # y coordinate of mouse
    pygame.display.set_caption('Memory Overflow')
 
    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)
 
    firstSelection = None # stores the (x, y) of the first box clicked.
 
    DISPLAYSURF.fill(BGCOLOUR)
 
    while True: # main game loop
        mouseClicked = False
 
        DISPLAYSURF.fill(BGCOLOUR) # drawing the window
        drawStatus(curr_score, curr_lv, available_flips)
        drawBoard(mainBoard, revealedBoxes)
 
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
            # my secret cheat key before flash!
            elif event.type == KEYDOWN:
                key = pygame.key.get_pressed()
                if key[pygame.K_h]:
                    #remember to print screen...
                    hint(mainBoard, 5000)
                elif key[pygame.K_9]:
                    available_flips += 9
            #
 
        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # The mouse is currently over a box.
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True # set the box as "revealed"
                available_flips -= 1
                if available_flips <= 0:
                    gameLostAnimation(available_flips)                    
                    pygame.quit()
                    sys.exit()                    
                if firstSelection == None: # the current box was the first box clicked
                    firstSelection = (boxx, boxy)
                    revealed.append(firstSelection)
                else: # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    colour1 = getColour(mainBoard, firstSelection[0], firstSelection[1])
                    colour2 = getColour(mainBoard, boxx, boxy)
 
                    # icons don't match
                    if colour1 != colour2:
                        pygame.time.wait(1000) 
                        revealed.append((boxx, boxy))
                        coverBoxesAnimation(mainBoard, revealed)
                        for box in revealed:
                            revealedBoxes[box[0]][box[1]] = False
                        revealed = []
                        firstSelection = None
                    # not fulfilling pattern
                    elif len(revealed)+1 < pattern:
                        revealed.append((boxx, boxy))
                    # has fulfilled pattern
                    else:
                        revealed.append((boxx,boxy))
                        completeMatch()
                        for box in revealed:
                            revealedBoxes[box[0]][box[1]] = False 
                        refillBox(mainBoard)
                        firstSelection = None

        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val] * BOARDHEIGHT)
    return revealedBoxes


def getRandomizedBoard():
    icons = []
    for colour in ALLCOLORS:
        icons.append(colour)

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            imax = len(icons) - 1
            i = random.randint(0, imax)
            column.append(icons[i])
        board.append(column)
    return board


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)


def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def drawIcon(colour, boxx, boxy):
    quarter = int(BOXSIZE * 0.25) 
    half =    int(BOXSIZE * 0.5) 

    left, top = leftTopCoordsOfBox(boxx, boxy) # get pixel coords from board coords
    pygame.draw.ellipse(DISPLAYSURF, colour, (left, top + quarter, BOXSIZE, half))


def getColour(board, boxx, boxy):
    return board[boxx][boxy]

def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOUR, (left, top, BOXSIZE, BOXSIZE))
        colour = getColour(board, box[0], box[1])
        drawIcon(colour, box[0], box[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAYSURF, box_colour, (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):
    # Do the "box reveal" animation.
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, - REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    # Do the "box cover" animation.
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(DISPLAYSURF, box_colour, (left, top, BOXSIZE, BOXSIZE))
            else:
                # Draw the (revealed) icon.
                colour = getColour(board, boxx, boxy)
                drawIcon(colour, boxx, boxy)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOUR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)
        
        
def refillBox(board):
    global revealed 
    coverBoxesAnimation(board, revealed)
    icons = []
    for colour in ALLCOLORS:
        icons.append(colour)    
    for box in revealed:
        imax = len(icons) - 1
        i = random.randint(0, imax)
        x = box[0]
        y = box[1]
        board[x][y] = icons[i]
    revealed = []
   
def levelUp():
    global curr_lv, pattern, box_colour, available_flips
    curr_lv += 1
    pattern += 1
    available_flips += 32
    b = 255-40*(curr_lv-1)
    g = 255-40*(curr_lv-1)
    box_colour = (255, b, g)

#reveal all squares for 1 sec, only possible after level 6 (5 same flips)
def hint(board, time):
    boxes = []
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            boxes.append((boxx, boxy))   
    revealBoxesAnimation(board, boxes)
    pygame.time.wait(time)
    coverBoxesAnimation(board, boxes)
    

def completeMatch():
    global curr_score, available_flips
    curr_score += MATCHSCORES[curr_lv - 1]
    if (curr_lv != MAXLEVEL) and (curr_score >= LEVELSCORES[curr_lv]):
        levelUp()
    new_flips = min(2**curr_lv, 25)
    available_flips += new_flips


def drawStatus(score, level, flipsLeft):
    global DISPLAYSURF
    status_font = pygame.font.Font('freesansbold.ttf', 18)
    # draw the score text
    scoreSurf = status_font.render('Score: %s' % score, True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = status_font.render('Level: %s' % level, True, WHITE)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)   
    
    # draw the flips-left text
    levelSurf = status_font.render('Flips left: %s' % flipsLeft, True, WHITE)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 80)
    DISPLAYSURF.blit(levelSurf, levelRect)   
         
     
def gameLostAnimation(flipsLeft):
    global DISPLAYSURF
    status_font = pygame.font.Font('freesansbold.ttf', 18)    
    # draw the flips-left text
    i = 3
    while (i>0):
        levelSurf = status_font.render('Flips left: %s' % flipsLeft, True, RED)
        levelRect = levelSurf.get_rect()
        levelRect.topleft = (WINDOWWIDTH - 150, 80)
        DISPLAYSURF.blit(levelSurf, levelRect)  
        pygame.display.update()
        FPSCLOCK.tick(FPS)        
        pygame.time.wait(300)
    
        levelSurf = status_font.render('Flips left: %s' % flipsLeft, True, WHITE)
        levelRect = levelSurf.get_rect()
        levelRect.topleft = (WINDOWWIDTH - 150, 80)
        DISPLAYSURF.blit(levelSurf, levelRect)    
        pygame.display.update()
        FPSCLOCK.tick(FPS)        
        pygame.time.wait(300)
        
        i -= 1
    pygame.time.wait(1000)
    
def winFlips(numberOfFlips):
    global available_flips
    available_flips += numberOfFlips


def drawLotto():
    ticket = random.randint(1, 100) * LOTTO[curr_lv-1]
    winning = random.randint(1, 100)
    if (ticket > winning):
        winType = random.randint(1, 3)
        if (winType == 1):
            hint(5000)
        elif (winType == 2):
            hint(3000)
        elif (winType == 3):
            winFlips(10+curr_lv*2)
    

if __name__ == '__main__':
    main()