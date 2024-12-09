import torch
import torch.optim as optim
import torch.nn as nn
import numpy as np
import os
from gobang_game import GobangGame  # Game environment class
from gobang_agent import GobangAgent  # Neural network agent class

# Set device to GPU if available, otherwise CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

def train_model(board_size, episodes, learning_rate, save_dir='models/'):
    """Train a Gobang agent for a given board size with logging."""
    game = GobangGame(board_size)
    agent = GobangAgent(board_size=board_size).to(device)  # Move model to GPU/CPU
    print("Agent parameters:", list(agent.parameters()))  # Check if model parameters exist

    # Ensure model is in training mode
    agent.train()

    # Check if parameters exist, if not raise an error
    if len(list(agent.parameters())) == 0:
        raise ValueError("Model has no parameters")

    optimizer = optim.Adam(agent.parameters(), lr=learning_rate)  # Initialize optimizer with agent's parameters
    loss_fn = nn.CrossEntropyLoss()

    # Create a subdirectory for this board size
    model_dir = os.path.join(save_dir, f"{board_size}x{board_size}")
    os.makedirs(model_dir, exist_ok=True)

    # Log file path
    log_file = os.path.join(model_dir, 'training_log.txt')

    # Open the log file to save steps
    try:
        with open(log_file, 'w') as f:
            for episode in range(episodes):
                state = game.reset()
                done = False
                total_loss = 0
                print(f"Episode {episode + 1}/{episodes} for {board_size}x{board_size} board...")

                current_player = 1  # Start with Black player

                while not done:
                    state_tensor = torch.FloatTensor(np.array(state)).unsqueeze(0).unsqueeze(0).to(device)
                    action_logits = agent(state_tensor)
                    action_probs = torch.softmax(action_logits, dim=-1)
                    action_dist = torch.distributions.Categorical(action_probs)
                    action = action_dist.sample().item()
                    x, y = divmod(action, board_size)

                    if not game.is_valid_move(x, y):
                        continue  # Skip invalid moves

                    new_state, done = game.step((x, y))
                    reward = 1 if done else 0

                    # Log the move to the file with the episode and current player
                    player = 'Black' if current_player == 1 else 'White'
                    f.write(f"Episode {episode + 1} - {player} Move: {chr(y + 65)}{x + 1}\n")
                    f.flush()  # Ensure that the content is written immediately

                    # Alternate players
                    current_player = 2 if current_player == 1 else 1

                    # Compute loss
                    target = torch.tensor([action], dtype=torch.long).to(device)
                    loss = loss_fn(action_logits, target)
                    total_loss += loss.item()

                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    state = new_state

                print(f"Board Size {board_size} - Episode {episode + 1}/{episodes} - Loss: {total_loss:.4f}")

            # Save the model for this board size
            model_path = os.path.join(model_dir, "model.pth")
            torch.save(agent.state_dict(), model_path)
            print(f"Model for {board_size}x{board_size} board saved at {model_path}")

    except Exception as e:
        print(f"Error writing to file {log_file}: {e}")


# Function to pretrain models for different board sizes
def pretrain_models(min_size, max_size, episodes, learning_rate):
    """Pretrain Gobang models for board sizes from min_size to max_size."""
    for size in range(min_size, max_size + 1):
        print(f"Training model for {size}x{size} board...")
        train_model(size, episodes, learning_rate)

if __name__ == "__main__":
    # Train only 15x15 board and log moves to 'training_log.txt'
    pretrain_models(min_size=15, max_size=15, episodes=1000, learning_rate=0.002)
