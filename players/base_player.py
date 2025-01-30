from abc import ABC, abstractmethod
from typing import List, Tuple

from cards import Card, Organ
from enums import Action, CardColor, OrganState, CardType, TreatmentName
from game_state import GameState
from moves import Move


class BasePlayer(ABC):
    def __init__(self, name: str):
        self.name: str = name
        self.hand: List[Card] = []
        self.body: List[Organ] = []
        self.move_history: List[Tuple[Card, bool]] = []

    def __str__(self) -> str:
        return self.name

    def remove_hand_card(self, card):
        return self.hand.remove(card)

    def get_hand_card_by_id(self, card_id):
        return self.hand[card_id]

    def get_hand_card_by_name(self, card_name):
        return next((card for card in self.hand if card.name == card_name), None)

    def get_hand_card_by_type(self, card_type):
        return next((card for card in self.hand if card.type == card_type), None)

    def add_card_to_hand(self, card: Card) -> None:
        assert len(self.hand) < 3
        self.hand.append(card)

    def add_card_to_body(self, organ: Organ) -> None:
        assert organ.color not in [organ.color for organ in self.body]
        self.body.append(organ)

    def get_organ_by_color(self, color):
        return next((organ for organ in self.body if organ.color == color), None)

    def get_organ_colors(self):
        return [organ.color for organ in self.body]

    def add_organ_to_body(self, organ):
        self.body.append(organ)

    def remove_organ_from_body(self, organ):
        self.body.remove(organ)

    def get_infected_organs(self):
        return [organ for organ in self.body if organ.state == OrganState.INFECTED]

    def draw_card(self, deck):
        card = deck.draw_card()
        self.add_card_to_hand(card)

    @property
    def body_organ_colors(self):
        return [organ.color for organ in self.body]

    def discard_card(self, game_state, card_id):
        card = self.get_hand_card_by_id(card_id)
        game_state.add_card_to_discard_pile(card)
        self.hand.remove(card)

    def take_turn(self, game_state) -> bool:
        action = self.decide_action(game_state)
        print('Decision:', action.name)
        if action == Action.PLAY:
            card, moves = self.decide_moves(game_state)
            if not card or not moves:
                return True
            successful_moves = 0
            for move in moves:
                is_error = card.play(game_state, self, move)
                if not is_error:
                    successful_moves += 1
                    self.remove_hand_card(card)
                    self.move_history.append((card.name, is_error))
                    assert len(self.body_organ_colors) == len(set(self.body_organ_colors))
            if successful_moves == 0:
                return True
        elif action == Action.DISCARD:
            card_ids = self.decide_cards_to_discard_indices(game_state)
            if not card_ids:
                return True
            return self.discard_cards(game_state, card_ids)
        else:
            raise ValueError("Unknown action decision")

    def play_card(self, game_state, card) -> bool:
        print('Chosen card:', card)
        is_error = card.play(game_state, self)
        if not is_error:
            self.remove_hand_card(card)
        self.move_history.append((card.name, is_error))
        print(f'Success: {not is_error}')
        return is_error

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

    def decide_moves(self, game_state) -> Tuple[Card, List[Move]]:
        card_id = self.decide_card_to_play_index(game_state)
        card = self.get_hand_card_by_id(card_id)

        moves_to_play = []

        if card.type == CardType.MEDICINE:
            if card.color == CardColor.WILD:
                chosen_color = self.decide_organ_color(game_state)
            else:
                chosen_color = card.color
            chosen_organ = self.get_organ_by_color(chosen_color)
            if chosen_organ:
                moves_to_play.append(Move(player_organ=chosen_organ))

        elif card.type == CardType.VIRUS:
            chosen_opponent = self.decide_opponent(game_state, card)
            if card.color == CardColor.WILD:
                chosen_color = self.decide_organ_color(game_state, opponent_body=chosen_opponent.body)
            else:
                chosen_color = self.get_organ_by_color(card.color)
            chosen_organ = chosen_opponent.get_organ_by_color(chosen_color)
            if chosen_opponent and chosen_organ:
                moves_to_play.append(Move(opponent=chosen_opponent, opponent_organ=chosen_organ))

        elif card.type == CardType.ORGAN:
            moves_to_play.append(Move())

        elif card.name == TreatmentName.LATEX_GLOVE:
            moves_to_play.append(Move())

        elif card.name == TreatmentName.MEDICAL_ERROR:
            chosen_opponent = self.decide_opponent(game_state, card)
            if chosen_opponent:
                moves_to_play.append(Move(opponent=chosen_opponent))

        elif card.name == TreatmentName.ORGAN_THIEF:
            chosen_opponent = self.decide_opponent(game_state, card)
            chosen_color = self.decide_organ_color(game_state, opponent_body=chosen_opponent.body)
            chosen_organ = chosen_opponent.get_organ_by_color(chosen_color)
            if chosen_opponent and chosen_organ and chosen_organ != OrganState.IMMUNISED and chosen_organ.color not in self.body_organ_colors:
                moves_to_play.append(Move(opponent=chosen_opponent, opponent_organ=chosen_organ))

        elif card.name == TreatmentName.TRANSPLANT:
            chosen_opponent = self.decide_opponent(game_state, card)
            chosen_player_color = self.decide_organ_color(game_state)
            chosen_opponent_color = self.decide_organ_color(game_state, opponent_body=chosen_opponent.body)
            chosen_player_organ = self.get_organ_by_color(chosen_player_color)
            chosen_opponent_organ = chosen_opponent.get_organ_by_color(chosen_opponent_color)
            if chosen_opponent and chosen_player_organ and chosen_opponent_organ and chosen_player_organ.state < OrganState.IMMUNISED and chosen_opponent_organ.state < OrganState.IMMUNISED and chosen_opponent_organ not in self.body_organ_colors and chosen_player_organ not in chosen_opponent.body_organ_colors:
                moves_to_play.append(Move(opponent=chosen_opponent, player_organ=chosen_player_organ,
                                  opponent_organ=chosen_opponent_organ))

        elif card.name == TreatmentName.CONTAGION:
            for infected_player_organ in self.body:
                for virus in infected_player_organ.viruses:
                    chosen_opponent = self.decide_opponent(game_state, card)
                    if virus.color == CardColor.WILD:
                        chosen_color = self.decide_organ_color(game_state, opponent_body=chosen_opponent.body)
                    else:
                        chosen_color = virus.color
                    chosen_organ = chosen_opponent.get_organ_by_color(chosen_color)
                    if chosen_opponent and chosen_organ:
                        moves_to_play.append(Move(opponent=chosen_opponent, player_organ=infected_player_organ,
                                                  opponent_organ=chosen_organ))

        return card, moves_to_play
