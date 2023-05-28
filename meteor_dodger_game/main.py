import pygame, sys, random
from openal import *

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
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.image = pygame.image.load(path)
        self.img_size = random.randint(60, 110)
        self.is_giant = False

        low_probability_choice = random.choice(range(180))
        if low_probability_choice == 0:
            self.img_size = random.randint(200, 300)
            self.is_giant = True 

        self.image = pygame.transform.scale(self.image, (self.img_size, self.img_size))
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))

    def update(self):
        self.rect.centerx += self.x_speed
        self.rect.centery += self.y_speed

        #self.rect.bottom += self.x_speed
        #self.rect.right += self.x_speed
        if self.rect.centery == 800:
            self.kill()

# Laser and Item Sprites  ------------------------------

class Laser(pygame.sprite.Sprite):
    def __init__(self, path, pos, speed, direction='up', speed_enhanced=None):
        super().__init__()
        self.speed = speed
        self.direction = direction
        self.speed_enhanced = speed_enhanced

        self.image = pygame.image.load(path)
        self.rotated_left = pygame.transform.rotate(self.image, 30)
        self.rotated_right = pygame.transform.rotate(self.image, -30)

        self.rect = self.image.get_rect(center = pos)

        if self.direction == 'right':
            self.rect.centery -= 30

    def update(self):
        if self.direction == 'left':
            self.rect.centerx -= self.speed_enhanced 
        elif self.direction == 'right':
            self.rect.centerx += self.speed_enhanced

        self.rect.centery -= self.speed

        if self.rect.centery <= -50: #-100
            self.kill()

    def rotate_left(self):
        self.image = self.rotated_left

    def rotate_right(self):
        self.image = self.rotated_right


class Booster(pygame.sprite.Sprite):
    def __init__(self, path, booster_type, x_pos, y_pos, x_speed, y_speed):
        super().__init__()
        self.x_speed = x_speed
        self.y_speed = y_speed

        self.image = pygame.image.load(path)
        if booster_type == 1:
            self.image = pygame.transform.scale(self.image, (200,200))
        elif booster_type == 0:
            self.image = pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect(center = (x_pos, y_pos))

    def update(self):
        self.rect.centerx += self.x_speed
        self.rect.centery += self.y_speed

        if self.rect.centery == 800:
            self.kill()

class Animation(pygame.sprite.Sprite):
    def __init__(self, x, y, img_name, img_range, size):
        super().__init__()
        self.images = []

        for num in img_range:
            exp_img = pygame.image.load(f'./assets/gfx/animation/{img_name}{num}.png').convert_alpha()
            exp_img = pygame.transform.scale(exp_img, size)
            self.images.append(exp_img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x,y))
        #self.rect.center = [x,y]
        self.counter = 0

    def update(self):
        exp_speed = 4
        self.counter += 1

        if self.counter >= exp_speed and self.index < len(self.images) - 1:
            self.index += 1
            self.image = self.images[self.index]
            self.counter = 0

        if self.counter >= exp_speed and self.index >= len(self.images) - 1:
            self.kill()

# ----------------------------------------------
pygame.init()

## Game setup
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

# SFX
intro_sound = oalOpen('./assets/sfx/intro.wav')
main_sound = oalOpen('./assets/sfx/slow_travel.wav')
crash_sound = oalOpen('./assets/sfx/crash.wav')
booster_sound = oalOpen('./assets/sfx/booster.wav')
end_sound = oalOpen('./assets/sfx/futuristic.wav')

oal_listener = oalGetListener() 
oal_listener.set_gain(.2)
intro_sound.play()

for sound in [intro_sound, main_sound]:
    sound.set_looping(True)

game_font = pygame.font.Font('./assets/fonts/LazenbyCompSmooth.ttf', 40)
game_font_2 = pygame.font.Font('./assets/fonts/LazenbyCompSmooth.ttf', 24)

score = 0
score_visible = 0
laser_timer = 0
laser_active = False
highest_score = 0
booster_active = False
booster_timer = 0
bg_slide_y = 0
game_state = "intro"
intro_loaded = False

pygame.mouse.set_visible(False)

# Rendering texts
intro_text_surface = game_font.render('Are you ready?', True, (255,255,255))
intro_text_surface_2 = game_font_2.render('Press the Spacebar to play', True, (255,255,255))
  
intro_text_rect = intro_text_surface.get_rect(center = (640, 260))#320
intro_text_rect_2 = intro_text_surface_2.get_rect(center = (640, 400))

ending_text_surface = game_font.render('You\'re a space hero !', True, (255,255,255))
ending_text_surface_2 = game_font_2.render('Press the Spacebar to play again', True, (255,255,255))

ending_text_rect = ending_text_surface.get_rect(center = (640, 260)) #320
ending_text_rect_2 = ending_text_surface_2.get_rect(center = (640, 620))

score_label = game_font_2.render('Score', True, (255,255,255))
score_label_rect = score_label.get_rect(center=(1225, 25))

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

laser_booster_group = pygame.sprite.Group()

shield_group = pygame.sprite.Group()

animation_group = pygame.sprite.Group()

# USEREVENTS
METEOR_EVENT = pygame.USEREVENT
pygame.time.set_timer(METEOR_EVENT, 150)

SHIELD_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SHIELD_EVENT, random.randint(6000, 10000))

LASER_BOOSTER_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(LASER_BOOSTER_EVENT, random.randint(14000, 19000))


# Game States
def intro():
    global intro_loaded

    intro_loaded = True

    screen.blit(intro_bg, (0,0))
    
    screen.blit(intro_text_surface, intro_text_rect)
    screen.blit(intro_text_surface_2, intro_text_rect_2)


