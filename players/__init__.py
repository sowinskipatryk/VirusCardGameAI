from enums import PlayerType
from players.base_player import BasePlayer
from players.human_player import HumanPlayer
from players.random_player import RandomPlayer
# from players.ai_explorer_player import ExplorerPlayer
from players.ai_rule_based_player import RuleBasedAIPlayer


class PlayerFactory:
    @staticmethod
    def create_player(player_type: PlayerType, name: str) -> BasePlayer:
        if player_type == PlayerType.HUMAN:
            return HumanPlayer(name)
        # elif player_type == PlayerType.EXPLORER:
        #     return ExplorerPlayer(name)
        elif player_type == PlayerType.RULE_BASED:
            return RuleBasedAIPlayer(name)
        elif player_type == PlayerType.RANDOM:
            return RandomPlayer(name)
        raise ValueError(f"Unknown player type: {player_type}")
