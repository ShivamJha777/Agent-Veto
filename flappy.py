import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Game variables
gravity = 0.5
bird_movement = 0
game_active = True
score = 0

# Bird setup
bird_rect = pygame.Rect(50, HEIGHT // 2, 30, 30)

# Pipe setup
pipe_width = 70
pipe_height = random.randint(150, 450)
pipe_gap = 200
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)

# Font
font = pygame.font.Font(None, 50)

def draw_bird():
    pygame.draw.rect(screen, BLACK, bird_rect)

def create_pipe():
    random_height = random.randint(150, 450)
    bottom_pipe = pygame.Rect(WIDTH, random_height, pipe_width, HEIGHT - random_height)
    top_pipe = pygame.Rect(WIDTH, 0, pipe_width, random_height - pipe_gap)
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, pipe)

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= -50 or bird_rect.bottom >= HEIGHT:
        return False
    return True

def display_score():
    score_surface = font.render(f'Score: {score}', True, BLACK)
    screen.blit(score_surface, (10, 10))

# Game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 10
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (50, HEIGHT // 2)
                bird_movement = 0
                score = 0
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

    screen.fill(WHITE)

    if game_active:
        # Bird movement
        bird_movement += gravity
        bird_rect.centery += bird_movement
        draw_bird()

        # Pipe movement
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Collision
        game_active = check_collision(pipe_list)

        # Score
        pipe_list = [pipe for pipe in pipe_list if pipe.centerx > -50]
        score += 0.01

    display_score()

    pygame.display.update()
    clock.tick(60)