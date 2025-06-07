import pygame
import math
import random

# ---------------------
# Initialization
# ---------------------
pygame.init()
WIDTH, HEIGHT = 900, 650
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Projectile Motion Demo")
clock = pygame.time.Clock()

# ---------------------
# Colors and Fonts
# ---------------------
# Define colors
WHITE     = (255, 255, 255)
BLACK     = (0, 0, 0)
DARKGREY  = (50, 50, 50)
LIGHTGREY = (200, 200, 200)
RED       = (230, 30, 30)
GREEN     = (30, 230, 30)
BLUE      = (50, 150, 255)
ORANGE    = (255, 165, 0)
YELLOW    = (255, 255, 0)

# Fonts
font = pygame.font.SysFont("Arial", 22)
info_font = pygame.font.SysFont("Verdana", 20, bold=True)

# ---------------------
# Utility: Draw Vertical Gradient
# ---------------------
def draw_gradient(surface, top_color, bottom_color):
    """Fill the surface with a vertical gradient from top_color to bottom_color."""
    height = surface.get_height()
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

# ---------------------
# Physics & Game Settings
# ---------------------
g = 300            # gravitational acceleration (pixels/s^2)
dt = 0.02          # simulation time step (seconds)
start_pos = (80, HEIGHT - 80)  # Launch point at bottom left (with some margin)

# Projectile and target settings
proj_radius = 10
target_radius = 25

# ---------------------
# Game State Variables
# ---------------------
game_state = "waiting"  # "waiting", "aiming", "launched", "finished"
projectile_pos = list(start_pos)
projectile_vel = (0, 0)
time_elapsed = 0

# Drag-and-shoot control
dragging = False
drag_start = None
drag_end = None

# Trail (particle system) – each particle is a dict with "pos" and "life"
trail_particles = []

# Score
score = 0

