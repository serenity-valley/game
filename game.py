import os
import sys
import pygame

from random import randint, choice
from math import sin, cos, radians

from utils import Timer
from vec2d import vec2d
from widgets import *


class Game:
    # -----------------------------
    # Global Game Parameters
    # -----------------------------
    BG_TILE_IMG = 'images/wood2.png'
    BUTTON_BGIMG = 'images/x.png'
    SCREEN_WIDTH, SCREEN_HEIGHT = 580, 500
    GRID_SIZE = 20
    FIELD_SIZE = (400, 400)

    def __init__(self):
        pygame.init()
        print("Pygame started.")

        # -----------------------------
        # Screen Setup
        # -----------------------------
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32
        )

        # Background tile
        self.tile_img = pygame.image.load(self.BG_TILE_IMG).convert()
        self.tile_img_rect = self.tile_img.get_rect()

        # -----------------------------
        # Message Board
        # -----------------------------
        print("Configuring MessageBoard...")
        self.tboard_rect = pygame.Rect(120, 120, 125, 30)

        self.tboard = MessageBoard(
            self.screen,
            rect=self.tboard_rect,
            bgcolor=pygame.Color(50, 20, 0),
            border_width=4,
            border_color=pygame.Color('black'),
            text=['This is a test.'],
            padding=5,
            font=('comic sans', 18),
            font_color=pygame.Color('yellow')
        )

        # -----------------------------
        # Buttons
        # -----------------------------
        print("Creating buttons...")

        # Close button
        self.button = Button(
            self.screen,
            pos=vec2d(self.tboard_rect.width, self.tboard_rect.top - 15),
            btntype='Close',
            imgnames=[self.BUTTON_BGIMG],
            attached=self.tboard
        )

        # Toggle Button
        self.togglebtn = Button(
            self.screen,
            pos=vec2d(250, 250),
            btntype='Toggle',
            imgnames=['images/toggle1.png', 'images/toggle2.png'],
            attached=None,
            text="Toggle",
            textcolor=(255, 255, 255)
        )

        # -----------------------------
        # Images / Widgets
        # -----------------------------
        self.clockImg = Images(self.screen, 'images/clock.png', pos=vec2d(430, 0))

        self.hand = Images(
            self.screen,
            'images/secondHand.png',
            pos=vec2d(505, 15),
            imgtype='Spinner'
        )

        self.textTest = textEntry(
            self.screen,
            pos=vec2d(0, self.SCREEN_HEIGHT - 50),
            size=vec2d(self.SCREEN_WIDTH, 50)
        )

        self.floater = movingRect(
            self.screen,
            pos=vec2d(self.SCREEN_WIDTH / 2, 0),
            speed=vec2d(0, 5)
        )

        self.moveImg = movingImg(
            self.screen,
            "images/toggle1.png",
            pos=vec2d(0, self.SCREEN_HEIGHT * 3 / 4),
            speed=vec2d(5, 0)
        )

        self.ball = circles(
            self.screen,
            pos=vec2d(25, 25),
            radius=25
        )

        # Lists for event routing
        self.buttons = [self.togglebtn, self.button]
        self.textEntries = [self.textTest]

        # World objects to draw
        self.world = [
            self.button,
            self.togglebtn,
            self.clockImg,
            self.hand,
            self.textTest,
            self.moveImg,
            self.floater,
            self.ball
        ]

        self.clock = pygame.time.Clock()
        self.paused = False

        # Grid data
        self.grid_nrows = 30
        self.grid_ncols = 30
        self.field_rect = pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.options = dict(
            debug=True,
            draw_grid=False
        )

        print("Game initialized.")

    # ------------------------------------------------------------
    # Coordinate Helpers
    # ------------------------------------------------------------
    def xy2coord(self, pos):
        x, y = pos
        x -= self.field_rect.left
        y -= self.field_rect.top
        return (y // self.GRID_SIZE, x // self.GRID_SIZE)

    def coord2xy_mid(self, coord):
        r, c = coord
        return (
            self.field_rect.left + c * self.GRID_SIZE + self.GRID_SIZE / 2,
            self.field_rect.top + r * self.GRID_SIZE + self.GRID_SIZE / 2
        )

    # ------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------
    def draw_background(self):
        tile_w, tile_h = self.tile_img_rect.size
        ncols = self.SCREEN_WIDTH // tile_w + 2
        nrows = self.SCREEN_HEIGHT // tile_h + 2

        for y in range(nrows):
            for x in range(ncols):
                self.screen.blit(self.tile_img, (x * tile_w, y * tile_h))

    def draw_grid(self):
        color = pygame.Color(50, 50, 50)

        for y in range(self.grid_nrows + 1):
            pygame.draw.line(
                self.screen,
                color,
                (0, y * self.GRID_SIZE),
                (self.SCREEN_WIDTH, y * self.GRID_SIZE)
            )

        for x in range(self.grid_ncols + 1):
            pygame.draw.line(
                self.screen,
                color,
                (x * self.GRID_SIZE, 0),
                (x * self.GRID_SIZE, self.SCREEN_HEIGHT)
            )

    def draw(self):
        self.draw_background()

        if self.options["draw_grid"]:
            self.draw_grid()

        # Message board
        self.tboard.draw()

        # Objects
        for obj in self.world:
            obj.draw()

    # ------------------------------------------------------------
    # Main Loop
    # ------------------------------------------------------------
    def run(self):
        print("Starting main loop...")
        while True:
            dt = self.clock.tick(30)

            if dt > 100:
                continue

            # Check active textEntry
            active = any(entry.clicked for entry in self.textEntries)

            # Event processing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

                elif event.type == pygame.KEYDOWN and not active:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_g:
                        self.options["draw_grid"] = not self.options["draw_grid"]

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for b in self.buttons:
                        b.mouse_click_event(event.pos)
                    for e in self.textEntries:
                        e.mouse_click_event(event.pos)

            if not self.paused:
                self.draw()

            pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    print("Creating game object...")
    game = Game()
    print("Game created. Running...")
    game.run()
