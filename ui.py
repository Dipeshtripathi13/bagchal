# ui.py
import sys
import pygame
import random
from env.bagchal_env import BagchalEnv
from agents.dqn_agent import DQNAgent

# Initialize pygame and set up constants
pygame.init()
CELL_SIZE = 100
BOARD_SIZE = 5
WIDTH = HEIGHT = CELL_SIZE * BOARD_SIZE
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bagchal - Tigers and Goats")

# Colors
BG_COLOR = (255, 248, 220)      # cornsilk background
LINE_COLOR = (0, 0, 0)          # black lines
GOAT_COLOR = (139, 69, 19)      # saddlebrown for goats
TIGER_COLOR = (255, 0, 0)       # red for tigers
SELECT_COLOR = (0, 0, 255)      # blue border for selected piece
HIGHLIGHT_COLOR = (50, 205, 50) # lime green for possible moves

# Initialize game environment
env = BagchalEnv()
env.reset()

selected = None
possible_moves = []
game_over = False
winner = None

def draw_board():
    SCREEN.fill(BG_COLOR)
    # Draw grid lines
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(SCREEN, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 2)
        pygame.draw.line(SCREEN, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), 2)
    # Draw pieces
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            cell_value = env.board[x][y]
            center = (y * CELL_SIZE + CELL_SIZE // 2, x * CELL_SIZE + CELL_SIZE // 2)
            if cell_value == 1:
                pygame.draw.circle(SCREEN, GOAT_COLOR, center, CELL_SIZE // 3)
            elif cell_value == 2:
                pygame.draw.circle(SCREEN, TIGER_COLOR, center, CELL_SIZE // 3)
    # Highlight selected piece
    if selected:
        sx, sy = selected
        center = (sy * CELL_SIZE + CELL_SIZE // 2, sx * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(SCREEN, SELECT_COLOR, center, CELL_SIZE // 3, 3)
    # Highlight possible moves
    for (mx, my) in possible_moves:
        center = (my * CELL_SIZE + CELL_SIZE // 2, mx * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(SCREEN, HIGHLIGHT_COLOR, center, CELL_SIZE // 6)

def get_adjacent_moves(r, c):
    moves = []
    for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            if env.board[nr][nc] == 0:
                moves.append((nr, nc))
    return moves

def get_capture_moves(r, c):
    moves = []
    for dr, dc in [(2,0), (-2,0), (0,2), (0,-2)]:
        nr, nc = r + dr, c + dc
        mr, mc = r + dr//2, c + dc//2
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            if env.board[mr][mc] == 1 and env.board[nr][nc] == 0:
                moves.append((nr, nc))
    return moves

def get_valid_moves_for_goat(r, c):
    return get_adjacent_moves(r, c)

def get_valid_moves_for_tiger(r, c):
    moves = get_adjacent_moves(r, c)
    moves.extend(get_capture_moves(r, c))
    return moves

def any_tiger_moves():
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if env.board[x][y] == 2:
                if get_adjacent_moves(x, y) or get_capture_moves(x, y):
                    return True
    return False

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx, my = pygame.mouse.get_pos()
            row = my // CELL_SIZE
            col = mx // CELL_SIZE
            if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
                continue
            if env.goat_turn:
                # Goat's turn
                if env.goats_to_place > 0:
                    # Placing phase
                    if env.board[row][col] == 0:
                        pos = row * BOARD_SIZE + col
                        obs, rew, done, _ = env.step((pos, pos))
                        next_player = "Goat" if env.goat_turn else "Tiger"
                        print(f"{next_player}'s turn, Goats left: {env.goats_to_place}, Goats killed: {env.killed_goats}")
                        selected = None
                        possible_moves = []
                        if done:
                            game_over = True
                            winner = 'Tigers'
                        else:
                            if not any_tiger_moves():
                                game_over = True
                                winner = 'Goats'
                else:
                    # Moving goats phase
                    if selected is None:
                        if env.board[row][col] == 1:
                            selected = (row, col)
                            possible_moves = get_adjacent_moves(row, col)
                    else:
                        if (row, col) in possible_moves:
                            from_idx = selected[0] * BOARD_SIZE + selected[1]
                            to_idx = row * BOARD_SIZE + col
                            obs, rew, done, _ = env.step((from_idx, to_idx))
                            next_player = "Goat" if env.goat_turn else "Tiger"
                            print(f"{next_player}'s turn, Goats left: {env.goats_to_place}, Goats killed: {env.killed_goats}")
                            selected = None
                            possible_moves = []
                            if done:
                                game_over = True
                                winner = 'Tigers'
                            else:
                                if not any_tiger_moves():
                                    game_over = True
                                    winner = 'Goats'
                        else:
                            if env.board[row][col] == 1:
                                selected = (row, col)
                                possible_moves = get_adjacent_moves(row, col)
                            else:
                                selected = None
                                possible_moves = []
            else:
                # Tiger's turn
                if selected is None:
                    if env.board[row][col] == 2:
                        selected = (row, col)
                        possible_moves = get_valid_moves_for_tiger(row, col)
                else:
                    if (row, col) in possible_moves:
                        from_idx = selected[0] * BOARD_SIZE + selected[1]
                        to_idx = row * BOARD_SIZE + col
                        obs, rew, done, _ = env.step((from_idx, to_idx))
                        next_player = "Goat" if env.goat_turn else "Tiger"
                        print(f"{next_player}'s turn, Goats left: {env.goats_to_place}, Goats killed: {env.killed_goats}")
                        selected = None
                        possible_moves = []
                        if done:
                            game_over = True
                            winner = 'Tigers'
                    else:
                        if env.board[row][col] == 2:
                            selected = (row, col)
                            possible_moves = get_valid_moves_for_tiger(row, col)
                        else:
                            selected = None
                            possible_moves = []
    # Highlight empty cells during placement phase
    if env.goat_turn and env.goats_to_place > 0:
        possible_moves = []
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if env.board[x][y] == 0:
                    possible_moves.append((x, y))
    # Draw board and pieces
    draw_board()
    if game_over:
        font = pygame.font.SysFont(None, 48)
        if winner == 'Tigers':
            text = font.render("Tigers win!", True, (255, 0, 0))
        else:
            text = font.render("Goats win!", True, (0, 128, 0))
        SCREEN.blit(text, ((WIDTH - text.get_width()) // 2, (HEIGHT - text.get_height()) // 2))
    pygame.display.flip()
    if game_over:
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()
    clock.tick(30)
