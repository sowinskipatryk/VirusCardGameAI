import random

from deck import Deck
from config import GameConfig
from enums import OrganState
from players import BasePlayer


class VirusGame:
    def __init__(self, config: GameConfig):
        if not config.is_valid():
            raise ValueError("The game configuration is invalid!")
        self.players = config.players
        self.num_players = len(self.players)
        self.deck = Deck()
        self.current_player_index = random.randint(0, self.num_players - 1)

    def start(self) -> None:
        winner = None
        while not winner:
            winner = self.play_turn()

    @staticmethod
    def check_win_condition(player: BasePlayer) -> bool:
        healthy_organs = [organ for organ in player.body if organ.state == OrganState.HEALTHY]
        return len(healthy_organs) >= 4

    def play_turn(self) -> bool:
        current_player = self.players[self.current_player_index]
        if len(current_player.hand) == 3:
            is_error = current_player.make_move(self)
            if self.check_win_condition(current_player):
                return True
        self.complete_hand(current_player)
        self.next_player()

    def next_player(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % self.num_players

    def complete_hand(self, player: BasePlayer) -> None:
        amount = 3 - len(player.hand)
        for _ in range(amount):
            drawn_card = self.deck.draw_card()
            player.hand.append(drawn_card)

    def get_opponents(self, player: BasePlayer):
        opponents = [opponent for opponent in self.players if opponent != player]
        return opponents
