import pygame, sys, random

# Sprite classes - we need to add them to groups

# Spaceship Sprite  ---------------------------

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos):
        super().__init__()
        self.uncharged = pygame.image.load(path)
        self.charged = pygame.image.load('./assets/spaceship_charged.png')

        self.image = self.uncharged
        self.rect = self.image.get_rect(center = (x_pos, y_pos))

        self.shield_surface = pygame.image.load('./assets/shield.png')
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
        if self.health < 5:
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

# Laser Sprite  ------------------------------

class Laser(pygame.sprite.Sprite):
    def __init__(self, path, pos, speed):
        super().__init__()
        self.speed = speed

        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center = pos)

    def update(self):
        self.rect.centery -= self.speed

        if self.rect.centery <= -100:
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
game_font = pygame.font.Font('./assets/LazenbyCompSmooth.ttf', 40)
score = 0
laser_timer = 0
laser_active = False

pygame.mouse.set_visible(False)

# Groups
spaceship = Spaceship('./assets/spaceship.png', 640, 500)
spaceship_group = pygame.sprite.GroupSingle()
spaceship_group.add(spaceship)

meteor_group = pygame.sprite.Group()

laser_group = pygame.sprite.Group()

shield_group = pygame.sprite.Group()

METEOR_EVENT = pygame.USEREVENT
pygame.time.set_timer(METEOR_EVENT, 150) #100

SHIELD_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SHIELD_EVENT, 8000)

# main-game & end_game stages
def main_game():
    global laser_active
    
    laser_group.draw(screen)
    laser_group.update()

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

    if pygame.sprite.spritecollide(spaceship_group.sprite, shield_group, True):
        spaceship_group.sprite.get_shield(1)
    # Laser timer for laser recharging
    if pygame.time.get_ticks() - laser_timer >= 1000: #200
        laser_active = True
        spaceship_group.sprite.charge()

    return 1

def end_game():
    text_surface = game_font.render('Game Over', True, (255,255,255))
    text_rect = text_surface.get_rect(center = (640, 320))
    screen.blit(text_surface, text_rect)

    score_surface = game_font.render(f'Score: {score}', True, (255,220,255))
    score_rect = score_surface.get_rect(center = (640, 400))
    screen.blit(score_surface, score_rect)

# -----------------------------------------------------

# Game loop

while True:
    for event in pygame.event.get(): # check for event/player input
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == METEOR_EVENT:
            meteor_path = random.choice(('Meteor1.png', 'Meteor2.png', 'Meteor3.png'))
            meteor = Meteor(
                f'./assets/{meteor_path}', 
                random.randrange(0, 1280),   # x_pos
                random.randrange(-500, -50), # y_pod
                random.randrange(-1, 1),     # x_speed
                random.randrange(2, 5)       # y_speed
            )
            meteor_group.add(meteor)

        if event.type == pygame.MOUSEBUTTONDOWN and spaceship_group.sprite.health > 0 and laser_active:
            laser = Laser('./assets/laser.png', event.pos, 12)
            laser_group.add(laser)
            laser_active = False
            laser_timer = pygame.time.get_ticks()

            spaceship_group.sprite.discharge()

        if event.type == pygame.MOUSEBUTTONDOWN and spaceship_group.sprite.health <= 0:
            spaceship_group.sprite.health = 5
            meteor_group.empty()
            score = 0

        if event.type == SHIELD_EVENT:
            shield = Shield(
                './assets/shield.png',
                random.randrange(0, 1280),
                random.randrange(-500, -50),
                random.randrange(-1, 1),
                random.randrange(1, 4)
            )

            shield_group.add(shield)

    screen.fill((41,42,45)) # rgb color

    if spaceship_group.sprite.health > 0:
        score += main_game()
    else:
        end_game()
 
    pygame.display.update() # draw frame
    clock.tick(120) # control the frame rate