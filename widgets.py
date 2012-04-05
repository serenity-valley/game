""" Simplistic "GUI Widgets" for a Pygame screen.
    
    Most widgets receive a 'surface' argument in the constructor.
    This is the pygame surface to which the widget will draw 
    itself when it's draw() method is called.
    
    Unless otherwise specified, all rectangles are pygame.Rect
    instances, and all colors are pygame.Color instances.
"""
import sys

import pygame
from pygame import Rect, Color
from vec2d import vec2d

class WidgetError(Exception): pass
class LayoutError(WidgetError): pass

class Box(object):
    """ A rectangular box. Has a background color, and can have
        a border of a different color.
        
        Has a concept of the "internal rect". This is the rect
        inside the border (not including the border itself).
    """
    def __init__(self, 
            surface,
            rect,
            bgcolor,
            border_width=0,
            border_color=Color('black')):
        """ rect:
                The (outer) rectangle defining the location and
                size of the box on the surface.
            bgcolor: 
                The background color
            border_width:
                Width of the border. If 0, no border is drawn. 
                If > 0, the border is drawn inside the bounding 
                rect of the widget (so take this into account when
                computing internal space of the box).
            border_color:
                Color of the border.
        """
        self.surface = surface
        self.rect = rect
        self.bgcolor = bgcolor
        self.border_width = border_width
        self.border_color = border_color
        
        # Internal rectangle
        self.in_rect = Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
        
    def draw(self):
        pygame.draw.rect(self.surface, self.border_color, self.rect)        
        pygame.draw.rect(self.surface, self.bgcolor, self.in_rect)

    def get_internal_rect(self):
        """ The internal rect of the box.
        """
        return self.in_rect


class MessageBoard(object):
    """ A rectangular "board" for displaying messages on the 
        screen. Uses a Box with text drawn inside.
        
        The text is a list of lines. It can be retrieved and 
        changed with the .text attribute.
    """
    def __init__(self, 
            surface,
            rect,
            text,
	    padding,
            font=('arial', 20),
            font_color=Color('white'),
            bgcolor=Color('gray25'),
            border_width=0,
            border_color=Color('black')):
        """ rect, bgcolor, border_width, border_color have the 
            same meaning as in the Box widget.
            
            text:
                The initial text of the message board.
            font:
                The font (a name, size tuple) of the message
            font_color:
                The font color
        """
        self.surface = surface
        self.rect = rect
        self.text = text
	self.padding = padding
        self.bgcolor = bgcolor
        self.font = pygame.font.SysFont(*font)
        self.font_color = font_color
        self.border_width = border_width
        
        self.box = Box(surface, rect, bgcolor, border_width, border_color)
        
    
    def draw(self):
        #Draw the surrounding box
        self.box.draw()
        
        # Internal drawing rectangle of the box 
        #
        #
        # Write a util method that takes in a width and height of space required for text and padding
        # width, height = self.font.size(text)
        # Calculate required space for text+padding+border
        # utils.get_messagebox_coords(width, height, padding)
        # returns x, y, height, width?
        
        
        text_rect = Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
            
        x_pos = text_rect.left
        y_pos = text_rect.top 
		
        # Render all the lines of text one below the other
        #
        for line in self.text:
            line_sf = self.font.render(line, True, self.font_color, self.bgcolor)
            
	    #test if we can fit text into the MessageBoard + padding
            if ( line_sf.get_width() + x_pos + self.padding > self.rect.right or line_sf.get_height() + y_pos + self.padding > self.rect.bottom):
		raise LayoutError('Cannot fit line "%s" in widget' % line)
            
            self.surface.blit(line_sf, (x_pos+self.padding, y_pos+self.padding))
            y_pos += line_sf.get_height()


class Button(object):
        """     Employs some crap from Box to draw a rectangular button, 
                has some methods to handle click events.
        """
        
        # needs to be replaced.
        (UNCLICKED, CLICKED) = range(2)
        
        def __init__(self, surface, pos=vec2d(0, 0), btntype="", imgnames=[], text="", padding=0, attached=""):
                print "In button init method"
                self.surface = surface
		self.pos = pos
                self.btntype = btntype
                self.imgnames = imgnames
                self.text = text
                self.padding = padding
                self.attached = attached
                
                #load images
		self.imgs = []
                for name in self.imgnames:
                        img = pygame.image.load(name).convert_alpha()
                        self.imgs.append(img)
                        
                #getting position, width and heigth for rect
                #for now we will assume images for all button states are the same size
                #and base calculations off of the first image provided
                
                self.imgwidth, self.imgheight = self.imgs[0].get_size()
                
                print "Image dimensions are: " + str(self.imgwidth) + ", " + str(self.imgheight)
                
                self.rect = Rect(self.pos.x, self.pos.y, self.imgwidth, self.imgheight)               
                
                #set button state to unclicked, untoggled
                self.state = Button.UNCLICKED
                self.toggle = 0 
                
        def draw(self):
                # eventually if we're going to draw arbitrary text on a button, we'll need a better method here.
                # this will do for now.
                if self.btntype == "Close":
                        self.surface.blit(self.imgs[0], self.rect)
                elif self.btntype == "Toggle":
                        self.surface.blit(self.imgs[toggle], self.rect)
                        #flip x back to UNCLICKED
                        Game.buttons[0].state = UNCLICKED
                        self.toggle = not toggle
                
        def mouse_click_event(self, pos):
                if self.btntype == "Close":
                        if self._point_is_inside(vec2d(pos)):
                                self.state = Button.CLICKED
                elif self.btntype == "Toggle":
                        if self._point_is_inside(vec2d(pos)):
                                self.state = Button.CLICKED
        
        def is_visible(self):
                if self.btntype == "Close":
                        return self.state == Button.UNCLICKED
                elif self.btntype == "Toggle":
                        return True
        
        #This will eventually be replaced with a more generic funciton
        #so we can pass in a pos and and rect and see if we clicked on it?
        def _point_is_inside(self, point):
                img_point = point - vec2d(
                        int(self.pos.x - self.imgwidth / 4),
                        int(self.pos.y - self.imgheight / 4))
                try:
                        pix = self.imgs[0].get_at(img_point)
                        return pix[3] > 0
                except IndexError:
                        return False
