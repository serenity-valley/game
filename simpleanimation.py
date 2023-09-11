import sys
import pygame

class SimpleAnimation:
    def __init__(self, screen, pos, images, scroll_period, duration=-1):
        self.screen = screen
        self.images = images
        self.pos = pos
        self.img_ptr = 0
        self.active = True
        self.duration = duration
        
        self.scroll_timer = scroll_period
        self.active_timer = duration
        
        self.scroll_time_passed = 0
        self.active_time_passed = 0
    
    def is_active(self):
        return self.active
    
    def update(self, time_passed):
        self.scroll_time_passed += time_passed
        self.active_time_passed += time_passed
        
        if self.scroll_time_passed >= self.scroll_timer:
            self._advance_img()
            self.scroll_time_passed = 0
        
        if self.duration >= 0 and self.active_time_passed >= self.active_timer:
            self.active = False

    def draw(self):
        if self.active:
            cur_img = self.images[self.img_ptr]
            draw_rect = cur_img.get_rect().move(self.pos)
            self.screen.blit(cur_img, draw_rect)
            
    def _advance_img(self):
        self.img_ptr = (self.img_ptr + 1) % len(self.images)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((300, 300))
    clock = pygame.time.Clock()
    
    explosion_img = pygame.image.load('images/explosion1.png').convert_alpha()
    images = [explosion_img, pygame.transform.rotate(explosion_img, 90)]
    
    expl = SimpleAnimation(screen, (100, 100), images, 100, 2120)
    
    while True:
        time_passed = clock.tick(50)
        
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        expl.update(time_passed)
        expl.draw()
        
        pygame.display.flip()
