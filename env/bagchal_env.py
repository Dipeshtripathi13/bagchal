# bagchal_env.py
import numpy as np
import gym
from gym import spaces

class BagchalEnv(gym.Env):
    def __init__(self):
        super(BagchalEnv, self).__init__()
        self.size = 5
        self.board = np.zeros((self.size, self.size), dtype=int)

        self.goats_to_place = 20
        self.placed_goats = 0
        self.killed_goats = 0
        self.max_kills = 5

        # Initialize tiger positions at the four corners
        self.tigers = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for x, y in self.tigers:
            self.board[x][y] = 2  # 2 represents tiger

        self.goat_turn = True

        # Observation: 5x5 board flattened
        self.observation_space = spaces.Box(low=0, high=2, shape=(25,), dtype=int)
        # Action: from_pos (0-24), to_pos (0-24)
        self.action_space = spaces.MultiDiscrete([25, 25])

    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.goats_to_place = 20
        self.placed_goats = 0
        self.killed_goats = 0
        self.tigers = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for x, y in self.tigers:
            self.board[x][y] = 2
        self.goat_turn = True
        return self._get_obs()

    def _get_obs(self):
        return self.board.flatten()

    def get_grid(self):
        return self.board

    def _in_bounds(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def _is_valid_capture(self, from_x, from_y, to_x, to_y):
        dx = to_x - from_x
        dy = to_y - from_y
        # Tiger capture must jump exactly two spaces straight
        if abs(dx) == 2 and dy == 0:
            return True
        if dx == 0 and abs(dy) == 2:
            return True
        return False

    def step(self, action):
        from_pos, to_pos = action

        # Convert flat indices to (x, y)
        if isinstance(from_pos, int):
            from_x, from_y = divmod(from_pos, self.size)
        else:
            from_x, from_y = from_pos
        if isinstance(to_pos, int):
            to_x, to_y = divmod(to_pos, self.size)
        else:
            to_x, to_y = to_pos

        reward = -0.01  # small default penalty
        done = False

        # Check move is inside the board
        if not self._in_bounds(to_x, to_y):
            return self._get_obs(), -1, done, {}

        if self.goat_turn:
            # Goat's move or placement
            if self.goats_to_place > 0:
                # Placing a new goat on an empty cell
                if self.board[to_x][to_y] == 0:
                    self.board[to_x][to_y] = 1
                    self.goats_to_place -= 1
                    self.placed_goats += 1
                    reward = 0.1
                else:
                    reward = -1  # invalid placement
            else:
                # Move an existing goat: must move to adjacent empty cell
                if (self.board[from_x][from_y] == 1 and 
                        self.board[to_x][to_y] == 0 and 
                        (abs(to_x - from_x) + abs(to_y - from_y) == 1)):
                    self.board[from_x][from_y] = 0
                    self.board[to_x][to_y] = 1
                    reward = 0.1
                else:
                    reward = -1  # invalid goat move
        else:
            # Tiger's move or capture
            dx = to_x - from_x
            dy = to_y - from_y
            # Normal move to adjacent empty
            if (self.board[from_x][from_y] == 2 and 
                    self.board[to_x][to_y] == 0 and 
                    (abs(dx) + abs(dy) == 1)):
                self.board[from_x][from_y] = 0
                self.board[to_x][to_y] = 2
                reward = 0.1
            # Capture move (jump over one goat)
            elif self._is_valid_capture(from_x, from_y, to_x, to_y):
                mid_x = (from_x + to_x) // 2
                mid_y = (from_y + to_y) // 2
                if (self.board[from_x][from_y] == 2 and 
                        self.board[mid_x][mid_y] == 1 and 
                        self.board[to_x][to_y] == 0):
                    self.board[from_x][from_y] = 0
                    self.board[mid_x][mid_y] = 0
                    self.board[to_x][to_y] = 2
                    self.killed_goats += 1
                    reward = 1.0
                    if self.killed_goats >= self.max_kills:
                        done = True  # Tigers win
                else:
                    reward = -1  # invalid capture
            else:
                reward = -1  # invalid tiger move

        # Switch turn
        self.goat_turn = not self.goat_turn
        return self._get_obs(), reward, done, {}

    def render(self, mode="human"):
        symbols = {0: '.', 1: 'G', 2: 'T'}
        print("\n".join(" ".join(symbols[cell] for cell in row) for row in self.board))
        print(f"Goats left to place: {self.goats_to_place}, Goats killed: {self.killed_goats}")
