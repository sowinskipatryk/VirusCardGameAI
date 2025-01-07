from config import GameConfig
from game import VirusGame
from enums import PlayerType


if __name__ == "__main__":
    config = GameConfig()

    config.add_player(PlayerType.RANDOM, "John")
    config.add_player(PlayerType.RANDOM, "George")
    config.add_player(PlayerType.RANDOM, "Amy")
    config.add_player(PlayerType.RANDOM, "Phil")

    game = VirusGame(config)
    game.start()
