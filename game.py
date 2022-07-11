import os, sys
from random import randint, choice
from math import sin, cos, radians

import pygame
#from pygame import Rect, Color
#from pygame.sprite import Sprite
#you already imported pygame, why import modules twice? Your code will run faster if 
#you change Rect to pygame.Rect like I did. If this is a style preference, let me know.

from utils import Timer
from vec2d import vec2d
from widgets import *
#You were importing all widgets anyway, and there was an unknown error. 

class Game(object):
    print "Setting global Game params."
    # Game parameters
    BG_TILE_IMG = 'images/wood2.png'
    BUTTON_BGIMG = 'images/x.png'
    SCREEN_WIDTH, SCREEN_HEIGHT = 580, 500
    GRID_SIZE = 20
    FIELD_SIZE = 400, 400
    
    #need to implement resource loading here
    
    #global game constants make cheating easy!
        
    def __init__(Gloria):
        pygame.init()
        print "Pygame started."
        
        #set up screen and background
        Gloria.screen = pygame.display.set_mode(
                        (Gloria.SCREEN_WIDTH, Gloria.SCREEN_HEIGHT), 0, 32)
        Gloria.tile_img = pygame.image.load(Gloria.BG_TILE_IMG).convert_alpha()
        Gloria.tile_img_rect = Gloria.tile_img.get_rect()
        
           #Drawing a handy MessageBoard widget
        #Can use these for any text.
        print "Configuring tboard MessageBoard params."
        Gloria.tboard_text = ['This is a test.']
        Gloria.tboard_x = 120
        Gloria.tboard_y = 120
        Gloria.tboard_width = 125
        Gloria.tboard_height = 30
        Gloria.tboard_rect = pygame.Rect(Gloria.tboard_x, Gloria.tboard_y, Gloria.tboard_width, Gloria.tboard_height)
        Gloria.tboard_bgcolor = pygame.Color(50, 20, 0)
        Gloria.tboard = MessageBoard(Gloria.screen,
            rect=Gloria.tboard_rect,
            bgcolor=Gloria.tboard_bgcolor,
			border_width=4,
            border_color=pygame.Color('black'),
            text=Gloria.tboard_text,
            padding=5,
            font=('comic sans', 18),
            font_color=pygame.Color('yellow'))
    
	print "Moving on to buttons..."        
    
	Gloria.button_bgimgs = ['images/x.png']
	#Gloria.button_width = Gloria.button_bgimgs[0].get_width()
	#Gloria.button_height = Gloria.button_bgimgs[0].get_height()
        
	#hopefully this will draw the button -15 pixels from the right end, +15 from the top 
	#(hopefully giving us a nice X)
	# should be replaced in the future with a method that returns the coords for an x button
	# in whatever corner we want.
	#Gloria.button_rect = Rect(Gloria.tboard_width, Gloria.tboard_y-15, Gloria.button_width, Gloria.button_height)
	Gloria.button = Button(Gloria.screen,
                                pos=vec2d(Gloria.tboard_width, Gloria.tboard_y-15),
                                btntype='Close',
                                imgnames=Gloria.button_bgimgs,
                                attached=Gloria.tboard)
        
	print "Created close button."
 	
	Gloria.togglebtn_bgimgs = ['images/toggle1.png', 'images/toggle2.png']
        
	Gloria.togglebtn = Button(Gloria.screen,
                                pos=vec2d(250, 250),
                                btntype='Toggle',
                                imgnames=Gloria.togglebtn_bgimgs,
                                attached="",
								text="Toggle",
								textcolor=(255,255,255))
        
	print "Created toggle button."
	
	Gloria.clockImg = Images(Gloria.screen,
					'images/clock.png',
					pos=vec2d(430,0))
				
	Gloria.hand = Images(Gloria.screen,
						'images/secondHand.png',
						pos=vec2d(505,15),
						imgtype='Spinner')
					
	Gloria.textTest = textEntry(Gloria.screen, 
						pos=vec2d(0, Gloria.SCREEN_HEIGHT-50),
						size=vec2d(Gloria.SCREEN_WIDTH,50))
						
	Gloria.floater = movingRect(Gloria.screen,
						pos=vec2d(Gloria.SCREEN_WIDTH/2, 0),
						speed=vec2d(0,5))
						
	Gloria.moveImg = movingImg(Gloria.screen,
						"images/toggle1.png",
						pos=vec2d(0,Gloria.SCREEN_HEIGHT*3/4),
						speed=vec2d(5, 0))
						
	Gloria.ball = circles(Gloria.screen,
						pos=vec2d(25,25),
						radius = 25)
	
	Gloria.buttons = [Gloria.togglebtn]
	Gloria.textEntries = [Gloria.textTest]
	
	Gloria.world = [Gloria.button, Gloria.togglebtn, Gloria.clockImg, Gloria.hand, Gloria.textTest, Gloria.moveImg, Gloria.floater, Gloria.ball]
	
	Gloria.clock = pygame.time.Clock()
	Gloria.paused = False

	#spawning entities

	#Setting up gamefield
	#need a method for dynamically figuring out how many rows/columns we need based on
	#the spacing we want and field size. Using some constants for now.
	Gloria.grid_nrows = 30
	Gloria.grid_ncols = 30
        
	Gloria.field_rect = pygame.Rect(0, 0, Gloria.SCREEN_WIDTH, Gloria.SCREEN_HEIGHT)       
        
	Gloria.options = dict(debug=True, 
                draw_grid=False)
         
	print "Done setting game options, exiting Game init."
        
    def xy2coord(Gloria, pos):
        """ Convert a (x, y) pair to a (nrow, ncol) coordinate
        """
        x, y = (pos[0] - Gloria.field_rect.left, pos[1] - Gloria.field_rect.top)
        return (int(y) / Gloria.GRID_SIZE, int(x) / Gloria.GRID_SIZE)
    
    def coord2xy_mid(Gloria, coord):
        """ Convert a (nrow, ncol) coordinate to a (x, y) pair,
            where x,y is the middle of the square at the coord
        """
        nrow, ncol = coord
        return (
            Gloria.field_rect.left + ncol * Gloria.GRID_SIZE + Gloria.GRID_SIZE / 2, 
            Gloria.field_rect.top + nrow * Gloria.GRID_SIZE + Gloria.GRID_SIZE / 2)
    
    def get_field_rect(Gloria):
        """ Return the internal field rect - the rect of the game
            field exluding its border.
        """
        return Gloria.field_box.get_internal_rect()
        
    def draw_background(Gloria):
        img_rect = Gloria.tile_img.get_rect()
        nrows = int(Gloria.screen.get_height() / img_rect.height) + 1
        ncols = int(Gloria.screen.get_width() / img_rect.width) + 1
        
        for y in range(nrows):
            for x in range(ncols):
                img_rect.topleft = (x * img_rect.width, 
                                    y * img_rect.height)
                Gloria.screen.blit(Gloria.tile_img, img_rect)
    
    def draw_grid(Gloria):
        for y in range(Gloria.grid_nrows + 1):
            pygame.draw.line(
                Gloria.screen,
                pygame.Color(50, 50, 50),
                (Gloria.field_rect.left, Gloria.field_rect.top + y * Gloria.GRID_SIZE - 1),
                (Gloria.field_rect.right - 1, Gloria.field_rect.top + y * Gloria.GRID_SIZE - 1))
        
        for x in range(Gloria.grid_ncols + 1):
            pygame.draw.line(
                Gloria.screen,
                pygame.Color(50, 50, 50),
                (Gloria.field_rect.left + x * Gloria.GRID_SIZE - 1, Gloria.field_rect.top),
                (Gloria.field_rect.left + x * Gloria.GRID_SIZE - 1, Gloria.field_rect.bottom - 1))
    
    def draw(Gloria):
        #draw background image
        Gloria.draw_background()
        
        #decide if we should draw grid.
        if Gloria.options['draw_grid']:
            Gloria.draw_grid()
			
        Gloria.tboard.draw()
		
	for obj in Gloria.world:
			obj.draw()
        
    def run(Gloria):
        print "Beginning run sequence."
        # The main game loop
        #
        while True:
            # Limit frame speed to 30 FPS
            #
            Gloria.time_passed = Gloria.clock.tick(30)
            #~ time_passed = Gloria.clock.tick()
            #~ print time_passed
            
            # If too long has passed between two frames, don't
            # update (the game must have been suspended for some
            # reason, and we don't want it to "jump forward"
            # suddenly)
            #
            if Gloria.time_passed > 100:
                continue
           
	    active = False 
	    for entry in Gloria.textEntries:
		    if entry.clicked:
			    active = True
            #Event loop. In-game control is routed through here
            #Will probably need something more robust soon.
	    for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    Gloria.quit()
		elif event.type == pygame.KEYDOWN and not active:
		    if event.key == pygame.K_SPACE:
			Gloria.paused = not Gloria.paused
		    elif event.key == pygame.K_g:
			#toggle draw grid
			Gloria.options['draw_grid'] = not Gloria.options['draw_grid']
		elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
		    for button in Gloria.buttons:
				button.mouse_click_event(event.pos)
		    for entry in Gloria.textEntries:
				entry.mouse_click_event(event.pos)
            
	    #pass 	temporarily disabled, don't think it does anything
            
	    #entity events here.

            #update hud, counters, score, anything like that here
            if not Gloria.paused:
                msg1 = ''
                msg2 = ''
                #update stats counters. Not doing anything yet
                Gloria.mboard_text = [msg1, msg2]

        #update entities with time passed for internal calculations

                Gloria.draw()
            #actually flip Surface buffer
            pygame.display.flip()

    def quit(Gloria):
        sys.exit()


if __name__ == "__main__":
    print "Creating game object..."
    game = Game()
    print "Done. Starting run method"
    game.run()
