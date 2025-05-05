import sys
import pygame
from env.bagchal_env import BagchalEnv

# Initialize pygame and constants
pygame.init()
CELL_SIZE = 100
BOARD_SIZE = 5
GRID_SIZE = CELL_SIZE * (BOARD_SIZE - 1)
PADDING = 60
INFO_PANEL_WIDTH = 200

WIDTH = GRID_SIZE + 2 * PADDING + INFO_PANEL_WIDTH
HEIGHT = GRID_SIZE + 2 * PADDING
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
INFO_BG_COLOR = (240, 240, 255)
BUTTON_COLOR = (180, 220, 180)
BUTTON_TEXT_COLOR = (0, 100, 0)

# Node positions (5x5 grid)
points = [(x * CELL_SIZE + PADDING, y * CELL_SIZE + PADDING)
          for y in range(BOARD_SIZE) for x in range(BOARD_SIZE)]

# Initialize game environment
env = BagchalEnv()
font = pygame.font.SysFont(None, 24)
selected = None
possible_moves = []
game_over = False
winner = None

def draw_board():
    SCREEN.fill(BG_COLOR)

    # Draw grid
    for i in range(BOARD_SIZE):
        pygame.draw.line(SCREEN, LINE_COLOR, points[i], points[i + 20], 2)
        pygame.draw.line(SCREEN, LINE_COLOR, points[i * 5], points[i * 5 + 4], 2)

    # Diagonals
    pygame.draw.line(SCREEN, LINE_COLOR, points[0], points[24], 2)
    pygame.draw.line(SCREEN, LINE_COLOR, points[4], points[20], 2)

    # Diamond
    pygame.draw.line(SCREEN, LINE_COLOR, points[2], points[10], 2)
    pygame.draw.line(SCREEN, LINE_COLOR, points[10], points[22], 2)
    pygame.draw.line(SCREEN, LINE_COLOR, points[22], points[14], 2)
    pygame.draw.line(SCREEN, LINE_COLOR, points[14], points[2], 2)

    # Draw dots and node numbers
    for i, (x, y) in enumerate(points):
        pygame.draw.circle(SCREEN, DOT_COLOR, (x, y), 5)
        num_surface = font.render(str(i), True, NUMBER_COLOR)
        SCREEN.blit(num_surface, (x + 8, y + 5))

    # Highlight possible moves
    for idx in possible_moves:
        x, y = points[idx]
        pygame.draw.circle(SCREEN, HIGHLIGHT_COLOR, (x, y), CELL_SIZE // 6)

    # Draw pieces
    for i, value in enumerate(env.get_board()):
        x, y = points[i]
        if value == 1:
            pygame.draw.circle(SCREEN, GOAT_COLOR, (x, y), CELL_SIZE // 4)
        elif value == 2:
            pygame.draw.circle(SCREEN, TIGER_COLOR, (x, y), CELL_SIZE // 4)

    # Highlight selected
    if selected is not None:
        x, y = points[selected]
        pygame.draw.circle(SCREEN, SELECT_COLOR, (x, y), CELL_SIZE // 3, 3)

def draw_info_panel():
    pygame.draw.rect(SCREEN, INFO_BG_COLOR, (GRID_SIZE + 2 * PADDING, 0, INFO_PANEL_WIDTH, HEIGHT))
    info_font = pygame.font.SysFont(None, 28)
    lines = [
        f"Goats left: {env.goats_to_place}",
        f"Goats killed: {env.killed_goats}",
        "",
        f"Turn: {'Goat' if env.is_goat_turn() else 'Tiger'}"
    ]
    for i, line in enumerate(lines):
        text = info_font.render(line, True, (0, 0, 0))
        SCREEN.blit(text, (GRID_SIZE + 2 * PADDING + 10, 50 + i * 40))

def draw_game_over():
    end_font = pygame.font.SysFont(None, 48)
    msg = f"{winner} win!"
    text = end_font.render(msg, True, (255, 0, 0) if winner == "Tigers" else (0, 128, 0))
    SCREEN.blit(text, ((WIDTH - text.get_width()) // 2, HEIGHT // 2 - 40))

    # Draw "Play Again" button
    button_font = pygame.font.SysFont(None, 32)
    button_text = button_font.render("Play Again", True, BUTTON_TEXT_COLOR)
    button_width, button_height = 160, 50
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT // 2 + 10
    pygame.draw.rect(SCREEN, BUTTON_COLOR, (button_x, button_y, button_width, button_height), border_radius=10)
    SCREEN.blit(button_text, (button_x + 25, button_y + 10))

    return pygame.Rect(button_x, button_y, button_width, button_height)

def get_clicked_node(pos):
    x, y = pos
    for i, (px, py) in enumerate(points):
        if (x - px)**2 + (y - py)**2 <= (CELL_SIZE // 3)**2:
            return i
    return None

def check_tigers_trapped():
    for idx in range(25):
        if env.board[idx] == 2:
            if env.get_valid_moves(idx):
                return False
    return True

def reset_game():
    global env, selected, possible_moves, game_over, winner
    env = BagchalEnv()
    selected = None
    possible_moves = []
    game_over = False
    winner = None

# Game loop
clock = pygame.time.Clock()
play_again_button = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over and play_again_button and play_again_button.collidepoint(event.pos):
                reset_game()
                continue

            if not game_over:
                idx = get_clicked_node(event.pos)
                if idx is not None:
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

                # Check win condition
                if env.killed_goats >= env.max_kills:
                    game_over = True
                    winner = "Tigers"
                elif env.goats_to_place == 0 and check_tigers_trapped():
                    game_over = True
                    winner = "Goats"

    draw_board()
    draw_info_panel()

    if game_over:
        play_again_button = draw_game_over()
    else:
        play_again_button = None

    pygame.display.flip()
    clock.tick(30)
