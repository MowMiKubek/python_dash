import pygame

pygame.init()

WIDTH, HEIGHT = 800, 400
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

GROUND_Y = HEIGHT - 20
GRAVITY = 1
JUMP_SPEED = -15
OBSTACLE_SPEED = 5


window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Dash")
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.velocity = 0
        self.on_ground = True

    def update(self, keys):
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity = JUMP_SPEED
            self.on_ground = False

        self.rect.y += self.velocity
        self.velocity += GRAVITY

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.velocity = 0
            self.on_ground = True


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, GROUND_Y)

    def update(self, keys):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()


running = True

all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

player = Player(100, HEIGHT - 40, 25)
all_sprites.add(player)

obstacle = Obstacle(WIDTH - 40, 25, 25)
obstacles.add(obstacle)
all_sprites.add(obstacle)

while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    window.fill(BLACK)
    all_sprites.draw(window)

    if pygame.sprite.spritecollideany(player, obstacles):
        running = False

    all_sprites.update(keys)
    pygame.display.update()

pygame.quit()
