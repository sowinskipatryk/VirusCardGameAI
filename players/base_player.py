from abc import ABC, abstractmethod
from typing import List

from cards import Card
from enums import Action


class BasePlayer(ABC):
    @classmethod
    def get_action_map(cls):
        return {
            Action.PLAY_CARD_1: lambda game: cls.play_card(game, 1),
            Action.PLAY_CARD_2: lambda game: cls.play_card(game, 2),
            Action.PLAY_CARD_3: lambda game: cls.play_card(game, 3),
            Action.DISCARD_CARD_1: lambda game: cls.discard_cards(game, [0]),
            Action.DISCARD_CARD_2: lambda game: cls.discard_cards(game, [1]),
            Action.DISCARD_CARD_3: lambda game: cls.discard_cards(game, [2]),
            Action.DISCARD_CARD_12: lambda game: cls.discard_cards(game, [0, 1]),
            Action.DISCARD_CARD_13: lambda game: cls.discard_cards(game, [0, 2]),
            Action.DISCARD_CARD_23: lambda game: cls.discard_cards(game, [1, 2]),
            Action.DISCARD_CARD_123: lambda game: cls.discard_cards(game, [0, 1, 2]),
        }

    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.body: List[Card] = []

    def __str__(self) -> str:
        return self.name

    def get_card_from_hand(self, card_id):
        return self.hand.pop(card_id)

    def add_card_to_hand(self, card: Card) -> None:
        self.hand.append(card)

    def add_card_to_body(self, card: Card) -> None:
        self.body.append(card)

    def make_move(self, game) -> None:
        decision = self.decide_action()
        action = self.get_action_map().get(decision)
        if action:
            action(game)
        else:
            raise ValueError("Unknown action decision")

    @abstractmethod
    def decide_action(self):
        pass

    def play_card(self, game, card_id):
        card = self.get_card_from_hand(card_id)
        is_error = card.play(game, self)
        return is_error

    def discard_cards(self, game, card_ids):
        sorted_ids = sorted(card_ids, reverse=True)
        for card_id in sorted_ids:
            card = self.get_card_from_hand(card_id)
            game.deck.discard_card(card)

    @abstractmethod
    def decide_opponent(self, opponents):
        pass

    @abstractmethod
    def decide_card(self):
        pass

    def get_possible_actions(self):
        possible_actions = []
        if self.hand:
            possible_actions.append(Action.PLAY_CARD)
            possible_actions.append(Action.DISCARD_CARD)

    @abstractmethod
    def decide_organ_color(self):
        pass
