import os, sys
from random import randint, choice
from math import sin, cos, radians

import pygame
from pygame import Rect, Color
from pygame.sprite import Sprite

from simpleanimation import SimpleAnimation
from utils import Timer
from vec2d import vec2d
from widgets import Box, MessageBoard, Button

class Game(object):
    # Game parameters
    BG_TILE_IMG = 'images/wood2.png'
    BUTTON_BGIMG = 'images/x.png'
    SCREEN_WIDTH, SCREEN_HEIGHT = 580, 500
    GRID_SIZE = 20
    FIELD_SIZE = 400, 400
    
    #will implement resource loading here
    
    #Arbitrary game constants. Will make cheating easy.

    def __init__(self):
        pygame.init()
        
        #set up screen and background
        self.screen = pygame.display.set_mode(
                        (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)
        self.tile_img = pygame.image.load(self.BG_TILE_IMG).convert_alpha()
        self.tile_img_rect = self.tile_img.get_rect()
	
	#Drawing a handy MessageBoard widget
	#Can use these for any text
        self.tboard_text = ['This is a test.']
        self.tboard_x = 20
        self.tboard_y = 20
        self.tboard_width = 125
        self.tboard_height = 30
        self.tboard_rect = Rect(self.tboard_x, self.tboard_y, self.tboard_width, self.tboard_height)
        self.tboard_bgcolor = Color(50, 20, 0)
        self.tboard = MessageBoard(self.screen,
            rect=self.tboard_rect,
            bgcolor=self.tboard_bgcolor,
            border_width=4,
            border_color=Color('black'),
            text=self.tboard_text,
	    padding=5,
            font=('comic sans', 18),
            font_color=Color('yellow'))
    
        self.button_bgimg = pygame.image.load(self.BUTTON_BGIMG).convert_alpha()
        self.button_width = self.button_bgimg.get_width()
        self.button_height = self.button_bgimg.get_height()
        
        
        #hopefully this will draw the button -15 pixels from the right end, +15 from the top 
        #(hopefully giving us a nice X)
        # should be replaced in the future with a method that returns the coords for an x button
        # in whatever corner we want.
        self.button_rect = Rect(self.tboard_width, self.tboard_y-15, self.button_width, self.button_height)
        self.button = Button(self.screen,
                                rect=self.button_rect,
                                btntype='Close',
                                bgimg=self.button_bgimg,
                                attached=self.tboard)        
        
        self.clock = pygame.time.Clock()
        self.paused = False

	#spawning entities

        
        #Setting up gamefield
        #need a method for dynamically figuring out how many rows/columns we need based on
        #the spacing we want and field size. Using some constants for now.
        self.grid_nrows = 30
        self.grid_ncols = 30
        
        self.field_rect = Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        self.options = dict(debug=True, 
                draw_grid=False)
         
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
                Color(50, 50, 50),
                (self.field_rect.left, self.field_rect.top + y * self.GRID_SIZE - 1),
                (self.field_rect.right - 1, self.field_rect.top + y * self.GRID_SIZE - 1))
        
        for x in range(self.grid_ncols + 1):
            pygame.draw.line(
                self.screen,
                Color(50, 50, 50),
                (self.field_rect.left + x * self.GRID_SIZE - 1, self.field_rect.top),
                (self.field_rect.left + x * self.GRID_SIZE - 1, self.field_rect.bottom - 1))
    
    def draw(self):
	#draw background image
        self.draw_background()
	
	#draw game field crap here
        
	#decide if we should draw grid.
        if self.options['draw_grid']:
            self.draw_grid()
                
        #Only stuff being drawn right now.
        #Message board with x button
        self.tboard.draw()
	self.button.draw()
        
	#this way we can draw dynamic MessageBoards.
        #self.mboard.text = self.mboard_text <-- copy in latest text
        #self.mboard.draw()
        
	#other entity draw calls
        
    def run(self):
        # The main game loop
        #
        while True:
            # Limit frame speed to 30 FPS
            #
            time_passed = self.clock.tick(30)
            #~ time_passed = self.clock.tick()
            #~ print time_passed
            
            # If too long has passed between two frames, don't
            # update (the game must have been suspended for some
            # reason, and we don't want it to "jump forward"
            # suddenly)
            #
            if time_passed > 100:
                continue
            
	    #Event loop. In-game control is pretty much routed through here
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_g:
                        #toggle draw grid
                        #if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.options['draw_grid'] = not self.options['draw_grid']
                elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                        self.button.mouse_click_event(event.pos)
			pass
			#entity events here.

            #update hud, counters, score, anything like that here
            if not self.paused:
                msg1 = ''
                msg2 = ''
                #update stats counters. Not doing anything yet
                self.mboard_text = [msg1, msg2]

		#update entities with time passed for internal calculations

                self.draw()
            #actually flip Surface buffers
            pygame.display.flip()

    def quit(self):
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()