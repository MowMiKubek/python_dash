import pygame

pygame.init()

map_content = []
with open('data/map.csv', 'r') as file:
    file_content = file.readlines()
    for line in file_content:
        map_content.append(line.split(','))

BLOCK_SIZE = 30
SCREEN_HEIGHT = len(map_content) * BLOCK_SIZE
SCREEN_WIDTH = 2 * SCREEN_HEIGHT

HEIGHT = len(map_content)
WIDTH = 2 * HEIGHT

FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)
GREEN = (0, 128, 0)

GROUND_Y = SCREEN_HEIGHT - 20
GRAVITY = 1
JUMP_SPEED = -15
OBSTACLE_SPEED = 5
SPAWN_DELAY = 1000
MAX_OFFSET_SPAWN_DELAY = 500

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python Dash")
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.velocity = 0
        self.on_ground = True

    def update(self, keys):
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity = JUMP_SPEED
            self.on_ground = False

        # if self.rect.bottom >= GROUND_Y:
        floor_collided_block = pygame.sprite.spritecollideany(self, floor_group)
        if floor_collided_block is not None:
            self.velocity = 0
            self.on_ground = True
            self.rect.top = floor_collided_block.rect.top - BLOCK_SIZE
        # if not pygame.sprite.spritecollideany(self, floor_group):
        else:
            self.rect.y += self.velocity
            self.velocity += GRAVITY


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, keys):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, keys):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()


class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, keys):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()


def draw_debug_grid(window):
    for row in range(HEIGHT):
        for col in range(WIDTH):
            rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(window, WHITE, rect, 1)


running = True

all_sprites = pygame.sprite.Group()
player = Player(3 * BLOCK_SIZE, 0, BLOCK_SIZE)
obstacles = pygame.sprite.Group()
floor_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

all_sprites.add(player)

for i, row in enumerate(map_content):
    for j, cell in enumerate(row):
        if cell == 'Spike':
            obstacle = Obstacle(j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            obstacles.add(obstacle)
            all_sprites.add(obstacle)
        if cell == '0':
            floor = Floor(j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            floor_group.add(floor)
            all_sprites.add(floor)
        if cell == 'Orb':
            coin = Coin(j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            coin_group.add(coin)
            all_sprites.add(coin)

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
        pass

    all_sprites.update(keys)
    pygame.display.update()

pygame.quit()
