import os, sys
import pygame
from vec2d import vec2d
from utils import Timer
from simpleanimation import SimpleAnimation

class Game(object):
    # Game parameters
    SCREEN_WIDTH, SCREEN_HEIGHT = 580, 500
    BG_COLOR = (0, 0, 0)
    PLAYER_SPEED = 5
    BALL_SPEED = 3
    BALL_RADIUS = 10
    
    def __init__(self):
        pygame.init()
        
        # Set up screen
        self.screen = pygame.display.set_mode(
                        (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)
        pygame.display.set_caption("Bounce Game")
        
        # Load images
        self.player_img = pygame.image.load('images/toggle1.png').convert_alpha()
        self.ball_img = pygame.image.load('images/default_crosshatch.png').convert_alpha()
        self.explosion_img = pygame.image.load('images/explosion1.png').convert_alpha()
        
        # Scale images if needed
        self.player_rect = self.player_img.get_rect()
        self.ball_rect = self.ball_img.get_rect()
        self.ball_rect.width = self.ball_rect.height = self.BALL_RADIUS * 2
        
        # Initialize game objects
        self.player_pos = vec2d(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50)
        self.ball_pos = vec2d(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
        self.ball_vel = vec2d(0, self.BALL_SPEED)  # Start moving down
        
        # Game state
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.explosion = None
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
        
        # Mouse movement
        mouse_pos = pygame.mouse.get_pos()
        self.player_pos.x = mouse_pos[0] - self.player_rect.width // 2
        
        # Keep player within screen bounds
        self.player_pos.x = max(0, min(self.SCREEN_WIDTH - self.player_rect.width, self.player_pos.x))
        
    def update(self):
        if self.game_over:
            if self.explosion and not self.explosion.is_active():
                self.explosion = None
            return
        
        # Update ball position
        self.ball_pos += self.ball_vel
        
        # Ball collision with walls
        if self.ball_pos.x <= 0 or self.ball_pos.x >= self.SCREEN_WIDTH - self.ball_rect.width:
            self.ball_vel.x *= -1
        if self.ball_pos.y <= 0:
            self.ball_vel.y *= -1
        
        # Ball collision with player
        player_rect = pygame.Rect(self.player_pos.x, self.player_pos.y, 
                                 self.player_rect.width, self.player_rect.height)
        ball_rect = pygame.Rect(self.ball_pos.x, self.ball_pos.y, 
                               self.ball_rect.width, self.ball_rect.height)
        
        if player_rect.colliderect(ball_rect):
            # Bounce ball upwards with random x direction
            self.ball_vel.y = -abs(self.ball_vel.y)
            self.ball_vel.x = (self.ball_pos.x - self.player_pos.x) / (self.player_rect.width // 2) * self.BALL_SPEED
        
        # Ball falls below player (game over)
        if self.ball_pos.y >= self.SCREEN_HEIGHT:
            self.game_over = True
            # Create explosion animation
            self.explosion = SimpleAnimation(self.screen, 
                                            (self.ball_pos.x, self.ball_pos.y), 
                                            [self.explosion_img], 100, 1000)
        
        # Update explosion if active
        if self.explosion:
            self.explosion.update(self.clock.get_time())
        
    def draw(self):
        # Clear screen
        self.screen.fill(self.BG_COLOR)
        
        # Draw game objects
        if not self.game_over:
            # Draw player
            self.screen.blit(self.player_img, (self.player_pos.x, self.player_pos.y))
            # Draw ball
            self.screen.blit(self.ball_img, (self.ball_pos.x, self.ball_pos.y))
        else:
            # Draw game over text
            font = pygame.font.SysFont(None, 48)
            text = font.render("Game Over! Press R to Restart", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            
            # Draw explosion
            if self.explosion:
                self.explosion.draw()
        
        # Update display
        pygame.display.flip()
        
    def reset(self):
        # Reset game state
        self.game_over = False
        self.player_pos = vec2d(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50)
        self.ball_pos = vec2d(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
        self.ball_vel = vec2d(0, self.BALL_SPEED)
        self.explosion = None
        
    def run(self):
        # Main game loop
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
    def quit(self):
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
