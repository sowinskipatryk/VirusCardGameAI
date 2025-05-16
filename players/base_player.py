from abc import ABC, abstractmethod
from typing import List, Tuple

from models.cards import Card, Organ
from enums import Action, CardColor, OrganState
from game.game_state import GameState
from models.move import Move
from interface import presenter


class BasePlayer(ABC):
    def __init__(self, name: str):
        self.name: str = name
        self.hand: List[Card] = []
        self.body: List[Organ] = []
        self.move_history: List[Tuple[Card, bool]] = []

    def __str__(self) -> str:
        return self.name

    def remove_hand_card(self, card):
        assert card in self.hand
        return self.hand.remove(card)

    def get_hand_card_by_id(self, card_id):
        if card_id > len(self.hand):
            raise ValueError
        return self.hand[card_id]

    def get_hand_card_by_name(self, card_name):
        return next((card for card in self.hand if card.name == card_name), None)

    def get_hand_card_by_type(self, card_type):
        return next((card for card in self.hand if card.type == card_type), None)

    def add_card_to_hand(self, card: Card) -> None:
        if len(self.hand) >= 3:
            raise ValueError
        self.hand.append(card)

    def add_organ_to_body(self, organ: Organ) -> None:
        if organ.color in self.organ_colors:
            raise ValueError
        self.body.append(organ)

    def remove_organ_from_body(self, organ):
        assert organ in self.body
        self.body.remove(organ)

    def get_organ_by_color(self, color):
        return next((organ for organ in self.body if organ.color == color), None)

    def get_infected_organs(self):
        return [organ for organ in self.body if organ.state == OrganState.INFECTED]

    def draw_card(self, deck):
        card = deck.draw_card()
        assert card is not None
        self.add_card_to_hand(card)

    @property
    def organ_colors(self):
        return [organ.color for organ in self.body]

    def discard_card(self, game_state, card_id):
        card = self.get_hand_card_by_id(card_id)
        game_state.add_card_to_discard_pile(card)
        self.hand.remove(card)

    def play_card(self, game_state, card, moves):
        if not card or not moves:
            return

        num_successful_moves = 0
        for move in moves:
            is_error = card.play(game_state, self, move)
            if not is_error:
                num_successful_moves += 1
            self.move_history.append((card.name, is_error))
        if num_successful_moves:
            self.remove_hand_card(card)
            presenter.print_card_play_status_success()
        else:
            presenter.print_card_play_status_fail()
        return num_successful_moves

    def take_turn(self, game_state) -> bool:
        action = self.decide_action(game_state)
        assert action is not None
        presenter.print_decision(action.name)
        if action == Action.PLAY:
            card, moves = self.prepare_moves(game_state)
            presenter.print_card(card)
            num_successful_moves = self.play_card(game_state, card, moves)
            if not num_successful_moves:
                return True
        elif action == Action.DISCARD:
            card_ids = self.decide_cards_to_discard_indices(game_state)
            if not card_ids:
                return True
            return self.discard_cards(game_state, card_ids)
        else:
            raise ValueError("Unknown action decision")

    def discard_cards(self, game_state, card_ids):
        sorted_ids = sorted(card_ids, reverse=True)
        if not card_ids:
            return True
        for card_id in sorted_ids:
            hand_card = self.get_hand_card_by_id(card_id)
            self.remove_hand_card(hand_card)
            game_state.add_card_to_discard_pile(hand_card)

    @abstractmethod
    def decide_action(self, game_state: GameState) -> Action:
        pass

    @abstractmethod
    def decide_opponent(self, game_state: GameState, card: Card) -> 'BasePlayer':
        pass

    @abstractmethod
    def decide_organ_color(self, game_state: GameState, opponent_body=None) -> CardColor:
        pass

    def decide_card_to_play_index(self, game_state: GameState) -> int:
        pass

    @abstractmethod
    def decide_cards_to_discard_indices(self, game_state: GameState) -> List[int]:
        pass

    def prepare_moves(self, game_state) -> tuple[Card, Move] | tuple[Card, list[Move]]:
        card_id = self.decide_card_to_play_index(game_state)
        card = self.get_hand_card_by_id(card_id)
        moves_to_play = card.prepare_moves(self, game_state)
        return card, moves_to_play

    @property
    def num_failed_moves(self):
        return sum([1 for _, is_error in self.move_history if is_error])

    @property
    def num_successful_moves(self):
        return sum([1 for _, is_error in self.move_history if not is_error])

    def get_immunised_organs_num(self):
        return len([1 for organ in self.body if len(organ.medicines) == 2])

    def get_vaccinated_organs_num(self):
        return len([1 for organ in self.body if len(organ.medicines) == 1])

    def get_infected_organs_num(self):
        return len([1 for organ in self.body if organ.viruses])
