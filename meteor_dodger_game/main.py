import pygame, sys, random

# Sprite classes

# Spaceship Sprite  ---------------------------

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, uncharged_path, charged_path, x_pos, y_pos):
        super().__init__()
        self.uncharged = pygame.image.load(uncharged_path).convert_alpha()
        self.charged = pygame.image.load(charged_path).convert_alpha()

        self.image = self.uncharged
        self.rect = self.image.get_rect(center = (x_pos, y_pos))

        self.shield_surface = pygame.image.load('./assets/gfx/shield.png').convert_alpha()
        self.health = 5

    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        self.constrain_screen()
        self.display_health()

    def constrain_screen(self):
        if self.rect.right >= 1280:
            self.rect.right = 1280
        elif self.rect.left <= 0:
            self.rect.left = 0

    def display_health(self):
        for index, shield in enumerate(range(self.health)):
            screen.blit(self.shield_surface, (index * 40 + 10, 10))

    def get_damage(self, damage_amount):
        self.health -= damage_amount

    def get_shield(self, recovery_amount):
        self.health += recovery_amount

    def charge(self):
        self.image = self.charged
            
    def discharge(self):
        self.image = self.uncharged

# Meteor Sprite  ----------------------------

class Meteor(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos, x_speed, y_speed):
        super().__init__()
        self.x_speed = x_speed
        self.y_speed = y_speed

        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center = (x_pos, y_pos))

    def update(self):
        self.rect.centerx += self.x_speed
        self.rect.centery += self.y_speed

        #self.rect.bottom += self.x_speed
        #self.rect.right += self.x_speed
        if self.rect.centery == 800:
            self.kill()

# Laser and Item Sprites  ------------------------------

class Laser(pygame.sprite.Sprite):
    def __init__(self, path, pos, speed, dir='up', acc_speed=None):
        super().__init__()
        self.speed = speed
        self.dir = dir
        self.acc_speed = acc_speed

        self.image = pygame.image.load(path)
        self.rotated_left = pygame.transform.rotate(self.image, 30)
        self.rotated_right = pygame.transform.rotate(self.image, -30)

        self.rect = self.image.get_rect(center = pos)

        if self.dir == 'right':
            self.rect.centery -= 30

    def update(self):
        if self.dir == 'left':
            self.rect.centerx -= self.acc_speed 
        elif self.dir == 'right':
            self.rect.centerx += self.acc_speed

        self.rect.centery -= self.speed

        if self.rect.centery <= -50: #-100
            self.kill()

    def rotate_left(self):
        self.image = self.rotated_left

    def rotate_right(self):
        self.image = self.rotated_right

class LaserAccelerator(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos, x_speed, y_speed):
        super().__init__()
        self.x_speed = x_speed
        self.y_speed = y_speed

        self.image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.image, (200,200))
        self.rect = self.image.get_rect(center = (x_pos, y_pos))

    def update(self):
        self.rect.centerx += self.x_speed
        self.rect.centery += self.y_speed

        if self.rect.centery == 800:
            self.kill()

class Shield(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos, x_speed, y_speed):
        super().__init__()
        self.x_speed = x_speed
        self.y_speed = y_speed

        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center = (x_pos, y_pos))

    def update(self):
        self.rect.centerx += self.x_speed
        self.rect.centery += self.y_speed

        if self.rect.centery == 800:
            self.kill()

# ----------------------------------------------
pygame.init()

# Game setup
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
game_font = pygame.font.Font('./assets/fonts/LazenbyCompSmooth.ttf', 40)
game_font_2 = pygame.font.Font('./assets/fonts/LazenbyCompSmooth.ttf', 24)
score = 0
laser_timer = 0
laser_active = False
highest_score = 0
accelerator_active = False
accelerator_timer = 0
bg_slide_y = 0
game_state = "intro"
intro_loaded = False

pygame.mouse.set_visible(False)

# Rendering texts
intro_text_surface = game_font.render('Are you ready?', True, (255,255,255))
intro_text_surface_2 = game_font_2.render('Click to continue', True, (255,255,255))
  
intro_text_rect = intro_text_surface.get_rect(center = (640, 260))#320
intro_text_rect_2 = intro_text_surface_2.get_rect(center = (640, 400))

ending_text_surface = game_font.render('Game Over', True, (255,255,255))
ending_text_rect = ending_text_surface.get_rect(center = (640, 260)) #320

# Background surfaces
intro_bg = pygame.image.load('./assets/gfx/background_3.png').convert_alpha()
space_bg = pygame.image.load('./assets/gfx/background_6.png').convert_alpha()
end_bg = pygame.image.load('./assets/gfx/background_4.png').convert_alpha()

# Groups
spaceship = Spaceship(
    './assets/gfx/spaceship.png',
    './assets/gfx/spaceship_charged.png', 
    640, 
    500
)

spaceship_group = pygame.sprite.GroupSingle()
spaceship_group.add(spaceship)

meteor_group = pygame.sprite.Group()

laser_group = pygame.sprite.Group()

laser_acc_group = pygame.sprite.Group()

shield_group = pygame.sprite.Group()


# USEREVENTS
METEOR_EVENT = pygame.USEREVENT
pygame.time.set_timer(METEOR_EVENT, 150)

SHIELD_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SHIELD_EVENT, random.randint(6000, 10000))

ACCELERATOR_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(ACCELERATOR_EVENT, random.randint(15000, 18000))