# Create a new target in a designated region
def create_target():
    x = random.randint(WIDTH // 2, WIDTH - target_radius - 20)
    y = random.randint(target_radius + 20, HEIGHT - 200)
    return (x, y)
target_pos = create_target()

# ---------------------
# Helper Functions
# ---------------------
def draw_text(text, pos, color=WHITE, font_obj=font):
    label = font_obj.render(text, True, color)
    win.blit(label, pos)

def physics_position(t, angle_deg, speed):
    """Return position (x, y) at time t given initial angle and speed."""
    theta = math.radians(angle_deg)
    x = start_pos[0] + speed * math.cos(theta) * t
    y = start_pos[1] - speed * math.sin(theta) * t + 0.5 * g * t**2
    return x, y

def physics_velocity(t, angle_deg, speed):
    """Return velocity (vx, vy) at time t given initial conditions."""
    theta = math.radians(angle_deg)
    vx = speed * math.cos(theta)
    vy = -speed * math.sin(theta) + g * t
    return vx, vy

def draw_trail():
    """Draw all particles in the trail."""
    for particle in trail_particles:
        pos = particle["pos"]
        life = particle["life"]
        alpha = max(0, min(255, int(life * 255)))
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        s.fill((ORANGE[0], ORANGE[1], ORANGE[2], alpha))
        win.blit(s, (int(pos[0] - 4), int(pos[1] - 4)))

def update_trail(dt):
    """Decrease life of particles and remove expired ones."""
    for particle in trail_particles:
        particle["life"] -= dt
    while trail_particles and trail_particles[0]["life"] <= 0:
        trail_particles.pop(0)

def reset_game():
    global game_state, projectile_pos, projectile_vel, time_elapsed, dragging, drag_start, drag_end, trail_particles, target_pos
    game_state = "waiting"
    projectile_pos = list(start_pos)
    projectile_vel = (0, 0)
    time_elapsed = 0
    dragging = False
    drag_start = None
    drag_end = None
    trail_particles = []
    target_pos = create_target()

def check_collision(p1, r1, p2, r2):
    """Determine if two circles at p1 and p2 with radii r1 and r2 intersect."""
    dist = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
    return dist <= (r1 + r2)

def draw_target(pos, radius):
    """Draw a simple solid target with border."""
    pygame.draw.circle(win, GREEN, pos, radius)
    pygame.draw.circle(win, DARKGREY, pos, radius, 2)

# ---------------------
# Main Loop
# ---------------------
running = True
while running:
    clock.tick(60)
    
    # Event Processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle drag-and-shoot controls via mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if game_state in ["waiting", "finished"]:
                if game_state == "finished":
                    reset_game()
                if math.hypot(mouse_pos[0]-start_pos[0], mouse_pos[1]-start_pos[1]) <= 20:
                    dragging = True
                    drag_start = mouse_pos
                    drag_end = mouse_pos
                    game_state = "aiming"

        if event.type == pygame.MOUSEMOTION:
            if dragging:
                drag_end = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                dragging = False
                dx = start_pos[0] - drag_end[0]
                dy = start_pos[1] - drag_end[1]
                power = math.hypot(dx, dy) * 2.5
                if power < 10:
                    power = 10
                angle = math.degrees(math.atan2(dy, dx))
                projectile_vel = (power * math.cos(math.radians(angle)),
                                  power * math.sin(math.radians(angle)))
                game_state = "launched"
                time_elapsed = 0

    # ---------------------
    # Update Simulation
    # ---------------------
    if game_state == "launched":
        time_elapsed += dt
        projectile_pos[0] = start_pos[0] + projectile_vel[0] * time_elapsed
        projectile_pos[1] = start_pos[1] + projectile_vel[1] * time_elapsed + 0.5 * g * time_elapsed**2

        trail_particles.append({"pos": tuple(projectile_pos), "life": 1.0})
        update_trail(dt)

        if projectile_pos[1] >= start_pos[1] or projectile_pos[0] > WIDTH or projectile_pos[0] < 0:
            game_state = "finished"

        if check_collision(projectile_pos, proj_radius, target_pos, target_radius):
            game_state = "finished"
            score += 1

    # ---------------------
    # Drawing
    # ---------------------
    draw_gradient(win, (135, 206, 235), WHITE)
    pygame.draw.rect(win, LIGHTGREY, (0, start_pos[1], WIDTH, HEIGHT-start_pos[1]))
    draw_target(target_pos, target_radius)
    draw_trail()
    
    shadow_offset = 4
    pygame.draw.circle(win, DARKGREY, (int(projectile_pos[0]+shadow_offset), int(projectile_pos[1]+shadow_offset)), proj_radius)
    pygame.draw.circle(win, RED, (int(projectile_pos[0]), int(projectile_pos[1])), proj_radius)

    if dragging and drag_start and drag_end:
        pygame.draw.aaline(win, BLUE, start_pos, drag_end, 4)
        s = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(s, (BLUE[0], BLUE[1], BLUE[2], 120), (20, 20), 20)
        win.blit(s, (drag_end[0]-20, drag_end[1]-20))
    
    pygame.draw.circle(win, BLACK, start_pos, 12)
    pygame.draw.circle(win, LIGHTGREY, start_pos, 10)
    
    # ---------------------
    # Real-Time Physics Info
    # ---------------------
    info_lines = []
    if game_state in ["aiming", "waiting"]:
        if dragging and drag_start and drag_end:
            dx = start_pos[0] - drag_end[0]
            dy = start_pos[1] - drag_end[1]
            power = math.hypot(dx, dy) * 2.5
            aim_angle = math.degrees(math.atan2(dy, dx))
            info_lines.append(f"Aim Angle: {aim_angle:.1f}°")
            info_lines.append(f"Power: {power:.1f} px/s")
        else:
            info_lines.append("Drag from the launch point")
            info_lines.append("to set direction and power.")
    elif game_state in ["launched", "finished"]:
        speed = math.hypot(projectile_vel[0], projectile_vel[1])
        launch_angle = math.degrees(math.atan2(projectile_vel[1], projectile_vel[0]))
        vx, vy = physics_velocity(time_elapsed, launch_angle, speed)
        info_lines.append(f"Angle: {launch_angle:.1f}°")
        info_lines.append(f"Speed: {speed:.1f} px/s")
        info_lines.append(f"Time: {time_elapsed:.2f} s")
        info_lines.append(f"vx: {vx:.1f}  vy: {vy:.1f}")
        if game_state == "finished":
            if check_collision(projectile_pos, proj_radius, target_pos, target_radius):
                info_lines.append("Target Hit!")
            else:
                info_lines.append("Missed!")
            info_lines.append("Click to reset.")

    info_box = pygame.Surface((240, len(info_lines)*30 + 10), pygame.SRCALPHA)
    info_box.fill((255, 255, 255, 200))
    win.blit(info_box, (WIDTH - 250, 10))
    for i, line in enumerate(info_lines):
        text_surface = info_font.render(line, True, BLACK)
        win.blit(text_surface, (WIDTH - 240, 15 + i * 30))
    
    draw_text(f"Score: {score}", (10, 10), BLACK, font)

    pygame.display.update()

    if game_state == "finished" and pygame.mouse.get_pressed()[0] and not dragging:
        reset_game()

pygame.quit()
sys.exit()
