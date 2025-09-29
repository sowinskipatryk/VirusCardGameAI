from game.enums import PlayerType
from game.constants import GameConstants
from game.players.base_player import BasePlayer
from game.players.dqn_player import DQNPlayer
from game.players.mcts_player import MCTSPlayer
from game.players.ismcts_player import ISMCTSPlayer
from game.players.human_player import HumanPlayer
from game.players.random_player import RandomPlayer
from game.players.neat_player import NEATPlayer
from game.players.strategy_based_ai import StrategyBasedAIPlayer
from game.players.rule_based_ai import RuleBasedAIPlayer

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
        PlayerType.DQN_AI: DQNPlayer,
        PlayerType.MCTS_AI: MCTSPlayer,
        PlayerType.ISMCTS_AI: ISMCTSPlayer,
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
