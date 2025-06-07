import pygame
import random
import sys
import math
from pygame import gfxdraw

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
GOLD = (255, 215, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
PURPLE = (138, 43, 226)
ORANGE = (255, 140, 0)
TEAL = (0, 128, 128)
BRIGHT_RED = (255, 50, 50)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Critical Hit Probability Demo")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont("Arial", 32, bold=True)
normal_font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 16)
crit_font = pygame.font.SysFont("Arial", 32, bold=True)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 70
        self.health = 100
        self.max_health = 100
        self.crit_chance = 20  # 20% chance to crit
        self.min_damage = 10
        self.max_damage = 25
        self.crit_multiplier = 2.0
        self.animation_frames = 0
        self.is_attacking = False
        self.attack_target = None
        self.color = BLUE
        
    def draw(self, surface):
        # Draw the player
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw health bar
        bar_width = 70
        health_percent = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.x - 10, self.y - 20, bar_width, 10))
        pygame.draw.rect(surface, GREEN, (self.x - 10, self.y - 20, bar_width * health_percent, 10))
        pygame.draw.rect(surface, BLACK, (self.x - 10, self.y - 20, bar_width, 10), 1)
        
        # Show health value
        health_text = small_font.render(f"{self.health}/{self.max_health}", True, BLACK)
        surface.blit(health_text, (self.x - 5, self.y - 40))
    
    def attack(self, enemy):
        self.is_attacking = True
        self.animation_frames = 30  # Animation duration
        self.attack_target = enemy
        
        # Calculate random base damage for this attack
        base_damage = random.randint(self.min_damage, self.max_damage)
        
        # Calculate if this is a critical hit
        is_critical = random.randint(1, 100) <= self.crit_chance
        
        # Calculate final damage
        damage = base_damage
        if is_critical:
            damage = int(damage * self.crit_multiplier)
        
        return damage, is_critical, base_damage

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 70
        self.health = 100
        self.max_health = 100
        self.crit_chance = 10  # 10% chance to crit
        self.min_damage = 8
        self.max_damage = 20
        self.crit_multiplier = 1.5
        self.animation_frames = 0
        self.is_attacking = False
        self.attack_target = None
        self.color = RED
        
    def draw(self, surface):
        # Draw the enemy
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw health bar
        bar_width = 70
        health_percent = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.x - 10, self.y - 20, bar_width, 10))
        pygame.draw.rect(surface, GREEN, (self.x - 10, self.y - 20, bar_width * health_percent, 10))
        pygame.draw.rect(surface, BLACK, (self.x - 10, self.y - 20, bar_width, 10), 1)
        
        # Show health value
        health_text = small_font.render(f"{self.health}/{self.max_health}", True, BLACK)
        surface.blit(health_text, (self.x - 5, self.y - 40))
    
    def attack(self, player):
        self.is_attacking = True
        self.animation_frames = 30  # Animation duration
        self.attack_target = player
        
        # Calculate random base damage for this attack
        base_damage = random.randint(self.min_damage, self.max_damage)
        
        # Calculate if this is a critical hit
        is_critical = random.randint(1, 100) <= self.crit_chance
        
        # Calculate final damage
        damage = base_damage
        if is_critical:
            damage = int(damage * self.crit_multiplier)
        
        return damage, is_critical, base_damage

