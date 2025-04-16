import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GROUND_HEIGHT = HEIGHT // 2
PLAYER_SIZE = 20
FPS = 60
CHUNK_WIDTH = WIDTH  # Width of each terrain chunk

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (34, 139, 34)
PLAYER_COLOR = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Fractal Terrain")
clock = pygame.time.Clock()


def generate_terrain_segment(start_x, end_x, start_y=None, end_y=None, roughness=0.5, max_displacement=200):
    """Generate a fractal terrain segment between start_x and end_x"""
    if start_y is None:
        start_y = GROUND_HEIGHT + random.randint(-50, 50)
    if end_y is None:
        end_y = GROUND_HEIGHT + random.randint(-50, 50)

    terrain = [(start_x, start_y), (end_x, end_y)]

    def midpoint_displacement(left, right, displacement):
        # Get midpoint
        mid_x = (left[0] + right[0]) / 2
        mid_y = (left[1] + right[1]) / 2

        # Displace midpoint vertically
        mid_y += random.uniform(-displacement, displacement)

        # Clamp the displacement
        mid_y = max(GROUND_HEIGHT - max_displacement,
                    min(GROUND_HEIGHT + max_displacement, mid_y))

        # Add the new point
        terrain.append((mid_x, mid_y))
        terrain.sort(key=lambda p: p[0])  # Keep points ordered by x-coordinate

        # Recursively apply to left and right segments
        new_displacement = displacement * roughness
        if new_displacement > 1:
            midpoint_displacement(left, (mid_x, mid_y), new_displacement)
            midpoint_displacement((mid_x, mid_y), right, new_displacement)

    # Start the recursion
    midpoint_displacement(terrain[0], terrain[-1], max_displacement)

    return terrain


# Initialize terrain
terrain_segments = []

# Generate initial terrain segments
for i in range(3):  # Generate 3 chunks to start
    start_x = i * CHUNK_WIDTH
    end_x = (i + 1) * CHUNK_WIDTH
    segment = generate_terrain_segment(start_x, end_x)
    terrain_segments.append(segment)

# Player position
player_x = 100
player_y = min([p[1] for segment in terrain_segments for p in segment
                if p[0] >= 95 and p[0] <= 105]) - PLAYER_SIZE

# Camera offset
camera_x = 0

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 20:
        player_x -= 5
    if keys[pygame.K_RIGHT]:
        player_x += 5

    # Update camera to follow player
    camera_x = player_x - WIDTH // 3

    # Generate new terrain segments as needed
    last_segment_end = terrain_segments[-1][-1][0]
    if player_x > last_segment_end - WIDTH:
        new_segment = generate_terrain_segment(
            last_segment_end,
            last_segment_end + CHUNK_WIDTH,
            terrain_segments[-1][-1][1],  # Continue from last segment's end height
            None
        )
        terrain_segments.append(new_segment)

        # Remove old segments that are far behind (memory management)
        if len(terrain_segments) > 3:
            terrain_segments.pop(0)

    # Find ground level below player
    player_ground_y = HEIGHT
    for segment in terrain_segments:
        for i in range(len(segment) - 1):
            x1, y1 = segment[i]
            x2, y2 = segment[i + 1]
            if x1 <= player_x <= x2:
                # Linear interpolation
                t = (player_x - x1) / (x2 - x1)
                player_ground_y = y1 + t * (y2 - y1)
                break

    # Keep player on ground
    player_y = player_ground_y - PLAYER_SIZE

    # Draw everything
    screen.fill(SKY_BLUE)

    # Draw terrain (only visible portions)
    for segment in terrain_segments:
        visible_points = [p for p in segment if -100 <= p[0] - camera_x <= WIDTH + 100]
        if len(visible_points) >= 2:
            pygame.draw.lines(screen, GROUND_COLOR, False,
                              [(p[0] - camera_x, p[1]) for p in visible_points], 3)

    # Draw player
    pygame.draw.rect(screen, PLAYER_COLOR,
                     (player_x - camera_x, player_y, PLAYER_SIZE, PLAYER_SIZE))

    # Draw explanation text
    font = pygame.font.SysFont('Arial', 16)
    text1 = font.render("Endless Fractal Terrain Generation", True, (0, 0, 0))
    text2 = font.render("Uses midpoint displacement algorithm", True, (0, 0, 0))
    text3 = font.render("Arrow keys to move", True, (0, 0, 0))

    screen.blit(text1, (10, 10))
    screen.blit(text2, (10, 30))
    screen.blit(text3, (10, 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()