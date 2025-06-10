import os
import pygame
import csv

pygame.init()

maps_filename_list = []

for obj in os.listdir('data/maps'):
    fullname = os.path.join('data/maps/', obj)
    if os.path.isdir(fullname) and len(os.listdir(fullname)) > 0:
        maps_filename_list.append(obj)

tileset_image = pygame.image.load('data/images/bg.png')
WIDTH, HEIGHT = tileset_image.get_size()
window = pygame.display.set_mode((WIDTH, HEIGHT))

font_header = pygame.font.SysFont('Comic Sans MS', 56)
font_item = pygame.font.SysFont('Comic Sams MS', 48)

menu_text = font_header.render("Select Map", True, (255, 255, 255))
menu_rect = menu_text.get_rect()
menu_rect.center = (WIDTH / 2, HEIGHT / 4)

selected_idx = 0
offset = 0
selecting = True
while selecting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                selecting = False
            if event.key == pygame.K_UP:
                if selected_idx == 0:
                    continue
                selected_idx -= 1
                print(selected_idx + 1)
                if selected_idx - offset < 0:
                    offset -= 1
            if event.key == pygame.K_DOWN:
                if selected_idx == len(maps_filename_list) - 1:
                    selected_idx = 0
                    offset = 0
                    continue
                selected_idx += 1
                print(selected_idx + 1)
                if selected_idx - offset >= 3:
                    offset += 1

    window.blit(tileset_image, (0, 0))
    window.blit(menu_text, menu_rect)

    for i, filename in enumerate(maps_filename_list[offset:offset+3]):
        selection_mark = "*" if i == selected_idx - offset else ""
        item_text = font_header.render(f'{selection_mark}{i+offset+1}. {filename}', True, (255, 255, 255))
        item_rect = item_text.get_rect()
        item_rect.center = (WIDTH / 2, HEIGHT / 2 + i*80)
        window.blit(item_text, item_rect)

    pygame.display.update()


map_folder_name = maps_filename_list[selected_idx]

map_content = []
with open(f'data/maps/{map_folder_name}/map_objects.csv', 'r') as file:
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
PLAYER_SPEED = 0
SPAWN_DELAY = 1000
MAX_OFFSET_SPAWN_DELAY = 500

VOLUME_MESSAGE_DURATION = 1000
MIN_VOLUME = 0
MAX_VOLUME = 100
VOLUME_TICK = 5

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

with open(f'data/maps/{map_folder_name}/map_background.csv', "r") as file:
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

volume = 0

pygame.mixer.init()
pygame.mixer.music.load("data/music/music1.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(volume / 100)


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

        self.rect.x += PLAYER_SPEED

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
    text = font.render("Victory" if victory else "Game over", True, WHITE)
    window.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 40))
    pygame.display.update()
    pygame.time.delay(3000)


def show_score(window, score):
    font = pygame.font.SysFont("Comic Sans MS", 48)
    text = font.render(f'Score: {score}', True, WHITE)
    window.blit(text, (0, 0))


volume_change_timestamp = pygame.time.get_ticks() - 1000


def show_volume(window, volume):
    font = pygame.font.SysFont("Comic Sans MS", 40)
    text = font.render(f'Volume: {volume}%', True, WHITE)
    duration = pygame.time.get_ticks() - volume_change_timestamp
    fraction = (VOLUME_MESSAGE_DURATION - duration) / VOLUME_MESSAGE_DURATION
    if fraction < 0:
        fraction = 0
    text.set_alpha(fraction * 256)
    window.blit(text, (SCREEN_WIDTH - text.get_rect().width, 0))


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

victory = False
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
        if event.type == pygame.MOUSEWHEEL:
            volume_change_timestamp = pygame.time.get_ticks()
            distance = event.y
            volume += distance * VOLUME_TICK
            if volume > MAX_VOLUME:
                volume = MAX_VOLUME
            if volume < MIN_VOLUME:
                volume = MIN_VOLUME
            pygame.mixer.music.set_volume(volume / 100)

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

    if player.rect.right >= SCREEN_WIDTH:
        running = False
        victory = True

    collided_obr = pygame.sprite.spritecollideany(player, orb_group)
    if collided_obr is not None:
        player.extra_jump = True
    else:
        player.extra_jump = False

    if pygame.sprite.spritecollide(player, coin_group, True):
        coin_counter += 1

    show_score(window, score)
    show_volume(window, volume)
    show_coin_count(window, coin_counter)

    all_sprites.update(keys)
    pygame.display.update()
    background_offset += OBSTACLE_SPEED
    if background_offset > background_surface.get_width() - SCREEN_WIDTH and OBSTACLE_SPEED > 0:
        PLAYER_SPEED = OBSTACLE_SPEED
        OBSTACLE_SPEED = 0

show_game_over(window)
pygame.quit()
