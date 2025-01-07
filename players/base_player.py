from abc import ABC, abstractmethod
from typing import List

from cards import Card
from enums import Action


class BasePlayer(ABC):
    @classmethod
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

    def make_move(self, game) -> bool:
        action = self.decide_action()
        if action == Action.PLAY:
            card_id = self.decide_card_to_play()
            if not card_id:
                return True
            return self.play_card(game, card_id)
        elif action == Action.DISCARD:
            card_ids = self.decide_cards_to_discard()
            if not card_ids:
                return True
            return self.discard_cards(game, card_ids)
        else:
            raise ValueError("Unknown action decision")

    @abstractmethod
    def decide_action(self):
        pass

    def play_card(self, game, card_id) -> bool:
        card = self.get_card_from_hand(card_id)
        is_error = card.play(game, self)
        return is_error

    def discard_cards(self, game, card_ids):
        sorted_ids = sorted(card_ids, reverse=True)
        for card_id in sorted_ids:
            card = self.get_card_from_hand(card_id)
            if not card:
                return True
            game.deck.discard(card)

    @abstractmethod
    def decide_opponent(self, opponents):
        pass

    @abstractmethod
    def decide_organ_color(self):
        pass

    @abstractmethod
    def decide_card_to_play(self) -> int:
        pass

    @abstractmethod
    def decide_cards_to_discard(self) -> List[int]:
        pass
