import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 288
screen_height = 512
screen = pygame.display.set_mode((screen_width, screen_height))

# Title
pygame.display.set_caption("Flappy Bird")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
sky_blue = (135, 206, 235)

# Bird
bird_x = 50
bird_y = 200
bird_width = 35
bird_height = 35
bird_velocity = 0
gravity = 0.25
bird_jump = -6

# Pipes
pipe_width = 70
pipe_gap = 150
pipe_list = []
pipe_color = (0, 255, 0)  # Green pipes
min_pipe_height = 50
max_pipe_height = screen_height - pipe_gap - min_pipe_height

# Game variables
score = 0
font = pygame.font.Font(None, 40)  # Default font, size 40

# Pipe creation
def create_pipe():
    random_pipe_pos = random.randint(min_pipe_height, max_pipe_height)
    bottom_pipe = pygame.Rect(screen_width, random_pipe_pos + pipe_gap, pipe_width, screen_height)
    top_pipe = pygame.Rect(screen_width, random_pipe_pos - screen_height, pipe_width, screen_height)
    return bottom_pipe, top_pipe

# Pipe movement
def move_pipes(pipes):
    for pipe in pipes:
        pipe.x -= 2
    return pipes

# Draw pipes
def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, pipe_color, pipe)

# Bird animation
def draw_bird(bird):
    pygame.draw.rect(screen, white, bird)

# Check for collisions
def check_collision(pipes):
    for pipe in pipes:
        if bird.colliderect(pipe):
            return True

    if bird.top <= 0 or bird.bottom >= screen_height:
        return True

    return False

# Display score
def display_score(score):
    score_surface = font.render(str(int(score)), True, white)
    score_rect = score_surface.get_rect(center=(screen_width // 2, 50))
    screen.blit(score_surface, score_rect)

# Game loop
running = True
clock = pygame.time.Clock()
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1400)  # Spawn pipes more frequently

bird = pygame.Rect(bird_x, bird_y, bird_width, bird_height)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_velocity = bird_jump
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

    # Bird movement
    bird_velocity += gravity
    bird_y += bird_velocity
    bird.y = bird_y

    # Pipe movement
    pipe_list = move_pipes(pipe_list)

    # Remove off-screen pipes
    pipe_list = [pipe for pipe in pipe_list if pipe.right > -pipe_width]

    # Check for collisions
    if check_collision(pipe_list):
        running = False

    # Score
    for pipe in pipe_list:
        if 95 < pipe.centerx < 105:  # Check if bird has passed the pipe
            score += 0.5  # Increase by 0.5 for each part of the pipe

    # Screen color
    screen.fill(sky_blue)

    # Draw pipes and bird
    draw_pipes(pipe_list)
    draw_bird(bird)

    # Display score
    display_score(score)

    # Update display
    pygame.display.update()
    clock.tick(60)

pygame.quit()
