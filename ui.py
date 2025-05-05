import sys
import pygame
from env.bagchal_env import BagchalEnv

# Pygame init
pygame.init()
CELL_SIZE = 100
BOARD_SIZE = 5
PADDING = 50
GRID_WIDTH = CELL_SIZE * (BOARD_SIZE - 1) + 2 * PADDING
INFO_WIDTH = 200
WIDTH = GRID_WIDTH + INFO_WIDTH
HEIGHT = GRID_WIDTH
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Baghchal")

# Colors
BG_COLOR = (255, 248, 220)
LINE_COLOR = (0, 0, 0)
GOAT_COLOR = (139, 69, 19)
TIGER_COLOR = (255, 0, 0)
DOT_COLOR = (0, 0, 0)
SELECT_COLOR = (0, 0, 255)
HIGHLIGHT_COLOR = (50, 205, 50)
NUMBER_COLOR = (0, 0, 255)
INFO_BG = (230, 230, 250)
BUTTON_COLOR = (100, 200, 100)
BUTTON_TEXT = (0, 0, 0)

# Font
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)

# Positions
points = [(x * CELL_SIZE + PADDING, y * CELL_SIZE + PADDING)
          for y in range(BOARD_SIZE) for x in range(BOARD_SIZE)]

# Setup
env = BagchalEnv()
selected = None
possible_moves = []
game_over = False
winner = None

def get_index_from_position(pos):
    x, y = pos
    for i, (px, py) in enumerate(points):
        if (x - px) ** 2 + (y - py) ** 2 <= (CELL_SIZE // 3) ** 2:
            return i
    return None

def check_tigers_trapped():
    for idx in range(25):
        if env.board[idx] == 2:
            if env.get_valid_moves(idx):
                return False
    return True

def draw_info_panel():
    pygame.draw.rect(SCREEN, INFO_BG, (GRID_WIDTH, 0, INFO_WIDTH, HEIGHT))
    texts = [
        f"Goats left: {env.goats_to_place}",
        f"Goats killed: {env.killed_goats}",
        f"Turn: {'Goat' if env.goat_turn else 'Tiger'}"
    ]
    for i, line in enumerate(texts):
        text = font.render(line, True, (0, 0, 0))
        SCREEN.blit(text, (GRID_WIDTH + 20, 40 + i * 30))

    if game_over:
        result = f"{winner} win!"
        text = big_font.render(result, True, (200, 0, 0))
        SCREEN.blit(text, (GRID_WIDTH + 20, 150))

        # Draw "Play Again" button
        pygame.draw.rect(SCREEN, BUTTON_COLOR, (GRID_WIDTH + 30, 250, 140, 40))
        btn_text = font.render("Play Again", True, BUTTON_TEXT)
        SCREEN.blit(btn_text, (GRID_WIDTH + 50, 260))

def draw_board():
    SCREEN.fill(BG_COLOR)

    # Horizontal and vertical lines
    for i in range(BOARD_SIZE):
        pygame.draw.line(SCREEN, LINE_COLOR,
                         (PADDING, PADDING + i * CELL_SIZE),
                         (PADDING + CELL_SIZE * (BOARD_SIZE - 1), PADDING + i * CELL_SIZE), 2)
        pygame.draw.line(SCREEN, LINE_COLOR,
                         (PADDING + i * CELL_SIZE, PADDING),
                         (PADDING + i * CELL_SIZE, PADDING + CELL_SIZE * (BOARD_SIZE - 1)), 2)

    # Diagonals
    pygame.draw.line(SCREEN, LINE_COLOR, points[0], points[24], 2)
    pygame.draw.line(SCREEN, LINE_COLOR, points[4], points[20], 2)

    # Diamond
    pygame.draw.line(SCREEN, LINE_COLOR, points[2], points[10], 2)
    pygame.draw.line(SCREEN, LINE_COLOR, points[10], points[22], 2)
    pygame.draw.line(SCREEN, LINE_COLOR, points[22], points[14], 2)
    pygame.draw.line(SCREEN, LINE_COLOR, points[14], points[2], 2)

    # Dots and node numbers
    for i, (x, y) in enumerate(points):
        pygame.draw.circle(SCREEN, DOT_COLOR, (x, y), 4)
        label = font.render(str(i), True, NUMBER_COLOR)
        SCREEN.blit(label, (x + 5, y + 5))

    # Highlight possible moves
    for idx in possible_moves:
        x, y = points[idx]
        pygame.draw.circle(SCREEN, HIGHLIGHT_COLOR, (x, y), CELL_SIZE // 6.5)

    # Draw pieces
    for i, val in enumerate(env.board):
        x, y = points[i]
        if val == 1:
            pygame.draw.circle(SCREEN, GOAT_COLOR, (x, y), CELL_SIZE // 5)
        elif val == 2:
            pygame.draw.circle(SCREEN, TIGER_COLOR, (x, y), CELL_SIZE // 4.5)

    # Highlight selected
    if selected is not None:
        x, y = points[selected]
        pygame.draw.circle(SCREEN, SELECT_COLOR, (x, y), CELL_SIZE // 3 + 4, 3)

    draw_info_panel()

def reset_game():
    global env, selected, possible_moves, game_over, winner
    env = BagchalEnv()
    selected = None
    possible_moves = []
    game_over = False
    winner = None

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if game_over and GRID_WIDTH + 30 <= mx <= GRID_WIDTH + 170 and 250 <= my <= 290:
                reset_game()
                continue

            if game_over:
                continue

            idx = get_index_from_position((mx, my))
            if idx is None or idx >= 25:
                continue

            if env.is_goat_turn():
                if env.goats_to_place > 0:
                    if env.board[idx] == 0:
                        env.step((idx, idx))
                        selected = None
                        possible_moves = []
                else:
                    if selected is None and env.board[idx] == 1:
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
                if selected is None and env.board[idx] == 2:
                    selected = idx
                    possible_moves = env.get_valid_moves(idx)
                elif selected is not None and idx in possible_moves:
                    env.step((selected, idx))
                    selected = None
                    possible_moves = []
                else:
                    selected = None
                    possible_moves = []

            # Check win conditions
            if env.killed_goats >= env.max_kills:
                game_over = True
                winner = "Tigers"
            elif check_tigers_trapped():
                game_over = True
                winner = "Goats"

    draw_board()
    pygame.display.flip()
    clock.tick(30)
