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
            
	    #test if we can fit text into the MessageBoard
            if ( line_sf.get_width() + x_pos + self.padding > self.rect.right or line_sf.get_height() + y_pos + self.padding > self.rect.bottom):
		raise LayoutError('Cannot fit line "%s" in widget' % line)
            
            self.surface.blit(line_sf, (x_pos+self.padding, y_pos+self.padding))
            y_pos += line_sf.get_height()


class Button(object):
        """     Employs some crap from Box to draw a rectangular button, 
                has some methods to handle click events.
        """
        
        (UNCLICKED, CLICKING, CLICKED) = range(3)
        
        def __init__(self, surface, rect, btntype, bgimg, attached):
                self.surface = surface
                self.rect = rect
                self.btntype = type
                self.bgimg = bgimg
                
                self.width, self.height = self.bgimg.get_size()
                
                self.state = Button.UNCLICKED
                
                self.attached = attached
                
        def draw(self):
                if self.is_visible():
                        self.surface.blit(self.bgimg, self.rect)
                
        def mouse_click_event(self, pos):
                if self._point_is_inside(vec2d(pos)):
                        self.state = Button.CLICKED

        
        def is_visible(self):
                return self.state == Button.UNCLICKED or self.state == Button.CLICKING
        
        #This will eventually be replaced with a more generic funciton
        #so we can pass in a pos and 2d vector and tell if we've clicked on something
        def _close_widget(self):
                self.state == Button.CLICKED
        
        def _point_is_inside(self, point):
                img_point = point - vec2d(  
                        int(self.width / 2),
                        int(self.height / 2))
                try:
                        pix = self.bgimg.get_at(img_point)
                        return pix[3] > 0
                except IndexError:
                        return False
