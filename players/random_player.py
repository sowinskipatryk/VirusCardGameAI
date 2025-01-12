import random
from typing import List

from enums import CardColor, Action
from players import BasePlayer


class RandomPlayer(BasePlayer):
    def decide_action(self, opponents):
        return random.choice(list(Action))

    def decide_opponent(self, opponents, card):
        return random.choice(opponents)

    def decide_organ_color(self, target_body=None):
        if target_body:
            colors = [organ.color for organ in target_body]
        elif self.body:
            colors = [organ.color for organ in self.body]
        else:
            colors = list(CardColor)
        return random.choice(colors)

    def decide_card_to_play(self) -> int:
        return random.randint(0, len(self.hand) - 1)

    def decide_cards_to_discard(self) -> List[int]:
        num_cards = random.randint(1, len(self.hand))
        return random.sample(range(len(self.hand)), num_cards)
