import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vector Shooting Game with Targets")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Player setup
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_speed = 5
player_radius = 15

# Bullets list
bullets = []
bullet_speed = 10
bullet_radius = 5

# Targets setup
targets = []
target_radius = 20
target_spawn_time = 2000  # milliseconds
last_spawn_time = pygame.time.get_ticks()

# Score
score = 0
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Math data
latest_direction = pygame.Vector2(0, 0)
latest_distance = None

# Game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Shoot bullet on mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            latest_direction = (mouse_pos - player_pos).normalize()
            bullets.append([player_pos.copy(), latest_direction])

    # Player movement
    keys = pygame.key.get_pressed()
    move = pygame.Vector2(0, 0)
    if keys[pygame.K_w]:
        move.y -= 1
    if keys[pygame.K_s]:
        move.y += 1
    if keys[pygame.K_a]:
        move.x -= 1
    if keys[pygame.K_d]:
        move.x += 1
    if move.length_squared() > 0:
        move = move.normalize() * player_speed
    player_pos += move

    # Spawn targets
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time > target_spawn_time:
        target_x = random.randint(target_radius, WIDTH - target_radius)
        target_y = random.randint(target_radius, HEIGHT - target_radius)
        targets.append(pygame.Vector2(target_x, target_y))
        last_spawn_time = current_time

    # Update and draw bullets
    latest_distance = None
    for bullet in bullets[:]:
        bullet[0] += bullet[1] * bullet_speed

        # Remove bullets out of screen
        if bullet[0].x < 0 or bullet[0].x > WIDTH or bullet[0].y < 0 or bullet[0].y > HEIGHT:
            bullets.remove(bullet)
            continue

        pygame.draw.circle(screen, RED, bullet[0], bullet_radius)

        # Bullet-target collision
        for target in targets[:]:
            distance = bullet[0].distance_to(target)
            if distance < bullet_radius + target_radius:
                targets.remove(target)
                bullets.remove(bullet)
                score += 1
                break
            elif distance < 300:
                if latest_distance is None or distance < latest_distance:
                    latest_distance = distance

    # Draw player
    pygame.draw.circle(screen, WHITE, player_pos, player_radius)

    # Draw shooting line to mouse position
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    pygame.draw.line(screen, BLUE, player_pos, mouse_pos, 2)

    # Draw targets
    for target in targets:
        pygame.draw.circle(screen, GREEN, target, target_radius)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Display math values
    pygame.draw.rect(screen, GRAY, (10, HEIGHT - 100, WIDTH - 20, 90))
    math_texts = [
        f"Movement Vector: ({move.x:.2f}, {move.y:.2f})",
        f"Bullet Direction Vector: ({latest_direction.x:.2f}, {latest_direction.y:.2f})",
        f"Last Bullet-Target Distance: {latest_distance:.2f}" if latest_distance is not None else "Last Bullet-Target Distance: N/A"
    ]
    for i, line in enumerate(math_texts):
        text_surf = small_font.render(line, True, WHITE)
        screen.blit(text_surf, (20, HEIGHT - 90 + i * 22))

    pygame.display.flip()

pygame.quit()
sys.exit()