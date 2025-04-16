import pygame
import math
from queue import PriorityQueue

# Initialize Pygame and set up the window
pygame.init()
WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Pathfinding Visualization (A*)")

# Define colors
RED = (255, 0, 0)         # Start
GREEN = (0, 255, 0)       # Goal
BLUE = (0, 0, 255)        # Path
# YELLOW removed for open set!
WHITE = (255, 255, 255)   # Unvisited
BLACK = (0, 0, 0)         # Barrier
PURPLE = (128, 0, 128)    # Closed set
GREY = (128, 128, 128)    # Grid lines
ORANGE = (255, 165, 0)    # For start/goal border

# Define grid parameters
ROWS = 15
GAP = WIDTH // ROWS  # size of each cube

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = row * GAP
        self.y = col * GAP
        self.color = WHITE
        self.neighbors = []
        self.prev = None

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == PURPLE

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == RED

    def is_goal(self):
        return self.color == GREEN

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = RED

    def make_closed(self):
        self.color = PURPLE

    def make_barrier(self):
        self.color = BLACK

    def make_goal(self):
        self.color = GREEN

    def make_path(self):
        self.color = BLUE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, GAP, GAP))

    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < ROWS - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # RIGHT
        if self.col < ROWS - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def heuristic(a, b):
    # Using Manhattan distance as the heuristic
    x1, y1 = a
    x2, y2 = b
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def make_grid():
    grid = []
    for i in range(ROWS):
        grid.append([])
        for j in range(ROWS):
            node = Node(i, j)
            grid[i].append(node)
    return grid

def draw_grid(win):
    for i in range(ROWS):
        pygame.draw.line(win, GREY, (0, i * GAP), (WIDTH, i * GAP))
        pygame.draw.line(win, GREY, (i * GAP, 0), (i * GAP, WIDTH))

def draw(win, grid):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win)
    pygame.display.update()

def get_clicked_pos(pos):
    x, y = pos
    row = x // GAP
    col = y // GAP
    return row, col

def a_star(draw, grid, start, goal):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = heuristic(start.get_pos(), goal.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == goal:
            reconstruct_path(came_from, goal, draw)
            goal.make_goal()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1  # assume each step has cost 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor.get_pos(), goal.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    # Removed neighbor.make_open() so it doesn't turn yellow

        draw()

        if current != start:
            current.make_closed()
    return False

def main(win):
    grid = make_grid()

    start = None
    goal = None

    run = True

    while run:
        draw(win, grid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Left mouse button to set start, goal, or barriers
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]
                if not start and node != goal:
                    start = node
                    start.make_start()
                elif not goal and node != start:
                    goal = node
                    goal.make_goal()
                elif node != start and node != goal:
                    node.make_barrier()

            # Right mouse button resets a node
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == goal:
                    goal = None

            if event.type == pygame.KEYDOWN:
                # Press SPACE to run the A* algorithm
                if event.key == pygame.K_SPACE and start and goal:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    a_star(lambda: draw(win, grid), grid, start, goal)

                # Press 'c' to clear the grid
                if event.key == pygame.K_c:
                    start = None
                    goal = None
                    grid = make_grid()

    pygame.quit()

if __name__ == "__main__":
    main(WIN)
