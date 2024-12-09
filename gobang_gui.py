import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

class GobangGameGUI(tk.Canvas):
    def __init__(self, master, game, agent, mode_var, move_log, turn_label, log_file, **kwargs):
        super().__init__(master, **kwargs)
        self.game = game
        self.agent = agent
        self.mode_var = mode_var
        self.move_log = move_log
        self.turn_label = turn_label  # Turn indicator label
        self.board_size = game.board_size
        self.CELL_WIDTH = 40
        self.OFFSET = 30  # Adjusted to make space for labels
        self.config(bg='burlywood')
        self.bind("<Button-1>", self.on_click)
        self.bind("<Motion>", self.on_mouse_move)  # Track mouse movement
        self.pack(side=tk.LEFT)
        self.move_history = []  # Track move history

        # Images for the turn indicator
        self.black_turn_image = ImageTk.PhotoImage(Image.open("black_piece.png").resize((50, 50)))
        self.white_turn_image = ImageTk.PhotoImage(Image.open("white_piece.png").resize((50, 50)))

        # Initialize the turn label
        self.update_turn_label()

        # Load the training log to simulate the moves
        self.training_moves = self.load_training_log(log_file)
        self.current_move_idx = 0  # Start from the first move in the training log

        self.draw_board()

    def load_training_log(self, log_file):
        """Load the training log from file."""
        moves = []
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    # Try to extract episode, player, and move from the line
                    parts = line.strip().split(' - ')
                    if len(parts) == 2:
                        # Extract player and move information
                        episode_info = parts[1].split(' Move: ')
                        if len(episode_info) == 2:
                            player = episode_info[0].strip()
                            move = episode_info[1].strip()
                            moves.append((player, move))
                    else:
                        print(f"Skipping invalid line: {line}")
        except Exception as e:
            print(f"Error loading training log: {e}")
        return moves

    def agent_move(self):
        """AI makes a move based on the current game state."""
        if self.mode_var.get() == "Easy AI":
            self.random_ai_move()  # Easy AI: Random move
        elif self.mode_var.get() == "Hard AI":
            self.hard_ai_move()

        # Check if there's a winner based on the current board state
        winner = self.game.check_winner()
        if winner:
            self.announce_winner(winner)

    def random_ai_move(self):
        """Make a random move for the AI."""
        valid_moves = [(i, j) for i in range(self.board_size) for j in range(self.board_size) if
                       self.game.is_valid_move(i, j)]
        if valid_moves:
            x, y = random.choice(valid_moves)
            self.move_history.append((x, y, self.game.current_player))  # Log the AI's move
            self.game.step((x, y))  # Make the AI's move
            self.log_move(x, y, 'White')  # Log the move
            self.draw_board()  # Redraw the board after the move

    def hard_ai_move(self):
        """Make a move based on the training log (AI move from the log)."""
        if self.current_move_idx < len(self.training_moves):
            player, move = self.training_moves[self.current_move_idx]
            move_x = ord(move[0]) - 65  # Convert column letter to index (A->0, B->1, C->2, ...)
            move_y = int(move[1:]) - 1  # Convert row number to index (1->0, 2->1, 3->2, ...)

            if self.game.is_valid_move(move_x, move_y):
                self.move_history.append(
                    (move_x, move_y, self.game.current_player))  # Log the AI's move
                self.game.step((move_x, move_y))  # Make the AI's move
                self.log_move(move_x, move_y, player)  # Log the move in the move log
                self.draw_board()  # Redraw the board after the move

                # Move to the next step in the log
                self.current_move_idx += 1
            else:
                print(f"Invalid move in log: {move} at index {self.current_move_idx}")

    def update_turn_label(self):
        """Update the turn label based on the current player."""
        if self.game.current_player == 1:  # Player 1 (Black)
            self.turn_label.config(image=self.black_turn_image)
        else:  # Player 2 (White)
            self.turn_label.config(image=self.white_turn_image)

    def draw_board(self):
        """Draw the board grid and alphanumeric labels."""
        self.delete("all")

        # Draw grid lines
        for i in range(self.board_size):
            x = self.OFFSET + i * self.CELL_WIDTH
            y = self.OFFSET + i * self.CELL_WIDTH
            self.create_line(x, self.OFFSET, x,
                             self.OFFSET + (self.board_size - 1) * self.CELL_WIDTH)
            self.create_line(self.OFFSET, y, self.OFFSET + (self.board_size - 1) * self.CELL_WIDTH,
                             y)

        # Draw alphanumeric labels
        for i in range(self.board_size):
            # Column labels (A, B, C, ...)
            letter = chr(65 + i)  # Convert to ASCII: 65 = 'A'
            x = self.OFFSET + i * self.CELL_WIDTH
            self.create_text(x, self.OFFSET - 15, text=letter, font=("Arial", 12, "bold"))

            # Row labels (1, 2, 3, ...)
            number = str(i + 1)
            y = self.OFFSET + i * self.CELL_WIDTH
            self.create_text(self.OFFSET - 15, y, text=number, font=("Arial", 12, "bold"))

        # Draw pieces on the board
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.game.board[row][col] == 1:
                    self.draw_piece(row, col, 'black')
                elif self.game.board[row][col] == 2:
                    self.draw_piece(row, col, 'white')

        # Update the turn label
        self.update_turn_label()

    def draw_piece(self, row, col, color):
        """Draw a piece at the given grid location."""
        x = self.OFFSET + row * self.CELL_WIDTH
        y = self.OFFSET + col * self.CELL_WIDTH
        radius = self.CELL_WIDTH // 2 - 2
        self.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)

    def on_click(self, event):
        """Handle user clicks to place a piece."""
        tolerance = 0.3  # 30% of CELL_WIDTH as the tolerance

        x = (event.x - self.OFFSET) // self.CELL_WIDTH
        y = (event.y - self.OFFSET) // self.CELL_WIDTH

        snapped_x = round((event.x - self.OFFSET) / self.CELL_WIDTH)
        snapped_y = round((event.y - self.OFFSET) / self.CELL_WIDTH)

        if self.game.is_valid_move(snapped_x, snapped_y):
            self.move_history.append((snapped_x, snapped_y, self.game.current_player))  # Log the player's move
            self.game.step((snapped_x, snapped_y))  # Make the move on the game board
            self.log_move(snapped_x, snapped_y, 'Black' if self.game.current_player == 2 else 'White')  # Log move in the move log
            self.draw_board()  # Redraw the board after the move

            # Check for a winner after the player's move
            winner = self.game.check_winner()
            if winner:
                self.announce_winner(winner)
                return  # Exit to prevent AI from making a move

            if self.mode_var.get() != "Human vs. Human" and self.game.current_player == 2:  # If it's the AI's turn
                self.agent_move()  # Let the AI take a move

    def announce_winner(self, winner):
        """Announce the winner and reset the game."""
        winner_name = 'Black' if winner == 1 else 'White'
        messagebox.showinfo("Game Over", f"{winner_name} wins!")  # Display winner message
        self.game.reset()  # Reset the game after a win
        self.draw_board()  # Redraw the board

    def log_move(self, x, y, player):
        """Log the move in alphanumeric format (e.g., B5)."""
        column_letter = chr(65 + x)  # Convert column index to letter (A, B, C, ...)
        row_number = y + 1  # Convert row index to number (1, 2, 3, ...)
        move_text = f"{player}: {column_letter}{row_number}\n"
        self.move_log.insert(tk.END, move_text)
        self.move_log.see(tk.END)  # Scroll to the latest move
        self.update_turn_label()

    def on_mouse_move(self, event):
        """Track the mouse position and show a piece contour during movement."""
        x = (event.x - self.OFFSET) // self.CELL_WIDTH
        y = (event.y - self.OFFSET) // self.CELL_WIDTH

        # Calculate the position to "snap" to the grid (ensure it's aligned with the grid intersections)
        snapped_x = round((event.x - self.OFFSET) / self.CELL_WIDTH)
        snapped_y = round((event.y - self.OFFSET) / self.CELL_WIDTH)

        # If the position is valid, show a preview of the piece contour
        if self.game.is_valid_move(snapped_x, snapped_y):
            self.preview_x = snapped_x
            self.preview_y = snapped_y
            self.draw_board()  # Redraw the board to remove the old preview
            self.draw_preview_piece(self.preview_x, self.preview_y)  # Draw the piece contour

    def draw_preview_piece(self, x, y):
        """Draw the contour of the piece at the mouse position, making sure the mouse is centered on it."""
        color = 'black' if self.game.current_player == 1 else 'white'
        radius = self.CELL_WIDTH // 2 - 2
        # Calculate the position for the contour so that it snaps to the grid intersection
        x_pos = self.OFFSET + x * self.CELL_WIDTH
        y_pos = self.OFFSET + y * self.CELL_WIDTH
        self.create_oval(x_pos - radius, y_pos - radius, x_pos + radius, y_pos + radius,
                         outline=color, width=2)



