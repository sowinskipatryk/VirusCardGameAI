from abc import ABC, abstractmethod
from typing import List, Tuple

from cards import Card, Organ
from enums import Action, CardColor
from game_state import GameState


class BasePlayer(ABC):
    def __init__(self, name: str):
        self.name: str = name
        self.hand: List[Card] = []
        self.body: List[Organ] = []
        self.move_history: List[Tuple[Card, bool]] = []

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

    def make_move(self, game_state) -> bool:
        opponents = game_state.get_opponents(self)
        action = self.decide_action(game_state)
        print('Decision:', action.name)
        if action == Action.PLAY:
            card_id = self.decide_card_to_play(game_state)
            print('Card id:', card_id)
            if card_id is None:
                return True
            return self.play_card(game_state, card_id)
        elif action == Action.DISCARD:
            card_ids = self.decide_cards_to_discard(game_state)
            return self.discard_cards(game_state, card_ids)
        else:
            raise ValueError("Unknown action decision")

    def play_card(self, game_state, card_id) -> bool:
        try:
            card = self.get_hand_card_by_id(card_id)
        except IndexError:
            return True
        print('Chosen card:', card)
        is_error = card.play(game_state, self)
        if not is_error:
            self.remove_hand_card_by_id(card_id)
        self.move_history.append((card.name, is_error))
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
    def decide_action(self, game_state: GameState) -> Action:
        pass

    @abstractmethod
    def decide_opponent(self, game_state: GameState, card: Card) -> 'BasePlayer':
        pass

    @abstractmethod
    def decide_organ_color(self, game_state: GameState, target_body=None) -> CardColor:
        pass

    @abstractmethod
    def decide_card_to_play(self, game_state: GameState) -> int:
        pass

    @abstractmethod
    def decide_cards_to_discard(self, game_state: GameState) -> List[int]:
        pass
