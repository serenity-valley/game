""" Simplistic "GUI Widgets" for a Pygame screen.
    
    Most widgets receive a 'surface' argument in the constructor.
    This is the pygame surface to which the widget will draw 
    itself when it's draw() method is called.
    
    Unless otherwise specified, all rectangles are pygame.Rect
    instances, and all colors are pygame.Color instances.
"""
import sys
import time
import pygame
from pygame import Rect, Color
from vec2d import vec2d

from game import *
import simpleanimation

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
        # Need a method that takes in a width and height of space required for text and padding
        # width, height = self.font.size(text)
        # Calculate required space for text+padding+border
        # utils.get_messagebox_coords(width, height, padding)
        # returns x, y, height, width?
        
        # Internal rectangle where the text is actually drawn
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
        
	def __init__(self, surface, pos=vec2d(0, 0), btntype="", imgnames=[], text="", textcolor=(0,0,0), 
		textimg=0,padding=0, attached=""):
		print "In button init method"
		self.surface = surface
		self.pos = pos
		self.btntype = btntype
		self.imgnames = imgnames
		self.text = text
		self.textcolor = textcolor
		self.textimg = textimg
		self.padding = padding
		self.attached = attached
		self.state = Button.UNCLICKED
		self.toggle = 0 
			
		#load images
		self.imgs = []
		for name in self.imgnames:
			img = pygame.image.load(name).convert_alpha()
			#img = img.set_colorkey((255,255,255))
			#it would be nice to make the images transparent,
			#but it throws an error not worth fighting
			self.imgs.append(img)
                
		self.imgwidth, self.imgheight = self.imgs[self.toggle].get_size()
		self.rect = Rect(self.pos.x, self.pos.y, self.imgwidth, self.imgheight)
		print "Image dimensions are: " + str(self.imgwidth) + ", " + str(self.imgheight)
		
		#creates a text label to place in the middle of the button
		font = pygame.font.SysFont("Times New Roman", 25)
		self.textOverlay =  font.render(self.text,1,self.textcolor)
		self.textSize = vec2d(font.size(self.text))
		self.textRect = Rect(self.pos.x+self.imgwidth/2-self.textSize.x/2,self.pos.y+self.imgheight/2-self.textSize.y/2,0,0)
                
                
	def draw(self):
		if self.btntype == "Close":
			self.surface.blit(self.imgs[0], self.rect)
		elif self.btntype == "Toggle":
			self.surface.blit(self.imgs[self.toggle], self.rect)
			if self.toggle == self.textimg:
				self.surface.blit(self.textOverlay, self.textRect)
			
 
	def mouse_click_event(self, pos):
		if self.btntype == "Close":
			if self._point_is_inside(vec2d(pos)):
				self.state = Button.CLICKED
		elif self.btntype == "Toggle":
			if self._point_is_inside(vec2d(pos)):
				self.state = not self.state
				self.toggle = not self.toggle
				self.imgwidth, self.imgheight = self.imgs[self.toggle].get_size()
				self.rect = Rect(self.pos.x, self.pos.y, self.imgwidth, self.imgheight)
				self.textRect = Rect(self.pos.x+self.imgwidth/2-self.textSize.x/2,self.pos.y+self.imgheight/2-self.textSize.y/2,0,0)
		elif self.btntype == "Action":
			if self._point_is_inside(vec2d(pos)):
				self.count = 100
				expl = simpleanimation.start()
				print "Action"
        
	def _point_is_inside(self, mpos):
		if mpos.x > self.rect.x and mpos.x < self.rect.x+self.imgwidth:
			if mpos.y > self.rect.y and mpos.y < self.rect.y+self.imgheight:
				return True

class Images(object):
	""" allows for unclickable images """
	def __init__(self, surface, image, pos=vec2d(0, 0),imgtype=""):
		self.surface = surface
		self.imgtype = imgtype
		self.img = pygame.image.load(image).convert_alpha()
		self.pos = pos
		self.count = 0
		self.imgwidth, self.imgheight = self.img.get_size()
		print "Image dimensions are: " + str(self.imgwidth) + ", " + str(self.imgheight)
		self.rect = Rect(self.pos.x, self.pos.y, self.imgwidth, self.imgheight)  
		
	def draw(self):
		#rotations didn't work well on diagonals. Could use a smoother method
		#but it's really only to test image draw and pause easier 
		if self.imgtype == "Spinner":
			""" spinners make a full rotation every second """
			x, y, ix, iy = self.rect
			if self.count == 7:
				self.img= pygame.transform.rotate(self.img, -90)
				self.rect.y += self.imgheight
			elif self.count == 15:
				self.img= pygame.transform.rotate(self.img, -90)
			elif self.count == 22:
				self.img = pygame.transform.rotate(self.img, -90)
				self.rect.x -= self.imgheight
			elif self.count == 30:
				self.img = pygame.transform.rotate(self.img, -90)
				self.count = 0
				self.rect.x += self.imgheight
				self.rect.y -= self.imgheight
			self.count += 1
		self.surface.blit(self.img, self.rect)