def main_game():
    global laser_active
    global booster_active
    global booster_timer
    global bg_slide_y
    global score_visible
    # Sliding background
    if bg_slide_y >= 720:
        #screen.blit(space_bg, (0, i-720)) #no + 1
        bg_slide_y = 0
    screen.blit(space_bg, (0, bg_slide_y))  # no+1
    screen.blit(space_bg, (0, bg_slide_y - 720)) # no+1
    bg_slide_y += .65

    laser_group.draw(screen)
    laser_group.update()

    laser_booster_group.draw(screen)
    laser_booster_group.update()

    spaceship_group.draw(screen)
    spaceship_group.update()
    
    meteor_group.draw(screen)
    meteor_group.update()

    shield_group.draw(screen)
    shield_group.update()

    animation_group.draw(screen)
    animation_group.update()

    if score % 50 == 0:
        score_visible = score
      
    score_surface = game_font_2.render(f'{score_visible}', True, (255,255,255))
    score_rect = score_surface.get_rect(center=(1225, 60))
    screen.blit(score_surface, score_rect)
    screen.blit(score_label, score_label_rect)

    for laser_sprite in laser_group:
        meteors = pygame.sprite.spritecollide(laser_sprite, meteor_group, True)

        if len(meteors) > 0:
            for meteor in meteors:
                explosion = Animation(
                    meteor.rect.x + 50, 
                    meteor.rect.y, 
                    'exp', 
                    range(1, 6),
                    (meteor.img_size, meteor.img_size)
                )
                animation_group.add(explosion)

    if pygame.sprite.spritecollide(spaceship_group.sprite, meteor_group, False): # returns a list of collided sprites
        meteors_collided = pygame.sprite.spritecollide(spaceship_group.sprite, meteor_group, True)
        
        for meteor in meteors_collided:
            if meteor.is_giant:
                spaceship_group.sprite.get_damage(2)
            else:
                spaceship_group.sprite.get_damage(1)
            
            crash = Animation(
                meteor.rect.x + 50, 
                meteor.rect.y + 50, 
                'exp', 
                range(1, 6),
                (meteor.img_size, meteor.img_size)
            )
            animation_group.add(crash)

            crash_sound.play()
        
        if spaceship_group.sprite.health <= 0:
            main_sound.stop()
            end_sound.play()
            
    if spaceship_group.sprite.health < 5 and pygame.sprite.spritecollide(spaceship_group.sprite, shield_group, False):
        shields = pygame.sprite.spritecollide(spaceship_group.sprite, shield_group, True)
       
        for shield in shields:
            particles = Animation(
                shield.rect.x, 
                shield.rect.y, 
                'particles', 
                range(1, 7),
                (220, 220)
            )
            animation_group.add(particles)
        
        spaceship_group.sprite.get_shield(1)
        booster_sound.play()

    if pygame.sprite.spritecollide(spaceship_group.sprite, laser_booster_group, False): # returns a list of collided sprites
        booster_active = True
        booster_timer = pygame.time.get_ticks()

        boosters = pygame.sprite.spritecollide(spaceship_group.sprite, laser_booster_group, True)
       
        for booster in boosters:
            particles_acc = Animation(
                booster.rect.x + 100, 
                booster.rect.y + 120, 
                'particles', 
                range(1, 7),
                (220, 220)
            )
            animation_group.add(particles_acc)
            
        booster_sound.play()

    # Laser timer for laser recharging
    if pygame.time.get_ticks() - laser_timer >= 1000: #200
        laser_active = True
        spaceship_group.sprite.charge()

    if pygame.time.get_ticks() - booster_timer >= 12000:
        booster_active = False

    return 1

def end_game():
    global highest_score
    global bg_slide_y

    bg_slide_y = 0

    if highest_score == 0 or score > highest_score:
        highest_score = score
       
    screen.blit(end_bg, (0,0))

    screen.blit(ending_text_surface, ending_text_rect)
    screen.blit(ending_text_surface_2, ending_text_rect_2)

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
            oalQuit()
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

            if booster_active:
                laser_rotated_left = Laser('./assets/gfx/laser.png', event.pos, 12, 'left', 8)
                laser_rotated_left.rotate_left()
                laser_group.add(laser_rotated_left)

                laser_rotated_right = Laser('./assets/gfx/laser.png', event.pos, 12, 'right', 8)
                laser_rotated_right.rotate_right()
                laser_group.add(laser_rotated_right)

            spaceship_group.sprite.discharge()

        # Restarting the game
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and spaceship_group.sprite.health <= 0:
            spaceship_group.sprite.health = 5
            meteor_group.empty()
            shield_group.empty()
            laser_booster_group.empty()
            laser_active = False
            booster_active = False
            score = 0
            intro_loaded = False
            game_state = "intro"

            intro_sound.play()
            end_sound.stop()

            for animation_sprite in animation_group:
                animation_sprite.kill()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_state == "intro" and intro_loaded:
            game_state = "main"
            intro_loaded = False

            intro_sound.stop()
            main_sound.play()

        if event.type == SHIELD_EVENT and not intro_loaded:
            shield = Booster(
                './assets/gfx/shield.png',
                0,
                random.randrange(0, 1280),
                random.randrange(-500, -50),
                random.randrange(-1, 1),
                random.randrange(1, 4)
            )

            shield_group.add(shield)

        if event.type == LASER_BOOSTER_EVENT and not intro_loaded:
            laser_booster = Booster(
                './assets/gfx/booster.png',
                1,
                random.randrange(0, 1280),
                random.randrange(-500, -50),
                random.randrange(-1, 1),
                random.randrange(1, 4)
            )
            laser_booster_group.add(laser_booster)

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
    