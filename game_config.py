from typing import List

from enums import PlayerType
from players import PlayerFactory


class GameConfig:
    min_players: int = 2
    max_players: int = 6
    hand_size: int = 3
    num_organs_to_win: int = 4

    def __init__(self):
        self.players: List['BasePlayer'] = []

    def add_player(self, player_type: PlayerType, name: str) -> None:
        if len(self.players) >= self.max_players:
            raise ValueError(f"Exceeded max number of players: ({self.max_players})")

        player = PlayerFactory.create_player(player_type, name)
        self.players.append(player)

    def is_valid(self) -> bool:
        return self.min_players <= len(self.players) <= self.max_players
