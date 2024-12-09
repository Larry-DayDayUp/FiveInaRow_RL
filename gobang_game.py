import numpy as np

class GobangGame:
    def __init__(self, board_size=15):
        self.board_size = board_size
        self.reset()

    def reset(self):
        """Reset the game board."""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)  # Use a NumPy array
        self.current_player = 1  # Player 1 starts
        return self.board

    def step(self, action):
        """Take an action and update the game state."""
        x, y = action
        if self.board[x][y] != 0:
            return None, False  # Invalid move
        self.board[x][y] = self.current_player
        done = self.check_winner()
        self.current_player = 3 - self.current_player  # Switch player
        return self.board, done

    def check_winner(self):
        """Check the entire game board for a winner."""
        directions = [(1, 0), (0, 1), (1, 1),
                      (1, -1)]  # Directions: horizontal, vertical, diagonal (both)

        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y] != 0:  # Only check non-empty cells
                    current_player = self.board[x][y]
                    for dx, dy in directions:
                        count = 1
                        for step in range(1, 5):  # Check 4 steps in the direction
                            nx, ny = x + dx * step, y + dy * step
                            if 0 <= nx < self.board_size and 0 <= ny < self.board_size and \
                                    self.board[nx][ny] == current_player:
                                count += 1
                            else:
                                break
                        if count >= 5:  # Found 5 in a row
                            return current_player
        return 0  # No winner

    def is_valid_move(self, x, y):
        """Check if the move is valid (inside the board and unoccupied)."""
        return 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == 0

    def is_full(self):
        """Check if the board is full."""
        return not np.any(self.board == 0)  # This works correctly with NumPy arrays
