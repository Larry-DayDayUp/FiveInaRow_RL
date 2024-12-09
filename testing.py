import unittest
from gobang_agent import GobangAgent
from gobang_game import GobangGame
from train_gobang_rl import train_model

class TestGobang(unittest.TestCase):
    def test_agent_initialization(self):
        agent = GobangAgent(board_size=15)
        self.assertTrue(len(list(agent.parameters())) > 0, "Agent should have trainable parameters")

    def test_game_logic(self):
        game = GobangGame(board_size=15)
        self.assertTrue(game.is_valid_move(7, 7))
        game.step((7, 7))
        self.assertFalse(game.is_valid_move(7, 7))
        game.step((8, 8))
        self.assertEqual(game.current_player, 1)

    def test_model_training_loop(self):
        train_model(board_size=15, episodes=1, learning_rate=0.001, save_dir="models/")

if __name__ == "__main__":
    unittest.main()
