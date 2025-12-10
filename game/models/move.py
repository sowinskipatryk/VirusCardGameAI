from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from game.players.base_player import BasePlayer
    from game.models.cards import Organ


class Move:
    def __init__(
        self,
        opponent: Optional[BasePlayer] = None,
        player_organ: Optional[Organ] = None,
        opponent_organ: Optional[Organ] = None
    ) -> None:
        self.opponent = opponent
        self.player_organ = player_organ
        self.opponent_organ = opponent_organ

    def __repr__(self) -> str:
        parts = []
        if self.opponent:
            parts.append(f"opponent={self.opponent.name}")
        if self.player_organ:
            parts.append(f"player_organ={self.player_organ.name}")
        if self.opponent_organ:
            parts.append(f"opponent_organ={self.opponent_organ.name}")
        return f"Move({', '.join(parts)})" if parts else "Move()"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Move):
            return NotImplemented
        return (
            self.opponent == other.opponent
            and self.player_organ == other.player_organ
            and self.opponent_organ == other.opponent_organ
        )
