#from audioop import cross
#from cgitb import text
import pygame, sys, random

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock() # to determine frame rate/screen update time

pygame.mouse.set_visible(False)

# TEXT settings
game_font = pygame.font.Font(None, 64)
text_surface = game_font.render('You Won!', True, (255,255,255))
text_rect = text_surface.get_rect(center = (640,320))

# IMPORTED IMAGES
wood_bg = pygame.image.load('./assets/Wood_BG.png')
land_bg = pygame.image.load('./assets/Land_BG.png')
water_bg = pygame.image.load('./assets/Water_BG.png')
cloud_bg_1 = pygame.image.load('./assets/Cloud1.png')
cloud_bg_2 = pygame.image.load('./assets/Cloud2.png')
crosshair = pygame.image.load('./assets/crosshair.png')
duck_surface = pygame.image.load('./assets/duck.png')

land_position_y = 560
land_speed = 1

water_position_y = 640
water_speed = 1.5

duck_rect_list = []
duck_pos_list = []
duck_pos_vector = 1
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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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

    # WOOD - BACKGROUND               
    screen.blit(wood_bg, (0,0))

    # DUCKS
    for index, duck_rect in enumerate(duck_rect_list):
        if not duck_rect.x in range(duck_pos_list[index][0] - 250, duck_pos_list[index][0] + 250):
            duck_pos_list[index][2] *= -1
        duck_rect.x += duck_pos_list[index][3] * duck_pos_list[index][2]
    
        screen.blit(duck_surface, duck_rect)
  
    # CLOSURE TEXT
    if not len(duck_rect_list):
        screen.blit(text_surface, text_rect)
    
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

    pygame.display.update()
    clock.tick(120)