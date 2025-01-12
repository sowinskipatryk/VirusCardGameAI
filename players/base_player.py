from abc import ABC, abstractmethod
from typing import List
from collections import defaultdict

from cards import Card, Organ, CardType
from enums import Action


class BasePlayer(ABC):
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.body: List[Organ] = []
        self.cards_tried = defaultdict(int)
        self.cards_used = defaultdict(int)

    def __str__(self) -> str:
        return self.name

    def remove_hand_card_by_id(self, card_id):
        return self.hand.pop(card_id)

    def get_hand_card_by_id(self, card_id):
        return self.hand[card_id]

    def add_card_to_hand(self, card: Card) -> None:
        assert len(self.hand) < 3
        self.hand.append(card)

    def add_card_to_body(self, organ: Organ) -> None:
        assert organ.color not in [organ.color for organ in self.body]
        self.body.append(organ)

    def get_organ_by_color(self, color):
        return next((organ for organ in self.body if organ.color == color), None)

    def draw_card(self, deck):
        card = deck.draw_card()
        self.add_card_to_hand(card)

    def discard_card(self, deck, card_id):
        card = self.get_hand_card_by_id(card_id)
        deck.discard(card)
        self.hand.remove(card)

    def make_move(self, game) -> bool:
        opponents = game.get_opponents()
        action = self.decide_action(opponents)
        print('Decision:', action.name)
        if action == Action.PLAY:
            card_id = self.decide_card_to_play()
            print('Card id:', card_id)
            if not card_id:
                return True
            return self.play_card(game, card_id)
        elif action == Action.DISCARD:
            card_ids = self.decide_cards_to_discard()
            return self.discard_cards(game, card_ids)
        else:
            raise ValueError("Unknown action decision")

    def play_card(self, game, card_id) -> bool:
        try:
            card = self.get_hand_card_by_id(card_id)
        except IndexError:
            return True
        print('Chosen card:', card)
        self.cards_tried[card.name] += 1
        is_error = card.play(game, self)
        if not is_error:
            self.remove_hand_card_by_id(card_id)
            self.cards_used[card.name] += 1
        print(f'Success: {not is_error}')
        return is_error

    def discard_cards(self, game, card_ids):
        sorted_ids = sorted(card_ids, reverse=True)
        for card_id in sorted_ids:
            card = self.remove_hand_card_by_id(card_id)
            if not card:
                return True
            game.deck.discard(card)

    @abstractmethod
    def decide_action(self, opponents):
        pass

    @abstractmethod
    def decide_opponent(self, opponents, card):
        pass

    @abstractmethod
    def decide_organ_color(self, target_body=None):
        pass

    @abstractmethod
    def decide_card_to_play(self) -> int:
        pass

    @abstractmethod
    def decide_cards_to_discard(self) -> List[int]:
        pass
