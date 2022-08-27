import pygame, sys, random

# Sprite class - we need to add it to a group
class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos):
        super().__init__()
        self.image = pygame.image.load(path)
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
# ---------------------------------------------------
pygame.init()

screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

pygame.mouse.set_visible(False)

# Sprite Groups
spaceship = SpaceShip('./assets/spaceship.png', 640, 500)
spaceship_group = pygame.sprite.GroupSingle()
spaceship_group.add(spaceship)

#meteor1 = Meteor('./assets/Meteor1.png', 400, -100, 1, 4)
meteor_group = pygame.sprite.Group()
#meteor_group.add(meteor1)

laser_group = pygame.sprite.Group()

METEOR_EVENT = pygame.USEREVENT
pygame.time.set_timer(METEOR_EVENT, 150) #100
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
                random.randrange(2, 6)       # y_speed  #4-10 
            )
            meteor_group.add(meteor)
        if event.type == pygame.MOUSEBUTTONDOWN:
            laser = Laser('./assets/laser.png', event.pos, 12)
            laser_group.add(laser)

    screen.fill((41,42,45)) # rgb color

    laser_group.draw(screen)
    laser_group.update()

    spaceship_group.draw(screen)
    spaceship_group.update()
    
    meteor_group.draw(screen)
    meteor_group.update()

    pygame.display.update() # draw frame
    clock.tick(120) # control the framerate