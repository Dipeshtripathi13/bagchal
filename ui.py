import sys
import pygame
from env.bagchal_env import BagchalEnv

# Constants
CELL_SIZE = 100
PADDING = 50
WINDOW_SIZE = CELL_SIZE * 4 + 2 * PADDING
NODE_RADIUS = 10

# Colors
BG_COLOR = (255, 248, 220)
LINE_COLOR = (0, 0, 0)
DOT_COLOR = (0, 0, 0)
GOAT_COLOR = (139, 69, 19)
TIGER_COLOR = (255, 0, 0)
SELECT_COLOR = (0, 0, 255)
HIGHLIGHT_COLOR = (50, 205, 50)
TEXT_COLOR = (0, 0, 255)

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Baghchal")
font = pygame.font.SysFont(None, 24)

env = BagchalEnv()
selected = None
possible_moves = []

# Positions of nodes in the UI, based on the 5x5 logical board
points = [(PADDING + (i % 5) * CELL_SIZE, PADDING + (i // 5) * CELL_SIZE) for i in range(25)]

# Draw board lines (static connections)
def draw_lines():
    for i, neighbors in env.valid_moves_graph.items():
        for j in neighbors:
            if i < j:  # Avoid drawing twice
                pygame.draw.line(screen, LINE_COLOR, points[i], points[j], 2)

# Draw numbered dots and all pieces
def draw_board():
    screen.fill(BG_COLOR)
    draw_lines()

    # Draw nodes and numbers
    for idx, (x, y) in enumerate(points):
        pygame.draw.circle(screen, DOT_COLOR, (x, y), 5)
        text = font.render(str(idx), True, TEXT_COLOR)
        screen.blit(text, (x + 8, y + 8))

    # Draw possible move highlights
    for move in possible_moves:
        x, y = points[move]
        pygame.draw.circle(screen, HIGHLIGHT_COLOR, (x, y), CELL_SIZE // 6)

    # Draw pieces
    for i, val in enumerate(env.board):
        x, y = points[i]
        if val == 1:
            pygame.draw.circle(screen, GOAT_COLOR, (x, y), CELL_SIZE // 4)
        elif val == 2:
            pygame.draw.circle(screen, TIGER_COLOR, (x, y), CELL_SIZE // 4)

    # Draw selected ring
    if selected is not None:
        x, y = points[selected]
        pygame.draw.circle(screen, SELECT_COLOR, (x, y), CELL_SIZE // 3, 3)

def get_clicked_node(pos):
    mx, my = pos
    for i, (x, y) in enumerate(points):
        if (mx - x)**2 + (my - y)**2 <= (CELL_SIZE // 3)**2:
            return i
    return None

clock = pygame.time.Clock()
running = True
while running:
    draw_board()
    pygame.display.flip()
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        if event.type == pygame.MOUSEBUTTONDOWN:
            idx = get_clicked_node(pygame.mouse.get_pos())
            if idx is None:
                continue

            board = env.get_board()
            is_goat_turn = env.is_goat_turn()

            if is_goat_turn:
                if env.goats_to_place > 0:
                    if board[idx] == 0:
                        env.step((idx, idx))
                        selected = None
                        possible_moves = []
                else:
                    if selected is None and board[idx] == 1:
                        selected = idx
                        possible_moves = env.get_valid_moves(idx)
                    elif selected is not None and idx in possible_moves:
                        env.step((selected, idx))
                        selected = None
                        possible_moves = []
                    else:
                        selected = None
                        possible_moves = []
            else:
                if selected is None and board[idx] == 2:
                    selected = idx
                    possible_moves = env.get_valid_moves(idx)
                elif selected is not None and idx in possible_moves:
                    env.step((selected, idx))
                    selected = None
                    possible_moves = []
                else:
                    selected = None
                    possible_moves = []

pygame.quit()
sys.exit()
