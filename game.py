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
        
    def __init__(self):
        pygame.init()
        print "Pygame started."
        
        #set up screen and background
        self.screen = pygame.display.set_mode(
                        (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)
        self.tile_img = pygame.image.load(self.BG_TILE_IMG).convert_alpha()
        self.tile_img_rect = self.tile_img.get_rect()
        
           #Drawing a handy MessageBoard widget
        #Can use these for any text.
        print "Configuring tboard MessageBoard params."
        self.tboard_text = ['This is a test.']
        self.tboard_x = 120
        self.tboard_y = 120
        self.tboard_width = 125
        self.tboard_height = 30
        self.tboard_rect = pygame.Rect(self.tboard_x, self.tboard_y, self.tboard_width, self.tboard_height)
        self.tboard_bgcolor = pygame.Color(50, 20, 0)
        self.tboard = MessageBoard(self.screen,
            rect=self.tboard_rect,
            bgcolor=self.tboard_bgcolor,
			border_width=4,
            border_color=pygame.Color('black'),
            text=self.tboard_text,
            padding=5,
            font=('comic sans', 18),
            font_color=pygame.Color('yellow'))
    
	print "Moving on to buttons..."        
    
	self.button_bgimgs = ['images/x.png']
	#self.button_width = self.button_bgimgs[0].get_width()
	#self.button_height = self.button_bgimgs[0].get_height()
        
	#hopefully this will draw the button -15 pixels from the right end, +15 from the top 
	#(hopefully giving us a nice X)
	# should be replaced in the future with a method that returns the coords for an x button
	# in whatever corner we want.
	#self.button_rect = Rect(self.tboard_width, self.tboard_y-15, self.button_width, self.button_height)
	self.button = Button(self.screen,
                                pos=vec2d(self.tboard_width, self.tboard_y-15),
                                btntype='Close',
                                imgnames=self.button_bgimgs,
                                attached=self.tboard)
        
	print "Created close button."
 	
	self.togglebtn_bgimgs = ['images/toggle1.png', 'images/toggle2.png']
        
	self.togglebtn = Button(self.screen,
                                pos=vec2d(250, 250),
                                btntype='Toggle',
                                imgnames=self.togglebtn_bgimgs,
                                attached="",
								text="Toggle",
								textcolor=(255,255,255))
        
	print "Created toggle button."
	
	self.clockImg = Images(self.screen,
					'images/clock.png',
					pos=vec2d(430,0))
				
	self.hand = Images(self.screen,
						'images/secondHand.png',
						pos=vec2d(505,15),
						imgtype='Spinner')
					
	self.textTest = textEntry(self.screen, 
						pos=vec2d(0, self.SCREEN_HEIGHT-50),
						size=vec2d(self.SCREEN_WIDTH,50))
						
	self.floater = movingRect(self.screen,
						pos=vec2d(self.SCREEN_WIDTH/2, 0),
						speed=vec2d(0,5))
						
	self.moveImg = movingImg(self.screen,
						"images/toggle1.png",
						pos=vec2d(0,self.SCREEN_HEIGHT*3/4),
						speed=vec2d(5, 0))
						
	self.ball = circles(self.screen,
						pos=vec2d(25,25),
						radius = 25)
	
	self.buttons = [self.togglebtn]
	self.textEntries = [self.textTest]
	
	self.world = [self.button, self.togglebtn, self.clockImg, self.hand, self.textTest, self.moveImg, self.floater, self.ball]
	
	self.clock = pygame.time.Clock()
	self.paused = False

	#spawning entities

	#Setting up gamefield
	#need a method for dynamically figuring out how many rows/columns we need based on
	#the spacing we want and field size. Using some constants for now.
	self.grid_nrows = 30
	self.grid_ncols = 30
        
	self.field_rect = pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)       
        
	self.options = dict(debug=True, 
                draw_grid=False)
         
	print "Done setting game options, exiting Game init."
        
    def xy2coord(self, pos):
        """ Convert a (x, y) pair to a (nrow, ncol) coordinate
        """
        x, y = (pos[0] - self.field_rect.left, pos[1] - self.field_rect.top)
        return (int(y) / self.GRID_SIZE, int(x) / self.GRID_SIZE)
    
    def coord2xy_mid(self, coord):
        """ Convert a (nrow, ncol) coordinate to a (x, y) pair,
            where x,y is the middle of the square at the coord
        """
        nrow, ncol = coord
        return (
            self.field_rect.left + ncol * self.GRID_SIZE + self.GRID_SIZE / 2, 
            self.field_rect.top + nrow * self.GRID_SIZE + self.GRID_SIZE / 2)
    
    def get_field_rect(self):
        """ Return the internal field rect - the rect of the game
            field exluding its border.
        """
        return self.field_box.get_internal_rect()
        
    def draw_background(self):
        img_rect = self.tile_img.get_rect()
        nrows = int(self.screen.get_height() / img_rect.height) + 1
        ncols = int(self.screen.get_width() / img_rect.width) + 1
        
        for y in range(nrows):
            for x in range(ncols):
                img_rect.topleft = (x * img_rect.width, 
                                    y * img_rect.height)
                self.screen.blit(self.tile_img, img_rect)
    
    def draw_grid(self):
        for y in range(self.grid_nrows + 1):
            pygame.draw.line(
                self.screen,
                pygame.Color(50, 50, 50),
                (self.field_rect.left, self.field_rect.top + y * self.GRID_SIZE - 1),
                (self.field_rect.right - 1, self.field_rect.top + y * self.GRID_SIZE - 1))
        
        for x in range(self.grid_ncols + 1):
            pygame.draw.line(
                self.screen,
                pygame.Color(50, 50, 50),
                (self.field_rect.left + x * self.GRID_SIZE - 1, self.field_rect.top),
                (self.field_rect.left + x * self.GRID_SIZE - 1, self.field_rect.bottom - 1))
    
    def draw(self):
        #draw background image
        self.draw_background()
        
        #decide if we should draw grid.
        if self.options['draw_grid']:
            self.draw_grid()
			
        self.tboard.draw()
		
	for obj in self.world:
			obj.draw()
        
    def run(self):
        print "Beginning run sequence."
        # The main game loop
        #
        while True:
            # Limit frame speed to 30 FPS
            #
            self.time_passed = self.clock.tick(30)
            #~ time_passed = self.clock.tick()
            #~ print time_passed
            
            # If too long has passed between two frames, don't
            # update (the game must have been suspended for some
            # reason, and we don't want it to "jump forward"
            # suddenly)
            #
            if self.time_passed > 100:
                continue
           
	    active = False 
	    for entry in self.textEntries:
		    if entry.clicked:
			    active = True
            #Event loop. In-game control is routed through here
            #Will probably need something more robust soon.
	    for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    self.quit()
		elif event.type == pygame.KEYDOWN and not active:
		    if event.key == pygame.K_SPACE:
			self.paused = not self.paused
		    elif event.key == pygame.K_g:
			#toggle draw grid
			self.options['draw_grid'] = not self.options['draw_grid']
		elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
		    for button in self.buttons:
				button.mouse_click_event(event.pos)
		    for entry in self.textEntries:
				entry.mouse_click_event(event.pos)
            
	    #pass 	temporarily disabled, don't think it does anything
            
	    #entity events here.

            #update hud, counters, score, anything like that here
            if not self.paused:
                msg1 = ''
                msg2 = ''
                #update stats counters. Not doing anything yet
                self.mboard_text = [msg1, msg2]

        #update entities with time passed for internal calculations

                self.draw()
            #actually flip Surface buffer
            pygame.display.flip()

    def quit(self):
        sys.exit()


if __name__ == "__main__":
    print "Creating game object..."
    game = Game()
    print "Done. Starting run method"
    game.run()
