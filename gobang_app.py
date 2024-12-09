import tkinter as tk
from tkinter import messagebox
import torch
from gobang_game import GobangGame
from gobang_agent import GobangAgent
from gobang_gui import GobangGameGUI

class GobangApp(tk.Tk):
    def __init__(self, default_board_size=15):
        super().__init__()
        self.title("Gobang Game")
        self.geometry("900x700")
        self.board_size = default_board_size
        self.mode_var = tk.StringVar(value="Human vs. Human")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize game and agent
        self.game = GobangGame(board_size=self.board_size)
        self.agent = GobangAgent(board_size=self.board_size).to(self.device)

        # Define the path to the training log file
        log_file_path = f"models/{self.board_size}x{self.board_size}/training_log.txt"

        self.create_widgets(log_file_path)

    def create_widgets(self, log_file):
        menu_frame = tk.Frame(self, bg='lightgray', width=250)
        menu_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        self.turn_label = tk.Label(menu_frame, bg='lightgray')
        self.turn_label.pack(pady=10)

        self.move_log = tk.Text(menu_frame, width=30, height=20, bg='white')
        self.move_log.pack(pady=5)

        # Pass the log file path to the GUI class
        self.canvas = GobangGameGUI(self, self.game, self.agent, self.mode_var, self.move_log, self.turn_label, log_file, width=650, height=650)
        self.canvas.pack(side=tk.LEFT, padx=10)

        tk.Label(menu_frame, text="Choose Game Mode", bg='lightgray', font=("Arial", 14)).pack(pady=5)
        modes = [("Human vs. Human", "Human vs. Human"),
                 ("Easy AI", "Easy AI"),
                 ("Hard AI", "Hard AI")]
        for text, value in modes:
            tk.Button(menu_frame, text=text, command=lambda v=value: self.change_mode(v)).pack(pady=5)

        tk.Button(menu_frame, text="Surrender", command=self.give_up).pack(pady=5)

    def load_model(self, model_path):
        """Load a model with safety checks."""
        try:
            checkpoint = torch.load(model_path)
            # Load the state dictionary with strict=False to ignore mismatched layers
            self.agent.load_state_dict(checkpoint, strict=False)
            self.agent.eval()
            print(f"Successfully loaded model: {model_path}")
        except FileNotFoundError:
            print(f"Model not found at {model_path}")
            messagebox.showerror("Error", f"Model not found for {self.board_size}x{self.board_size} board.")
        except RuntimeError as e:
            print(f"Error loading model: {e}")
            messagebox.showerror("Error", f"Model dimensions do not match: {e}")

    def set_board_size(self, board_size):
        """Change the board size dynamically."""
        self.board_size = board_size
        self.game = GobangGame(board_size=self.board_size)
        self.agent = GobangAgent(board_size=self.board_size).to(self.device)  # Reinitialize the agent
        self.load_model(f"models/{board_size}x{board_size}/model.pth")

    def change_mode(self, mode):
        if messagebox.askyesno("Confirm Mode Change", f"Start a new game in {mode} mode?"):
            self.mode_var.set(mode)
            self.canvas.game.reset()
            self.move_log.delete(1.0, tk.END)
            self.canvas.draw_board()

    def give_up(self):
        winner = "White" if self.canvas.game.current_player == 1 else "Black"
        messagebox.showinfo("Game Over", f"{winner} wins!")
        self.canvas.game.reset()
        self.canvas.draw_board()
        self.move_log.delete(1.0, tk.END)

if __name__ == "__main__":
    app = GobangApp()
    app.mainloop()
