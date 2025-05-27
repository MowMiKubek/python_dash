import pygame
import csv

pygame.init()

map_content = []
with open('data/map_objects.csv', 'r') as file:
    file_content = file.readlines()
    for line in file_content:
        map_content.append(line.split(','))

player_image = pygame.image.load('data/images/avatar.png')
player_image = pygame.transform.scale(player_image, (32, 32))

floor_image = pygame.image.load('data/images/block_1.png')
floor_image = pygame.transform.scale(floor_image, (32, 32))

spike_image = pygame.image.load('data/images/obj-spike.png')
spike_image = pygame.transform.scale(spike_image, (32, 32))

orb_image = pygame.image.load('data/images/orb-yellow.png')
orb_image = pygame.transform.scale(orb_image, (32, 32))

coin_image = pygame.image.load('data/images/coin.png')
coin_image = pygame.transform.scale(coin_image, (32, 32))

tileset_image = pygame.image.load('data/images/bg.png')

FPS = 60
BLOCK_SIZE = 32
SCREEN_HEIGHT = len(map_content) * BLOCK_SIZE
SCREEN_WIDTH = 2 * SCREEN_HEIGHT
HEIGHT = len(map_content)
WIDTH = 2 * HEIGHT

GROUND_Y = SCREEN_HEIGHT - 20
GRAVITY = 1
JUMP_SPEED = -15
OBSTACLE_SPEED = 5
SPAWN_DELAY = 1000
MAX_OFFSET_SPAWN_DELAY = 500

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)
GREEN = (0, 128, 0)

tiles = []
tileset_rows = tileset_image.get_height() // BLOCK_SIZE
tileset_cols = tileset_image.get_width() // BLOCK_SIZE

for row in range(tileset_rows):
    for col in range(tileset_cols):
        tile = tileset_image.subsurface((col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        tiles.append(tile)

with open("data/map_background.csv", "r") as file:
    reader = csv.reader(file)
    tilemap = [list(map(int, row)) for row in reader]

MAP_ROWS = len(tilemap)
MAP_COLS = len(tilemap[0])

background_surface = pygame.Surface((MAP_COLS * BLOCK_SIZE, MAP_ROWS * BLOCK_SIZE), pygame.SRCALPHA)
for row_idx, row in enumerate(tilemap):
    for col_idx, tile_idx in enumerate(row):
        tile_image = tiles[tile_idx]
        background_surface.blit(tile_image, (col_idx * BLOCK_SIZE, row_idx * BLOCK_SIZE))

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python Dash")
clock = pygame.time.Clock()

pygame.mixer.init()
pygame.mixer.music.load("data/music/music1.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.velocity = 0
        self.on_ground = True
        self.extra_jump = False

    def update(self, keys):
        if keys[pygame.K_SPACE]:
            self.jump()

        self.rect.y += self.velocity
        self.velocity += GRAVITY

        floor_collided_block = pygame.sprite.spritecollideany(self, floor_group)
        if floor_collided_block is not None:
            if self.velocity > 0:
                self.velocity = 0
                self.on_ground = True
                self.rect.bottom = floor_collided_block.rect.top
        else:
            self.on_ground = False

    def jump(self):
        if self.on_ground or self.extra_jump:
            self.velocity = JUMP_SPEED
            self.on_ground = False


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = spike_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, keys):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()


class Orb(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = orb_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, keys):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = coin_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, keys):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()

class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = floor_image
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


def show_game_over(window):
    pygame.mixer.music.fadeout(1000)
    font = pygame.font.SysFont(None, 72)
    text = font.render("Game over", True, WHITE)
    window.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 40))
    pygame.display.update()
    pygame.time.delay(3000)


def show_score(window, score):
    font = pygame.font.SysFont("Comic Sans MS", 48)
    text = font.render(f'Score: {score}', True, WHITE)
    window.blit(text, (0, 0))

def show_coin_count(window, score):
    for i in range(score):
        window.blit(coin_image, (300 + 40 * i, 16))


running = True

all_sprites = pygame.sprite.Group()
player = Player(3 * BLOCK_SIZE, SCREEN_HEIGHT - 5 * BLOCK_SIZE, BLOCK_SIZE)
obstacles = pygame.sprite.Group()
floor_group = pygame.sprite.Group()
orb_group = pygame.sprite.Group()
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
            orb = Orb(j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            orb_group.add(orb)
            all_sprites.add(orb)
        if cell == 'Coin':
            coin = Coin(j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            coin_group.add(coin)
            all_sprites.add(coin)

score = 0
coin_counter = 0
last_score_timestamp = pygame.time.get_ticks()

background_offset = 0
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

    if pygame.time.get_ticks() - last_score_timestamp > 1000:
        last_score_timestamp = pygame.time.get_ticks()
        score += 1

    window.fill(BLACK)
    window.blit(background_surface, (-background_offset, 0))
    all_sprites.draw(window)

    if pygame.sprite.spritecollideany(player, obstacles):
        running = False

    floor_hits = pygame.sprite.spritecollide(player, floor_group, False)
    for block in floor_hits:
        # collision from left
        if player.rect.right >= block.rect.left:
            running = False
        elif player.rect.top <= block.rect.bottom:
            running = False

    collided_obr = pygame.sprite.spritecollideany(player, orb_group)
    if collided_obr is not None:
        player.extra_jump = True
    else:
        player.extra_jump = False

    if pygame.sprite.spritecollide(player, coin_group, True):
        coin_counter += 1

    show_score(window, score)
    show_coin_count(window, coin_counter)

    all_sprites.update(keys)
    pygame.display.update()
    background_offset += OBSTACLE_SPEED

show_game_over(window)
pygame.quit()
