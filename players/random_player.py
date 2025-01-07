import random

from enums import CardColor
from players import BasePlayer


class RandomPlayer(BasePlayer):
    def decide_action(self):
        return random.randint(0, 9)

    def decide_opponent(self, opponents):
        return random.choice(opponents)

    def decide_organ_color(self):
        return random.choice(list(CardColor))
