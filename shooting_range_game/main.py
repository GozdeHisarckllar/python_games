#from audioop import cross
#from cgitb import text
import pygame, sys, random
from openal import *
import time

class Animation(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []

        for num in range(5):
            exp_img = pygame.image.load(f'./assets/gfx/shot{num}.png').convert_alpha()
            exp_img = pygame.transform.scale(exp_img, (280, 280))
            self.images.append(exp_img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x,y))
        self.counter = 0

    def update(self):
        exp_speed = 2
        self.counter += 1

        if self.counter >= exp_speed and self.index < len(self.images) - 1:
            self.index += 1
            self.image = self.images[self.index]
            self.counter = 0

        if self.counter >= exp_speed and self.index >= len(self.images) - 1:
            self.kill()

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock() # to determine frame rate/screen update time

pygame.mouse.set_visible(False)

# SFX
hit_sound = oalOpen('./assets/sfx/hit.wav')
background_sound = oalOpen('./assets/sfx/funny_song.wav')
result_sound = oalOpen('./assets/sfx/good_result.wav')
yay_sound = oalOpen('./assets/sfx/yay.wav')
background_sound.set_looping(True)

oal_listener = oalGetListener() 
oal_listener.set_gain(.25)

background_sound.play()
# TEXT settings
game_font = pygame.font.Font(None, 64)
text_surface = game_font.render('You Won!', True, (255,255,255))
text_rect = text_surface.get_rect(center = (640,320))

# IMPORTED IMAGES
wood_bg = pygame.image.load('./assets/gfx/Wood_BG.png')
land_bg = pygame.image.load('./assets/gfx/Land_BG.png')
water_bg = pygame.image.load('./assets/gfx/Water_BG.png')
cloud_bg_1 = pygame.image.load('./assets/gfx/Cloud1.png')
cloud_bg_2 = pygame.image.load('./assets/gfx/Cloud2.png')
crosshair = pygame.image.load('./assets/gfx/crosshair.png')
duck_surface = pygame.image.load('./assets/gfx/duck.png')

land_position_y = 560
land_speed = 1

water_position_y = 640
water_speed = 1.5

duck_rect_list = []
duck_pos_list = []
duck_pos_vector = 1

is_end = False
'''
def drawRect(surface, pos):
    return surface.get_rect(center = pos)
'''
# DUCK RECTS
for i in range(20):
    duck_position_x = random.randrange(50, 1200)
    duck_position_y = random.randrange(120, 600)
    duck_pos_speed = random.randrange(1, 12)
    duck_rect = duck_surface.get_rect(center = (duck_position_x, duck_position_y))
    duck_pos_list.append([duck_position_x, duck_position_y, duck_pos_vector, duck_pos_speed])
    duck_rect_list.append(duck_rect)

crosshair_rect = None

animation_group = pygame.sprite.Group()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            oalQuit()
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            # rect helps to move the mouse position from the top left corner to the center of the image/surface
            crosshair_rect = crosshair.get_rect(center = event.pos) #the center of the rect is where the cursor is

        if event.type == pygame.MOUSEBUTTONDOWN:
            for index, duck_rect in enumerate(duck_rect_list):
                if duck_rect.collidepoint(event.pos):   # Collision refinement --instead of crosshair_rect.colliderect(duck_rect):
                    del duck_rect_list[index] 
                    del duck_pos_list[index]

                    shot = Animation(event.pos[0], event.pos[1])
                    animation_group.add(shot)
             
                    hit_sound.play()

    # WOOD - BACKGROUND               
    screen.blit(wood_bg, (0,0))

    # DUCKS
    for index, duck_rect in enumerate(duck_rect_list):
        if not duck_rect.x in range(duck_pos_list[index][0] - 250, duck_pos_list[index][0] + 250):
            duck_pos_list[index][2] *= -1
        duck_rect.x += duck_pos_list[index][3] * duck_pos_list[index][2]
    
        screen.blit(duck_surface, duck_rect)
  
    # CLOSURE TEXT
    if len(duck_rect_list) == 0:
        screen.blit(text_surface, text_rect)
        background_sound.stop()

        if not is_end:
            result_sound.play()
            yay_sound.play()
            is_end = True
    
    # LAND
    land_position_y -= land_speed

    if land_position_y <= 520 or land_position_y >= 600:#520-640
        land_speed *= -1

    screen.blit(land_bg, (0, land_position_y))

    # WATER
    water_position_y -= water_speed

    if water_position_y <= 500 or water_position_y >= 700:
        water_speed *= -1

    screen.blit(water_bg, (0, water_position_y))

    # we use the position of the rect as the position of the crosshair
    # place the surface/img on the rect
    if not crosshair_rect:
        crosshair_rect = crosshair.get_rect(center = (640,340))

    
    screen.blit(crosshair, crosshair_rect) 

    screen.blit(cloud_bg_1, (50,150))
    screen.blit(cloud_bg_1, (900,120))
    screen.blit(cloud_bg_2, (120,170))
    screen.blit(cloud_bg_1, (1120,100))
    screen.blit(cloud_bg_2, (150,125))
    screen.blit(cloud_bg_1, (400,50))
    screen.blit(cloud_bg_2, (800,90))

    animation_group.draw(screen)
    animation_group.update()

    pygame.display.update()
    clock.tick(120)