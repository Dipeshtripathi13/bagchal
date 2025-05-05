import numpy as np
import gym
from gym import spaces

class BagchalEnv(gym.Env):
    def __init__(self):
        super(BagchalEnv, self).__init__()
        self.size = 5
        self.board = np.zeros(25, dtype=int)  # Flattened board (0: empty, 1: goat, 2: tiger)
        self.goats_to_place = 20
        self.killed_goats = 0
        self.max_kills = 5
        self.goat_turn = True  # Goat starts
        self.valid_moves_graph = self.get_valid_moves_graph()

        # Place tigers at corners
        for i in [0, 4, 20, 24]:
            self.board[i] = 2

        self.observation_space = spaces.Box(low=0, high=2, shape=(25,), dtype=int)
        self.action_space = spaces.MultiDiscrete([25, 25])

    def reset(self):
        self.board = np.zeros(25, dtype=int)
        for i in [0, 4, 20, 24]:
            self.board[i] = 2
        self.goats_to_place = 20
        self.killed_goats = 0
        self.goat_turn = True
        return self.board.copy()

    def get_valid_moves_graph(self):
        """Returns the standard movement graph for Bagchal nodes"""
        return {
            0: [1, 5, 6],         1: [0, 2, 6],        2: [1, 3, 6, 7, 8],       3: [2, 4, 8],        4: [3, 8, 9],
            5: [0, 6, 10],        6: [0, 1, 2, 5, 7, 10, 11, 12],                 7: [2, 6, 8, 12],
            8: [2, 3, 4, 7, 9, 12, 13, 14],            9: [4, 8, 14],
            10: [5, 6, 11, 15, 16],   11: [6, 10, 12, 16],   12: [6, 7, 8, 11, 13, 16, 17, 18],
            13: [8, 12, 14, 18],  14: [9, 8, 13, 18, 19],
            15: [10, 16, 20], 16: [10, 11, 12, 15, 17, 20, 21, 22], 17: [12, 16, 18, 22],
            18: [12, 13, 14, 17, 19, 22, 23, 24], 19: [14, 18, 24],
            20: [15, 16, 21],     21: [20, 16, 22],     22: [21, 17, 16, 18, 23],
            23: [22, 18, 24],     24: [19, 18, 23],
        }

    def _get_adjacent_goat_moves(self, idx):
        return [i for i in self.valid_moves_graph[idx] if self.board[i] == 0]

    def _get_tiger_moves_and_captures(self, idx):
        moves = []
        for neighbor in self.valid_moves_graph[idx]:
            # Normal move
            if self.board[neighbor] == 0:
                moves.append((neighbor, None))  # (destination, no capture)

            # Possible capture
            dx = (neighbor % 5) - (idx % 5)
            dy = (neighbor // 5) - (idx // 5)
            dest_x = (neighbor % 5) + dx
            dest_y = (neighbor // 5) + dy
            dest_idx = dest_y * 5 + dest_x if 0 <= dest_x < 5 and 0 <= dest_y < 5 else None

            if dest_idx is not None and dest_idx in self.valid_moves_graph.get(neighbor, []):
                if self.board[neighbor] == 1 and self.board[dest_idx] == 0:
                    moves.append((dest_idx, neighbor))  # (destination, captured goat)
        return moves

    def step(self, action):
        from_idx, to_idx = action
        reward = -0.01
        done = False

        if self.board[to_idx] != 0:
            return self.board.copy(), -1, done, {}

        if self.goat_turn:
            if self.goats_to_place > 0:
                if self.board[to_idx] == 0:
                    self.board[to_idx] = 1
                    self.goats_to_place -= 1
                    reward = 0.1
                else:
                    reward = -1
            else:
                if self.board[from_idx] == 1 and to_idx in self._get_adjacent_goat_moves(from_idx):
                    self.board[from_idx] = 0
                    self.board[to_idx] = 1
                    reward = 0.1
                else:
                    reward = -1
        else:
            if self.board[from_idx] != 2:
                return self.board.copy(), -1, done, {}

            legal_moves = self._get_tiger_moves_and_captures(from_idx)
            for dest, captured in legal_moves:
                if dest == to_idx:
                    self.board[from_idx] = 0
                    self.board[to_idx] = 2
                    if captured is not None:
                        self.board[captured] = 0
                        self.killed_goats += 1
                        reward = 1.0
                        if self.killed_goats >= self.max_kills:
                            done = True
                    break
            else:
                return self.board.copy(), -1, done, {}

        self.goat_turn = not self.goat_turn
        return self.board.copy(), reward, done, {}

    def get_valid_moves(self, idx):
        if self.board[idx] == 1:  # Goat
            return self._get_adjacent_goat_moves(idx)
        elif self.board[idx] == 2:  # Tiger
            return [m[0] for m in self._get_tiger_moves_and_captures(idx)]
        else:
            return []

    def get_board(self):
        return self.board.copy()

    def is_goat_turn(self):
        return self.goat_turn
