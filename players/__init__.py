from enums import PlayerType
from game.game_constants import GameConstants
from players.base_player import BasePlayer
from players.human_player import HumanPlayer
from players.random_player import RandomPlayer
from players.neat_ai import ExplorerPlayer
from players.rule_based_ai import RuleBasedAIPlayer

from typing import List


class PlayerFactory:
    def __init__(self):
        self.players: List['BasePlayer'] = []

    @staticmethod
    def create_player(player_type: PlayerType, name: str, **kwargs) -> BasePlayer:
        if player_type == PlayerType.HUMAN:
            return HumanPlayer(name)
        elif player_type == PlayerType.EXPLORER:
            return ExplorerPlayer(name, **kwargs)
        elif player_type == PlayerType.RULE_BASED:
            return RuleBasedAIPlayer(name)
        elif player_type == PlayerType.RANDOM:
            return RandomPlayer(name)
        raise ValueError(f"Unknown player type: {player_type}")

    def add_player(self, player_type: PlayerType, name: str, **kwargs) -> 'Player':
        if len(self.players) >= GameConstants.MAX_PLAYERS:
            raise ValueError(f"Exceeded max number of players: ({GameConstants.MAX_PLAYERS})")

        player = self.create_player(player_type, name, **kwargs)
        self.players.append(player)
        return player

    def is_valid(self) -> bool:
        return GameConstants.MIN_PLAYERS <= len(self.players) <= GameConstants.MAX_PLAYERS
