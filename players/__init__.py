from enums import PlayerType
from game.game_constants import GameConstants
from players.base_player import BasePlayer
from players.human_player import HumanPlayer
from players.random_player import RandomPlayer
from players.neat_player import NEATPlayer
from players.strategy_based_ai import StrategyBasedAIPlayer
from players.rule_based_ai import RuleBasedAIPlayer

from typing import List


class PlayerFactory:
    def __init__(self):
        self.players: List['BasePlayer'] = []

    PLAYER_TYPE_TO_PLAYER_CLASS = {
        PlayerType.HUMAN: HumanPlayer,
        PlayerType.RANDOM: RandomPlayer,
        PlayerType.NEAT_AI: NEATPlayer,
        PlayerType.STRATEGY_BASED_AI: StrategyBasedAIPlayer,
        PlayerType.RULE_BASED_AI: RuleBasedAIPlayer,
    }

    def create_player(self, player_type: PlayerType, name: str, **kwargs) -> BasePlayer:
        try:
            return self.PLAYER_TYPE_TO_PLAYER_CLASS[player_type](name, **kwargs)
        except ValueError:
            raise ValueError(f"Unknown player type: {player_type}")

    def add_player(self, player_type: PlayerType, name: str, **kwargs) -> 'Player':
        if len(self.players) >= GameConstants.MAX_PLAYERS:
            raise ValueError(f"Exceeded max number of players: ({GameConstants.MAX_PLAYERS})")

        player = self.create_player(player_type, name, **kwargs)
        self.players.append(player)
        return player

    def is_valid(self) -> bool:
        return GameConstants.MIN_PLAYERS <= len(self.players) <= GameConstants.MAX_PLAYERS
