from enums import PlayerType
from ai_player import AIPlayer
from base_player import BasePlayer
from human_player import HumanPlayer
from random_player import RandomPlayer


class PlayerFactory:
    @staticmethod
    def create_player(player_type: PlayerType, name: str) -> BasePlayer:
        if player_type == PlayerType.HUMAN:
            return HumanPlayer(name)
        elif player_type == PlayerType.AI:
            return AIPlayer(name)
        elif player_type == PlayerType.RANDOM:
            return RandomPlayer(name)
        raise ValueError(f"Unknown player type: {player_type}")
