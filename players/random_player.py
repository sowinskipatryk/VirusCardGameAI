import random
from typing import List

from enums import CardColor, Action
from players import BasePlayer


class RandomPlayer(BasePlayer):
    def decide_action(self, game_state) -> Action:
        return random.choice(list(Action))

    def decide_opponent(self, game_state, card) -> BasePlayer:
        opponents = game_state.get_opponents(self)
        return random.choice(opponents)

    def decide_organ_color(self, game_state, opponent_body=None) -> CardColor:
        if opponent_body:
            colors = [organ.color for organ in opponent_body]
        elif self.body:
            colors = [organ.color for organ in self.body]
        else:
            colors = list(CardColor)
        return random.choice(colors)

    def decide_card_to_play_index(self, game_state) -> int:
        return random.randint(0, len(self.hand) - 1)

    def decide_cards_to_discard_indices(self, game_state) -> List[int]:
        num_cards = random.randint(1, len(self.hand))
        return random.sample(range(len(self.hand)), num_cards)