# Game States
def intro():
    global intro_loaded

    intro_loaded = True

    screen.blit(intro_bg, (0,0))
    
    screen.blit(intro_text_surface, intro_text_rect)
    screen.blit(intro_text_surface_2, intro_text_rect_2)


def main_game():
    global laser_active
    global accelerator_active
    global accelerator_timer
    global bg_slide_y

    # Sliding background
    if bg_slide_y >= 720:
        #screen.blit(space_bg, (0, i-720)) #no + 1
        bg_slide_y = 0
    screen.blit(space_bg, (0, bg_slide_y))  # no+1
    screen.blit(space_bg, (0, bg_slide_y - 720)) # no+1
    bg_slide_y += .65

    laser_group.draw(screen)
    laser_group.update()

    laser_acc_group.draw(screen)
    laser_acc_group.update()

    spaceship_group.draw(screen)
    spaceship_group.update()
    
    meteor_group.draw(screen)
    meteor_group.update()

    shield_group.draw(screen)
    shield_group.update()

    if pygame.sprite.spritecollide(spaceship_group.sprite, meteor_group, True): # returns a list of collided sprites
        spaceship_group.sprite.get_damage(1)

    for laser_sprite in laser_group:
        pygame.sprite.spritecollide(laser_sprite, meteor_group, True)

    if spaceship_group.sprite.health < 5 and pygame.sprite.spritecollide(spaceship_group.sprite, shield_group, True):
        spaceship_group.sprite.get_shield(1)

    if pygame.sprite.spritecollide(spaceship_group.sprite, laser_acc_group, True): # returns a list of collided sprites
        accelerator_active = True
        accelerator_timer = pygame.time.get_ticks()

    # Laser timer for laser recharging
    if pygame.time.get_ticks() - laser_timer >= 1000: #200
        laser_active = True
        spaceship_group.sprite.charge()

    if pygame.time.get_ticks() - accelerator_timer >= 12000:
        accelerator_active = False

    return 1

def end_game():
    global highest_score
    global bg_slide_y

    bg_slide_y = 0

    if highest_score == 0 or score > highest_score:
        highest_score = score
       
    screen.blit(end_bg, (0,0))

    screen.blit(ending_text_surface, ending_text_rect)

    score_surface = game_font.render(f'###  Score: {score}  ###', True, (255,220,255))
    score_rect = score_surface.get_rect(center = (640, 340)) #400
    screen.blit(score_surface, score_rect)

    highest_score_surface = game_font.render(f'Highest Score: {highest_score}', True, (255,220,255))
    highest_score_rect = highest_score_surface.get_rect(center = (640, 460)) #520
    screen.blit(highest_score_surface, highest_score_rect)

# -----------------------------------------------------

# Game loop

while True:
    for event in pygame.event.get(): # check for event/player input
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == METEOR_EVENT and not intro_loaded:
            meteor_path = random.choice(('Meteor1.png', 'Meteor2.png', 'Meteor3.png'))
            meteor = Meteor(
                f'./assets/gfx/{meteor_path}', 
                random.randrange(0, 1280),   # x_pos
                random.randrange(-500, -50), # y_pod
                random.randrange(-1, 1),     # x_speed
                random.randrange(2, 5)       # y_speed
            )
            meteor_group.add(meteor)

        if event.type == pygame.MOUSEBUTTONDOWN and spaceship_group.sprite.health > 0 and laser_active and not intro_loaded:
            laser = Laser('./assets/gfx/laser.png', event.pos, 12)
            laser_group.add(laser)
            laser_active = False
            laser_timer = pygame.time.get_ticks()

            if accelerator_active:
                laser_rotated_left = Laser('./assets/gfx/laser.png', event.pos, 12, 'left', 8)
                laser_rotated_left.rotate_left()
                laser_group.add(laser_rotated_left)

                laser_rotated_right = Laser('./assets/gfx/laser.png', event.pos, 12, 'right', 8)
                laser_rotated_right.rotate_right()
                laser_group.add(laser_rotated_right)

            spaceship_group.sprite.discharge()

        # Restarting the game
        if event.type == pygame.MOUSEBUTTONDOWN and spaceship_group.sprite.health <= 0:
            spaceship_group.sprite.health = 5
            meteor_group.empty()
            shield_group.empty()
            laser_acc_group.empty()
            laser_active = False
            accelerator_active = False
            score = 0
            intro_loaded = False
            game_state = "intro"

        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "intro" and intro_loaded:
            game_state = "main"
            intro_loaded = False

        if event.type == SHIELD_EVENT and not intro_loaded:
            shield = Shield(
                './assets/gfx/shield.png',
                random.randrange(0, 1280),
                random.randrange(-500, -50),
                random.randrange(-1, 1),
                random.randrange(1, 4)
            )

            shield_group.add(shield)

        if event.type == ACCELERATOR_EVENT and not intro_loaded:
            laser_acc = LaserAccelerator(
                './assets/gfx/item_1.png',
                random.randrange(0, 1280),
                random.randrange(-500, -50),
                random.randrange(-1, 1),
                random.randrange(1, 4)
            )
            laser_acc_group.add(laser_acc)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            spaceship_group.sprite.health = 0
    #screen.fill((41,42,45)) # rgb color 
   
    if game_state == "intro":
        intro()
    else:
        if spaceship_group.sprite.health > 0:
            score += main_game()
        else:
            end_game()
 
    pygame.display.update() # draw frame
    clock.tick(120) # control the frame rate
    