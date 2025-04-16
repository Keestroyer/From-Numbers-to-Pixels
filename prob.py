import pygame
import random
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("7 Up 7 Down")
font = pygame.font.SysFont("arial", 36)
big_font = pygame.font.SysFont("arial", 48, bold=True)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SOFT_BLUE = (135, 206, 250)
SOFT_PINK = (255, 182, 193)
BUTTON_COLOR = (255, 255, 255)
BUTTON_BORDER = (100, 100, 100)
BUTTON_HIGHLIGHT = (255, 255, 160)
RESULT_GREEN = (34, 177, 76)
RESULT_RED = (200, 0, 0)

# Load dice images
dice_images = [pygame.image.load(f"dice{i}.png") for i in range(1, 7)]
dice_images = [pygame.transform.scale(img, (64, 64)) for img in dice_images]

# Button class
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.selected = False

    def draw(self, surface):
        color = BUTTON_HIGHLIGHT if self.selected else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, BUTTON_BORDER, self.rect, 2, border_radius=12)
        txt = font.render(self.text, True, BLACK)
        text_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Create buttons
buttons = {
    "7 Down": Button(50, 300, 120, 50, "7 Down"),
    "7": Button(240, 300, 120, 50, "7"),
    "7 Up": Button(430, 300, 120, 50, "7 Up"),
}
roll_button = Button(240, 200, 120, 50, "Roll")

result = ""
player_guess = ""
dice = (0, 0)

# Function to draw gradient background
def draw_background(surface):
    for y in range(HEIGHT):
        r = int(SOFT_BLUE[0] + (SOFT_PINK[0] - SOFT_BLUE[0]) * y / HEIGHT)
        g = int(SOFT_BLUE[1] + (SOFT_PINK[1] - SOFT_BLUE[1]) * y / HEIGHT)
        b = int(SOFT_BLUE[2] + (SOFT_PINK[2] - SOFT_BLUE[2]) * y / HEIGHT)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

# Game loop
running = True
while running:
    draw_background(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for key, btn in buttons.items():
                if btn.is_clicked(pos):
                    player_guess = key
                    result = ""
                    dice = (0, 0)
                    for b in buttons.values():
                        b.selected = False
                    btn.selected = True

            if roll_button.is_clicked(pos) and player_guess:
                die1 = random.randint(1, 6)
                die2 = random.randint(1, 6)
                total = die1 + die2
                dice = (die1, die2)

                if total == 7 and player_guess == "7":
                    result = "You Win!"
                elif total < 7 and player_guess == "7 Down":
                    result = "You Win!"
                elif total > 7 and player_guess == "7 Up":
                    result = "You Win!"
                else:
                    result = "You Lose!"

    # Draw buttons
    for btn in buttons.values():
        btn.draw(screen)
    roll_button.draw(screen)

    # Show title
    title = big_font.render("🎲 7 Up 7 Down 🎲", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Show dice images
    if dice != (0, 0):
        img1 = dice_images[dice[0] - 1]
        img2 = dice_images[dice[1] - 1]
        screen.blit(img1, (WIDTH // 2 - 100, 100))
        screen.blit(img2, (WIDTH // 2 + 30, 100))

    # Show result with drop shadow
    if result:
        color = RESULT_GREEN if "Win" in result else RESULT_RED
        shadow = font.render(result, True, BLACK)
        res_txt = font.render(result, True, color)
        x = WIDTH // 2 - res_txt.get_width() // 2
        y = 260
        screen.blit(shadow, (x + 2, y + 2))
        screen.blit(res_txt, (x, y))

    pygame.display.flip()

pygame.quit()
sys.exit()