class DamageNumber:
    def __init__(self, x, y, damage, is_critical, base_damage=None):
        self.x = x
        self.y = y
        self.damage = damage
        self.base_damage = base_damage  # Store the base damage for display
        self.is_critical = is_critical
        self.lifetime = 60  # Frames
        self.color = BRIGHT_RED if is_critical else BLACK
        self.font_size = 32 if is_critical else 20
        self.font = pygame.font.SysFont("Arial", self.font_size, bold=is_critical)
        self.flash_timer = 10 if is_critical else 0
        self.flash_state = True
        
    def update(self):
        self.y -= 1
        self.lifetime -= 1
        
        # Handle flashing for critical hits
        if self.is_critical and self.flash_timer > 0:
            self.flash_timer -= 1
            if self.flash_timer % 2 == 0:
                self.flash_state = not self.flash_state
        
    def draw(self, surface):
        # Make text fade out as lifetime decreases
        alpha = min(255, int(255 * (self.lifetime / 60)))
        
        # For critical hits, create a glowing effect with background
        if self.is_critical:
            # Draw yellow glow behind the number
            glow_size = self.font_size + 10
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 0, 100), (glow_size, glow_size), glow_size)
            surface.blit(glow_surface, (self.x - glow_size + 10, self.y - glow_size + 10))
            
            # Use a larger, bold font
            if self.base_damage:
                damage_text = crit_font.render(f"{self.damage} ({self.base_damage}x{self.damage/self.base_damage:.1f})", True, BRIGHT_RED if self.flash_state else GOLD)
            else:
                damage_text = crit_font.render(f"{self.damage}", True, BRIGHT_RED if self.flash_state else GOLD)
        else:
            damage_text = self.font.render(f"{self.damage}", True, self.color)
        
        # Create a temporary surface with per-pixel alpha
        text_surface = pygame.Surface(damage_text.get_size(), pygame.SRCALPHA)
        
        # Blit the text onto the surface
        text_surface.blit(damage_text, (0, 0))
        
        # Apply the alpha
        text_surface.set_alpha(alpha)
        
        # Draw the text
        surface.blit(text_surface, (self.x - text_surface.get_width()//4, self.y))
        
        # Draw "CRITICAL" text if it's a critical hit
        if self.is_critical:
            # Create a background for better visibility
            crit_text = normal_font.render("CRITICAL!", True, BLACK)
            crit_width, crit_height = crit_text.get_size()
            
            # Create background with some padding
            padding = 5
            bg_surface = pygame.Surface((crit_width + padding*2, crit_height + padding*2))
            bg_surface.fill(GOLD)
            bg_surface.set_alpha(alpha)
            surface.blit(bg_surface, (self.x - crit_width//2 - padding, self.y - 25 - padding))
            
            # Create the text surface
            crit_surface = pygame.Surface(crit_text.get_size(), pygame.SRCALPHA)
            crit_surface.blit(crit_text, (0, 0))
            crit_surface.set_alpha(alpha)
            surface.blit(crit_surface, (self.x - crit_width//2, self.y - 25))

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surface = normal_font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class ProbabilityDisplay:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 300
        self.height = 200
        self.crit_history = []  # 1 for crit, 0 for normal
        self.max_history = 20
        self.damage_history = []  # Store damage values
        
    def add_hit(self, is_critical, damage):
        self.crit_history.append(1 if is_critical else 0)
        self.damage_history.append(damage)
        if len(self.crit_history) > self.max_history:
            self.crit_history.pop(0)
            self.damage_history.pop(0)
            
    def draw(self, surface, player_crit_chance, enemy_crit_chance, player_damage_range, enemy_damage_range):
        # Draw background
        pygame.draw.rect(surface, GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw title
        title_text = normal_font.render("Probability Statistics", True, BLACK)
        surface.blit(title_text, (self.x + 10, self.y + 10))
        
        # Draw player and enemy crit chances
        player_text = small_font.render(f"Player: {player_crit_chance}% crit, {player_damage_range[0]}-{player_damage_range[1]} dmg", True, BLUE)
        enemy_text = small_font.render(f"Enemy: {enemy_crit_chance}% crit, {enemy_damage_range[0]}-{enemy_damage_range[1]} dmg", True, RED)
        surface.blit(player_text, (self.x + 10, self.y + 40))
        surface.blit(enemy_text, (self.x + 10, self.y + 60))
        
        # Calculate actual crit rate
        if self.crit_history:
            actual_rate = sum(self.crit_history) / len(self.crit_history) * 100
            rate_text = small_font.render(f"Observed Crit Rate: {actual_rate:.1f}%", True, PURPLE)
            surface.blit(rate_text, (self.x + 10, self.y + 80))
            

        # Draw hit history
        history_y = self.y + 110
        history_text = small_font.render("Recent Hits:", True, BLACK)
        surface.blit(history_text, (self.x + 10, history_y))
        
        # Draw legend
        crit_legend = pygame.Rect(self.x + 10, history_y + 20, 12, 12)
        pygame.draw.rect(surface, BRIGHT_RED, crit_legend)
        pygame.draw.rect(surface, BLACK, crit_legend, 2)
        crit_text = small_font.render("= Critical Hit", True, BLACK)
        surface.blit(crit_text, (self.x + 25, history_y + 20))
        
        normal_legend_x = self.x + 120
        pygame.draw.circle(surface, TEAL, (normal_legend_x + 6, history_y + 26), 6)
        pygame.draw.circle(surface, BLACK, (normal_legend_x + 6, history_y + 26), 6, 2)
        normal_text = small_font.render("= Normal Hit", True, BLACK)
        surface.blit(normal_text, (normal_legend_x + 15, history_y + 20))
        
        # Draw the hit symbols
        start_y = history_y + 45
        symbols_per_row = 10
        for i, hit in enumerate(self.crit_history):
            row = i // symbols_per_row
            col = i % symbols_per_row
            
            symbol_x = self.x + 20 + (col * 25)
            symbol_y = start_y + (row * 25)
            
            if hit == 1:  # Critical
                # Draw square for crits with thick border and flashing effect
                pygame.draw.rect(surface, BRIGHT_RED, (symbol_x - 8, symbol_y - 8, 16, 16))
                pygame.draw.rect(surface, BLACK, (symbol_x - 8, symbol_y - 8, 16, 16), 2)
                
                # Add sparkle effect around critical hits
                for angle in range(0, 360, 90):
                    spark_x = symbol_x + int(12 * math.cos(math.radians(angle)))
                    spark_y = symbol_y + int(12 * math.sin(math.radians(angle)))
                    pygame.draw.line(surface, GOLD, (symbol_x, symbol_y), (spark_x, spark_y), 2)
            else:  # Normal hit
                # Draw circle for normal hits with thick border
                pygame.draw.circle(surface, TEAL, (symbol_x, symbol_y), 6)
                pygame.draw.circle(surface, BLACK, (symbol_x, symbol_y), 6, 2)

def draw_arrow(surface, start, end, color, width=2):
    pygame.draw.line(surface, color, start, end, width)
    # Calculate the angle of the line
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    # Calculate the points of the arrowhead
    arrow_size = 10
    arrow_points = [
        (end[0] - arrow_size * math.cos(angle - math.pi/6),
         end[1] - arrow_size * math.sin(angle - math.pi/6)),
        end,
        (end[0] - arrow_size * math.cos(angle + math.pi/6),
         end[1] - arrow_size * math.sin(angle + math.pi/6)),
    ]
    pygame.draw.polygon(surface, color, arrow_points)

def create_critical_effect(x, y, radius):
    # Create a surface for the critical hit effect
    effect_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    
    # Draw a yellow circle
    pygame.draw.circle(effect_surface, (255, 255, 0, 150), (radius, radius), radius)
    
    # Draw some lines radiating outward
    for angle in range(0, 360, 45):
        end_x = radius + int(radius * 0.8 * math.cos(math.radians(angle)))
        end_y = radius + int(radius * 0.8 * math.sin(math.radians(angle)))
        pygame.draw.line(effect_surface, (255, 140, 0, 200), (radius, radius), (end_x, end_y), 3)
    
    return effect_surface

def main():
    # Game objects
    player = Player(200, 300)
    enemy = Enemy(550, 300)
    
    # Buttons
    attack_button = Button(100, 450, 200, 50, "Attack", GREEN, (100, 255, 100))
    adjust_crit_button = Button(350, 450, 200, 50, "Adjust Crit Chance", BLUE, (100, 150, 255))
    reset_button = Button(600, 450, 100, 50, "Reset", GRAY, (220, 220, 220))
    
    # Probability display
    prob_display = ProbabilityDisplay(250, 50)
    
    # Game state
    player_turn = True
    game_over = False
    damage_numbers = []
    turn_count = 0
    message = ""
    message_timer = 0
    
    # Critical hit effects
    crit_effects = []
    
    # Attack buffer - time between player and enemy attacks
    attack_buffer = 0
    BUFFER_DURATION = 45  # Frames to wait between attacks
    
    # Main game loop
    running = True
    while running:
        # Process events
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True
        
        # Game logic
        if not game_over:
            # Handle button hover
            attack_button.check_hover(mouse_pos)
            adjust_crit_button.check_hover(mouse_pos)
            reset_button.check_hover(mouse_pos)
            
            # Handle button clicks
            if mouse_clicked:
                if attack_button.is_clicked(mouse_pos, mouse_clicked) and player_turn and not player.is_attacking and attack_buffer == 0:
                    # Player attacks
                    damage, is_critical, base_damage = player.attack(enemy)
                    
                    # Add to history
                    prob_display.add_hit(is_critical, damage)
                    
                    # Create damage number
                    damage_numbers.append(DamageNumber(enemy.x + enemy.width // 2, enemy.y, damage, is_critical, base_damage))
                    
                    # Add critical hit effect if critical
                    if is_critical:
                        crit_effects.append({
                            "surface": create_critical_effect(60, 60,  30),
                            "pos": (enemy.x + enemy.width // 2 - 30, enemy.y + enemy.height // 2 - 30),
                            "lifetime": 30
                        })
                    
                    # Apply damage
                    enemy.health = max(0, enemy.health - damage)
                    
                    # Set message
                    if is_critical:
                        message = f"Critical Hit! {base_damage} → {damage} damage!"
                    else:
                        message = f"Normal hit for {damage} damage."
                    message_timer = 120
                    
                    # Start buffer period
                    attack_buffer = BUFFER_DURATION
                    
                    # End turn
                    player_turn = False
                    turn_count += 1
                
                elif adjust_crit_button.is_clicked(mouse_pos, mouse_clicked):
                    # Cycle through different crit chance values
                    player.crit_chance = (player.crit_chance + 10) % 60
                    if player.crit_chance == 0:
                        player.crit_chance = 10
                
                elif reset_button.is_clicked(mouse_pos, mouse_clicked):
                    # Reset player and enemy
                    player.health = player.max_health
                    enemy.health = enemy.max_health
                    
                    # Reset turn and game state
                    player_turn = True
                    game_over = False
                    
                    # Clear animations and effects
                    damage_numbers.clear()
                    crit_effects.clear()
                    
                    # Reset turn count and attack buffer
                    turn_count = 0
                    attack_buffer = 0
                    attack_button.is_hovered = False  # Ensure button resets properly
                    
                    # Reset probability tracking
                    prob_display.crit_history.clear()
                    prob_display.damage_history.clear()
                    
                    # Reset message
                    message = "Game reset! Ready to play again."
                    message_timer = 120  # Display message for a bit longer

            
            # Handle animations
            if player.is_attacking:
                if player.animation_frames > 0:
                    player.animation_frames -= 1
                else:
                    player.is_attacking = False
            
            if enemy.is_attacking:
                if enemy.animation_frames > 0:
                    enemy.animation_frames -= 1
                else:
                    enemy.is_attacking = False
            
            # Update buffer timer
            if attack_buffer > 0:
                attack_buffer -= 1
            
            # Enemy turn
            if not player_turn and not enemy.is_attacking and enemy.health > 0 and attack_buffer == 0:
                # Enemy attacks after buffer period
                damage, is_critical, base_damage = enemy.attack(player)
                
                # Add to history
                prob_display.add_hit(is_critical, damage)
                
                # Create damage number
                damage_numbers.append(DamageNumber(player.x + player.width // 2, player.y, damage, is_critical, base_damage))
                
                # Add critical hit effect if critical
                if is_critical:
                    crit_effects.append({
                        "surface": create_critical_effect(60, 60, 30),
                        "pos": (player.x + player.width // 2 - 30, player.y + player.height // 2 - 30),
                        "lifetime": 30
                    })
                
                # Apply damage
                player.health = max(0, player.health - damage)
                
                # Set message
                if is_critical:
                    message = f"Enemy Critical Hit! {base_damage} → {damage} damage!"
                else:
                    message = f"Enemy hit you for {damage} damage."
                message_timer = 120
                
                # Start buffer period again
                attack_buffer = BUFFER_DURATION
                
                # End enemy turn
                player_turn = True
                turn_count += 1
            
            # Update damage numbers
            for damage_num in damage_numbers[:]:
                damage_num.update()
                if damage_num.lifetime <= 0:
                    damage_numbers.remove(damage_num)
            
            # Update critical effects
            for effect in crit_effects[:]:
                effect["lifetime"] -= 1
                if effect["lifetime"] <= 0:
                    crit_effects.remove(effect)
            
            # Check for game over
            if player.health <= 0:
                game_over = True
                message = "Game Over! You lost."
                message_timer = 180
            elif enemy.health <= 0:
                game_over = True
                message = "Victory! You won!"
                message_timer = 180
        
        # Drawing
        screen.fill(WHITE)
        
        # Draw UI elements
        title_text = title_font.render("Critical Hit Probability Demo", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))
        
        # Draw active player indicator (instead of text)
        if not game_over:
            if player_turn:
                # Draw blue arrow above player
                pygame.draw.polygon(screen, BLUE, [
                    (player.x + player.width // 2 - 10, player.y - 50),
                    (player.x + player.width // 2 + 10, player.y - 50),
                    (player.x + player.width // 2, player.y - 35)
                ])
            else:
                # Draw red arrow above enemy
                pygame.draw.polygon(screen, RED, [
                    (enemy.x + enemy.width // 2 - 10, enemy.y - 50),
                    (enemy.x + enemy.width // 2 + 10, enemy.y - 50),
                    (enemy.x + enemy.width // 2, enemy.y - 35)
                ])
        
        # Draw player and enemy
        player.draw(screen)
        enemy.draw(screen)
        
        # Draw critical hit effects
        for effect in crit_effects:
            # Make the effect pulse/fade
            alpha = int(255 * (effect["lifetime"] / 30))
            effect["surface"].set_alpha(alpha)
            screen.blit(effect["surface"], effect["pos"])
        
        # Draw attack animations
        if player.is_attacking:
            draw_arrow(screen, 
                      (player.x + player.width, player.y + player.height // 2),
                      (enemy.x, enemy.y + enemy.height // 2),
                      BLUE, 3)
        
        if enemy.is_attacking:
            draw_arrow(screen, 
                      (enemy.x, enemy.y + player.height // 2),
                      (player.x + player.width, player.y + enemy.height // 2),
                      RED, 3)
        
        # Draw damage numbers
        for damage_num in damage_numbers:
            damage_num.draw(screen)
        
        # Draw buttons if not game over
        if not game_over:
            attack_button.draw(screen)
            adjust_crit_button.draw(screen)
        reset_button.draw(screen)
        
        # Draw probability display
        prob_display.draw(screen, player.crit_chance, enemy.crit_chance, 
                         (player.min_damage, player.max_damage), 
                         (enemy.min_damage, enemy.max_damage))
        
        # Draw buffer indicator if in buffer period
        if attack_buffer > 0:
            buffer_percent = attack_buffer / BUFFER_DURATION
            buffer_width = 200 * buffer_percent
            pygame.draw.rect(screen, DARK_GRAY, (WIDTH // 2 - 100, 530, 200, 15))
            pygame.draw.rect(screen, PURPLE, (WIDTH // 2 - 100, 530, buffer_width, 15))
            pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 100, 530, 200, 15), 1)
            
            buffer_text = small_font.render("Action Delay", True, BLACK)
            screen.blit(buffer_text, (WIDTH // 2 - buffer_text.get_width() // 2, 550))
        
        # Draw message
        if message and message_timer > 0:
            message_timer -= 1
            
            # Give critical hit messages a special treatment
            if "Critical" in message:
                # Create a glowing background for the message
                message_text = normal_font.render(message, True, BLACK)
                text_width, text_height = message_text.get_size()
                
                # Background with padding
                padding = 10
                bg_rect = pygame.Rect(WIDTH // 2 - text_width // 2 - padding, 
                                    500 - padding, 
                                    text_width + padding * 2, 
                                    text_height + padding * 2)
                
                # Alternate colors for critical hit messages
                if (message_timer // 5) % 2 == 0:
                    pygame.draw.rect(screen, GOLD, bg_rect)
                else:
                    pygame.draw.rect(screen, ORANGE, bg_rect)
                
                pygame.draw.rect(screen, BLACK, bg_rect, 2)
                screen.blit(message_text, (WIDTH // 2 - text_width // 2, 500))
            else:
                message_text = normal_font.render(message, True, BLACK)
                screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, 500))
        
        # Game over message
        if game_over:
            game_over_text = title_font.render("Game Over", True, RED if player.health <= 0 else GREEN)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 120))
            
            result_text = normal_font.render("Click Reset to play again", True, BLACK)
            screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 160))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()