class textEntry(object):
	""" allows for reading input from the user """        
	def __init__(self, surface, pos=vec2d(0, 0), size = vec2d(200,50), text="", textcolor=(0,0,0),padding=0, bgcolor = (255,255,255)):
		print "In textEntry init method"
		self.surface = surface
		self.pos = pos
		self.size = size
		self.text = text
		self.textcolor = textcolor
		self.padding = padding
		self.clicked = False
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
		self.lastKey = ""
		self.delay = 1
		
		#creates a text label to place in the middle of the rectangle
		self.font = pygame.font.SysFont("Times New Roman", 25)
		self.textOverlay =  self.font.render(self.text,1,self.textcolor)
		self.textSize = vec2d(self.font.size(self.text))
		self.textRect = Rect(self.pos.x, self.pos.y, self.textSize.x, self.textSize.y)
                
	def draw(self):
		if self.clicked:
			if pygame.key.get_focused():
				pressed = pygame.key.get_pressed()
				for i in range(len(pressed)):
					if pressed[i] == 1:
						key = pygame.key.name(i)
						if self.lastKey == key and self.delay <= 1:
							#can't seem to find a decent delay time please fix
							self.delay += .4
						elif len(key) == 1 and self.font.size(self.text)[0] <= self.size.x:
							#could easily create a wrap using lists and proper indexing, will do later
							self.text+= key
							self.delay = 0
							self.lastKey = key
						elif key == "tab":
							self.text += "    "
							self.delay = 0
							self.lastKey = key
						elif key == "space":
							self.text += " "
							self.delay = 0
							self.lastKey = key
						elif key == "backspace":
							self.text = self.text[:-1]
							self.delay = 0
							self.lastKey = key
						
						self.textOverlay = self.font.render(self.text,1,self.textcolor)

		pygame.draw.rect(self.surface, (255,255,255), self.rect)
		self.surface.blit(self.textOverlay, self.textRect)
			
	def mouse_click_event(self, pos):
		if self._point_is_inside(vec2d(pos)):
			self.clicked = not self.clicked
        
	def _point_is_inside(self, mpos):
		if mpos.x > self.pos.x and mpos.x < self.pos.x+self.size.x:
			if mpos.y > self.pos.y and mpos.y < self.pos.y+self.size.y:
				return True

class movingRect(object):
	def __init__(self, surface, pos=vec2d(0,0), size=vec2d(20,20), color=(255,0,0), speed=vec2d(1,0), gravity=0):
		""" creates an object that moves around the screen """
		self.surface = surface
		self.surfaceSize = vec2d(self.surface.get_size())
		self.pos = pos
		self.size = size
		self.speed = speed
		self.gravity = gravity
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
		self.color = color
		
	def draw(self):
		if self.pos.x + self.size.x > self.surfaceSize.x or self.pos.x < 0:
			self.speed.x *= -1
		if self.pos.y + self.size.y > self.surfaceSize.y or self.pos.y < 0:
			self.speed.y *= -1
		self.pos.x += self.speed.x
		self.pos.y += self.speed.y
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
		pygame.draw.rect(self.surface, self.color, self.rect)

class movingImg(object):
	def __init__(self, surface, image, pos=vec2d(0,0), speed=vec2d(1,0), gravity=1):
		self.surface = surface
		self.surfaceSize = vec2d(self.surface.get_size())
		self.image = pygame.image.load(image)
		self.pos = pos
		self.speed = speed
		self.gravity = gravity
		self.size = vec2d(self.image.get_size())
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
	
	def draw(self):
		if self.pos.x + self.size.x > self.surfaceSize.x or self.pos.x < 0:
			self.speed.x *= -1
		if self.pos.y + self.size.y > self.surfaceSize.y or self.pos.y < 0:
			self.speed.y *= -1
		self.pos.x += self.speed.x
		self.pos.y += self.speed.y
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
		self.surface.blit(self.image, self.rect)
		
class circles(object):
	def __init__(self, surface, pos=vec2d(10,10), radius=5, bgcolor=(0,0,0)):
		""" creates a simple useless circle """
		self.surface = surface
		self.pos = pos
		self.radius = radius
		self.bgcolor = bgcolor
		
	def draw(self):
		pygame.draw.circle(self.surface, self.bgcolor, self.pos, self.radius)